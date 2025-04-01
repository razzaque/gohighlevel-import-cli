# gohighlevel_import_cli/importer.py

import pandas as pd
import logging
from datetime import datetime
from gohighlevel_import_cli.models import Contact, Task, Note
from gohighlevel_import_cli.gohighlevel_client import GoHighLevelClient

class Importer:
    def __init__(self, api_key, location_id, contacts_path, tasks_path, notes_path, dry_run=True):
        self.contacts_path = contacts_path
        self.tasks_path = tasks_path
        self.notes_path = notes_path
        self.client = GoHighLevelClient(api_key, location_id, dry_run)
        self.contacts_dict = {}
        self.unmatched_contacts = []

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
                self.contacts_dict[email] = Contact(
                    email=email,
                    source_id=row.get('Contact Name.id')
                )
            due_date = self._validate_date(row['Due Date'])
            task = Task(
                subject=row['Subject'],
                due_date=due_date,
                description=row.get('Description'),
                status=row.get('Status'),
                priority=row.get('Priority')
            )
            self.contacts_dict[email].add_task(task)

        for _, row in self.notes_df.iterrows():
            email = row['Email']
            if email not in self.contacts_dict:
                self.contacts_dict[email] = Contact(
                    email=email,
                    source_id=row.get('Parent ID.id')
                )
            created_time = self._validate_date(row.get('Created Time'))
            note = Note(
                title=row.get('Note Title'),
                content=row['Note Content'],
                created_time=created_time
            )
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

        for contact in self.contacts_dict.values():
            gh_contact = self.client.find_contact_by_email(contact.email)
            if not gh_contact:
                logging.warning(f"No match found in GoHighLevel for email: {contact.email}")
                self.unmatched_contacts.append(contact.email)
                continue

            contact.gohighlevel_id = gh_contact['id']
            for task in contact.tasks:
                self.client.create_task(contact.gohighlevel_id, task)
            for note in contact.notes:
                self.client.create_note(contact.gohighlevel_id, note)

            processed_count += 1

        logging.info(f"✅ Processed {processed_count} contacts.")

        if self.unmatched_contacts:
            unmatched_df = pd.DataFrame(self.unmatched_contacts, columns=["Unmatched Emails"])
            unmatched_df.to_csv("unmatched_contacts.csv", index=False)
            logging.info(f"⚠️ Wrote {len(self.unmatched_contacts)} unmatched emails to unmatched_contacts.csv")