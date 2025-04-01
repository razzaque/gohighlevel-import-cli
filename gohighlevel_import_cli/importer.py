# gohighlevel_import_cli/importer.py

import pandas as pd
import time
import os
import logging
from datetime import datetime
from gohighlevel_import_cli.models import Contact, Task, Note
from gohighlevel_import_cli.gohighlevel_client import GoHighLevelClient
from itertools import islice

class Importer:
    def __init__(self, api_key, location_id, contacts_path, tasks_path, notes_path, dry_run=True, limit=None):
        self.batch_size = int(os.getenv("BATCH_SIZE", 20))
        self.batch_delay = int(os.getenv("BATCH_DELAY", 5))
        self.import_log_path = "imported_contacts.log"
        self.already_imported = set()
        self.failed_imports = []
        self.failed_log_path = "failed_imports.csv"
        self.contacts_path = contacts_path
        self.tasks_path = tasks_path
        self.notes_path = notes_path
        self.client = GoHighLevelClient(api_key, location_id, dry_run)
        self.contacts_dict = {}
        self.unmatched_contacts = []
        self.limit = limit

    def log_failure(self, email, record_type, error, payload):
        self.failed_imports.append({
            "Email": email,
            "Type": record_type,
            "Error": str(error),
            "Payload": str(payload)
        })

    def chunked_iterable(self, iterable, size):
        it = iter(iterable)
        while True:
            chunk = list(islice(it, size))
            if not chunk:
                break
            yield chunk
 
    def load_data(self):
        self.contacts_df = pd.read_excel(self.contacts_path)
        self.tasks_df = pd.read_excel(self.tasks_path)
        self.notes_df = pd.read_excel(self.notes_path)

        self.tasks_df = self.tasks_df.merge(
            self.contacts_df[['Record Id', 'Email']],
            left_on='Contact Name.id',
            right_on='Record Id',
            how='left'
        ).dropna(subset=['Email'])

        self.notes_df = self.notes_df.merge(
            self.contacts_df[['Record Id', 'Email']],
            left_on='Parent ID.id',
            right_on='Record Id',
            how='left'
        ).dropna(subset=['Email'])

    def map_to_objects(self):
        for _, row in self.tasks_df.iterrows():
            email = row['Email']
            if email not in self.contacts_dict:
                match = self.contacts_df[self.contacts_df['Email'] == email]
                if not match.empty:
                    row_data = match.iloc[0]
                    additional_phones = [
                        value for key, value in row_data.items()
                        if "phone" in key.lower() and key.lower() != "mobile phone" and pd.notnull(value)
                    ]
                    address = {
                        "street": row_data.get("Mailing Street"),
                        "city": row_data.get("Mailing City"),
                        "state": row_data.get("Mailing State"),
                        "postalCode": row_data.get("Mailing Zip"),
                        "country": row_data.get("Mailing Country")
                    }
                    self.contacts_dict[email] = Contact(
                        email=email,
                        source_id=row_data.get('Record Id'),
                        first_name=row_data.get("First Name"),
                        last_name=row_data.get("Last Name"),
                        business_name=row_data.get("Company"),
                        phone=row_data.get("Mobile Phone"),
                        additional_phones=additional_phones,
                        address=address
                    )

            task = Task(
                subject=row['Subject'],
                due_date=self._validate_date(row['Due Date']),
                description=row.get('Description'),
                status=row.get('Status'),
                priority=row.get('Priority'),
                completed=str(row.get('Status')).strip().lower() == "completed"
            )
            task.owner = row.get("Task Owner")
            self.contacts_dict[email].add_task(task)

        for _, row in self.notes_df.iterrows():
            email = row['Email']
            if email not in self.contacts_dict:
                match = self.contacts_df[self.contacts_df['Email'] == email]
                if not match.empty:
                    row_data = match.iloc[0]
                    additional_phones = [
                        value for key, value in row_data.items()
                        if "phone" in key.lower() and key.lower() != "mobile phone" and pd.notnull(value)
                    ]
                    address = {
                        "street": row_data.get("Mailing Street"),
                        "city": row_data.get("Mailing City"),
                        "state": row_data.get("Mailing State"),
                        "postalCode": row_data.get("Mailing Zip"),
                        "country": row_data.get("Mailing Country")
                    }
                    self.contacts_dict[email] = Contact(
                        email=email,
                        source_id=row_data.get('Record Id'),
                        first_name=row_data.get("First Name"),
                        last_name=row_data.get("Last Name"),
                        business_name=row_data.get("Company"),
                        phone=row_data.get("Mobile Phone"),
                        additional_phones=additional_phones,
                        address=address
                    )

            note = Note(
                title=row.get('Note Title'),
                content=row['Note Content'],
                created_time=row.get('Created Time')
            )
            note.owner = row.get("Note Owner")
            self.contacts_dict[email].add_note(note)

    def _validate_date(self, date_value):
        try:
            if pd.isnull(date_value):
                return None
            if isinstance(date_value, str):
                return pd.to_datetime(date_value).isoformat()
            return date_value.isoformat()
        except Exception as e:
            logging.warning(f"Invalid date format: {date_value} — {e}")
            return None

    def run(self):
        logging.info("Loading data from Excel files...")
        self.load_data()
        logging.info("Mapping tasks and notes to contact objects...")
        self.map_to_objects()

        processed_count = 0

        # Load already-imported emails if log exists
        if os.path.exists(self.import_log_path):
            with open(self.import_log_path, "r") as f:
                self.already_imported = set(line.strip() for line in f if line.strip())

        # Apply contact limit if set
        all_contacts = list(self.contacts_dict.values())
        if self.limit:
            all_contacts = all_contacts[:self.limit]
            logging.info(f"Limiting import to first {self.limit} contacts.")

        for batch in self.chunked_iterable(all_contacts, self.batch_size):
            for contact in batch:
                if contact.email in self.already_imported:
                    logging.info(f"Skipping already imported contact: {contact.email}")
                    continue

                gh_contact = self.client.find_contact_by_email(contact.email)
                if not gh_contact:
                    self.unmatched_contacts.append(contact.email)
                    try:
                        gh_contact = self.client.create_contact(contact)
                        logging.info(f"Created new GoHighLevel contact for {contact.email}")
                    except Exception as e:
                        logging.error(f"Failed to create contact for {contact.email}: {e}")
                        self.log_failure(contact.email, "Contact", e, contact.__dict__)
                        continue
                else:
                    logging.info(f"Found existing GoHighLevel contact for {contact.email}")

                contact.gohighlevel_id = gh_contact['id']

                for task in contact.tasks:
                    try:
                        task_owner_name = task.status  # fallback if Task Owner is not passed (adjust if needed)
                        if hasattr(task, 'owner'):
                            task_owner_name = task.owner
                        assigned_to = self.client.resolve_user_id(task_owner_name) if task_owner_name else None
                        self.client.create_task(contact.gohighlevel_id, task, completed=getattr(task, 'completed', False), assigned_to=assigned_to)
                    except Exception as e:
                        logging.error(f"Failed to create task for {contact.email}: {e}")
                        self.log_failure(contact.email, "Task", e, task.__dict__)

                for note in contact.notes:
                    try:
                        note_owner_name = note.title  # fallback if Note Owner is not passed (adjust if needed)
                        if hasattr(note, 'owner'):
                            note_owner_name = note.owner
                        assigned_to = self.client.resolve_user_id(note_owner_name) if note_owner_name else None
                        self.client.create_note(contact.gohighlevel_id, note, assigned_to=assigned_to)
                    except Exception as e:
                        logging.error(f"Failed to create note for {contact.email}: {e}")
                        self.log_failure(contact.email, "Note", e, note.__dict__)

                with open(self.import_log_path, "a") as f:
                    f.write(contact.email + "\n")

                processed_count += 1

            logging.info(f"Waiting {self.batch_delay} seconds before next batch...")
            time.sleep(self.batch_delay)

        logging.info(f"Processed {processed_count} contacts.")

        if self.unmatched_contacts:
            unmatched_df = pd.DataFrame(self.unmatched_contacts, columns=["Unmatched Emails"])
            unmatched_df.to_csv("unmatched_contacts.csv", index=False)
            logging.info(f"Wrote {len(self.unmatched_contacts)} unmatched emails to unmatched_contacts.csv")

        if self.failed_imports:
            pd.DataFrame(self.failed_imports).to_csv(self.failed_log_path, index=False)
            logging.warning(f"Wrote {len(self.failed_imports)} failed records to {self.failed_log_path}")
