# gohighlevel_import_cli/importer.py

import pandas as pd
import logging
from models import Contact, Task, Note
from gohighlevel_client import GoHighLevelClient

class Importer:
    def __init__(self, api_key, contacts_path, tasks_path, notes_path, dry_run=True):
        self.contacts_path = contacts_path
        self.tasks_path = tasks_path
        self.notes_path = notes_path
        self.client = GoHighLevelClient(api_key, dry_run)
        self.contacts_dict = {}

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
            task = Task(
                subject=row['Subject'],
                due_date=row['Due Date'],
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
            note = Note(
                title=row.get('Note Title'),
                content=row['Note Content'],
                created_time=row.get('Created Time')
            )
            self.contacts_dict[email].add_note(note)

    def run(self):
        logging.info("Loading data from Excel files...")
        self.load_data()
        logging.info("Mapping tasks and notes to contact objects...")
        self.map_to_objects()

        for contact in self.contacts_dict.values():
            gh_contact = self.client.find_contact_by_email(contact.email)
            if not gh_contact:
                logging.warning(f"No match found in GoHighLevel for email: {contact.email}")
                continue

            contact.gohighlevel_id = gh_contact['id']
            for task in contact.tasks:
                self.client.create_task(contact.gohighlevel_id, task)
            for note in contact.notes:
                self.client.create_note(contact.gohighlevel_id, note)