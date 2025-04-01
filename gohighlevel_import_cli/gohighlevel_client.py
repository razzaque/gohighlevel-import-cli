# gohighlevel_import_cli/gohighlevel_client.py

import requests
import logging
import time
import os
from dotenv import load_dotenv
from gohighlevel_import_cli.models import Task, Note

class GoHighLevelClient:
    def __init__(self, api_key=None, location_id=None, dry_run=True):
        load_dotenv()
        self.dry_run = dry_run
        self.base_url = "https://services.leadconnectorhq.com"
        self.api_version = "2021-07-28"
        self.token = api_key or os.getenv("GHL_PRIVATE_INTEGRATION_TOKEN")
        self.location_id = location_id or os.getenv("GHL_LOCATION_ID")

        if not self.token:
            raise ValueError("GHL_PRIVATE_INTEGRATION_TOKEN is not set in the environment variables.")
        if not self.location_id:
            raise ValueError("GHL_LOCATION_ID is not set in the environment variables.")

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Version": self.api_version,
        }

    def _handle_rate_limit(self, response):
        if response.status_code == 429:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 1))
            logging.warning(f"Rate limit exceeded. Waiting {reset_time} seconds before retrying...")
            time.sleep(reset_time)
            return True
        return False

    def _make_request(self, method, url, **kwargs):
        for attempt in range(3):
            try:
                response = requests.request(method, url, headers=self._get_headers(), **kwargs)
                if self._handle_rate_limit(response):
                    continue
                logging.debug(f"Response [{response.status_code}]: {response.text}")
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logging.error(f"Request failed (attempt {attempt + 1}/3): {e}")
                time.sleep(2 ** attempt)
        raise Exception("API request failed after 3 attempts.")

    def find_contact_by_email(self, email):
        url = f"{self.base_url}/contacts/search"
        payload = {
            "locationId": self.location_id,
            "filters": [
                {
                    "field": "email",
                    "operator": "contains",
                    "value": email
                }
            ],
            "page": 1,
            "pageLimit": 1
        }
        logging.debug(f"Sending contact search payload: {payload}")
        result = self._make_request("POST", url, json=payload)
        return result.get("contacts", [None])[0]

    def create_task(self, contact_id, task: Task):
        payload = {
            "title": task.subject,
            "dueDate": task.due_date,
            "completed": False
        }
        if self.dry_run:
            logging.info(f"[DRY RUN] Would create task: {payload}")
            return payload
        else:
            url = f"{self.base_url}/contacts/{contact_id}/tasks"
            return self._make_request("POST", url, json=payload)

    def create_note(self, contact_id, note: Note):
        payload = {
            "body": note.content
        }
        if self.dry_run:
            logging.info(f"[DRY RUN] Would create note: {payload}")
            return payload
        else:
            url = f"{self.base_url}/contacts/{contact_id}/notes"
            return self._make_request("POST", url, json=payload)
