# gohighlevel_import_cli/gohighlevel_client.py

import requests
import logging
from models import Task, Note

class GoHighLevelClient:
    def __init__(self, api_key, dry_run=True):
        self.api_key = api_key
        self.dry_run = dry_run
        self.base_url = "https://rest.gohighlevel.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def find_contact_by_email(self, email):
        try:
            response = requests.get(f"{self.base_url}/contacts/search", params={"email": email}, headers=self.headers)
            response.raise_for_status()
            contacts = response.json().get("contacts", [])
            if contacts:
                return contacts[0]  # First match
            return None
        except Exception as e:
            logging.error(f"Error finding contact by email {email}: {e}")
            return None

    def create_task(self, contact_id, task: Task):
        payload = {
            "contactId": contact_id,
            "title": task.subject,
            "dueDate": task.due_date,
            "description": task.description,
            "status": task.status,
            "priority": task.priority
        }
        if self.dry_run:
            logging.info(f"[DRY RUN] Task payload: {payload}")
        else:
            try:
                response = requests.post(f"{self.base_url}/tasks/", json=payload, headers=self.headers)
                response.raise_for_status()
                logging.info(f"Task created: {response.json()}")
            except Exception as e:
                logging.error(f"Failed to create task for contact {contact_id}: {e}")

    def create_note(self, contact_id, note: Note):
        payload = {
            "contactId": contact_id,
            "title": note.title,
            "body": note.content,
            "createdTime": note.created_time
        }
        if self.dry_run:
            logging.info(f"[DRY RUN] Note payload: {payload}")
        else:
            try:
                response = requests.post(f"{self.base_url}/notes/", json=payload, headers=self.headers)
                response.raise_for_status()
                logging.info(f"Note created: {response.json()}")
            except Exception as e:
                logging.error(f"Failed to create note for contact {contact_id}: {e}")