# gohighlevel_import_cli/gohighlevel_client.py

import requests
import logging
import time
import os
from dotenv import load_dotenv
from gohighlevel_import_cli.models import Contact, Task, Note

class GoHighLevelClient:
    def __init__(self, api_key=None, location_id=None, dry_run=True):
        load_dotenv()
        self.dry_run = dry_run
        self.base_url = "https://services.leadconnectorhq.com"
        self.api_version = "2021-07-28"
        self.token = api_key or os.getenv("GHL_PRIVATE_INTEGRATION_TOKEN")
        self.location_id = location_id or os.getenv("GHL_LOCATION_ID")
        self.user_cache = {}  # Cache for user data
        
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

    def resolve_user_id(self, full_name):
        if full_name in self.user_cache:
            return self.user_cache[full_name]

        url = f"{self.base_url}/users/"
        params = {"locationId": self.location_id}
        try:
            result = self._make_request("GET", url, params=params)
            for user in result.get("users", []):
                user_name = f"{user.get('firstName', '').strip()} {user.get('lastName', '').strip()}".strip()
                if user_name.lower() == full_name.lower():
                    user_id = user.get("id")
                    self.user_cache[full_name] = user_id
                    logging.info(f"Matched user '{full_name}' to ID {user_id}")
                    return user_id
            logging.warning(f"No user match found for '{full_name}'")
            self.user_cache[full_name] = None
            return None
        except Exception as e:
            logging.error(f"Error resolving user '{full_name}': {e}")
            return None

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
        contacts = result.get("contacts", [])
        return contacts[0] if contacts else None

    def create_task(self, contact_id, task: Task, completed=False, assigned_to=None):
        payload = {
            "title": task.subject,
            "dueDate": task.due_date,
            "completed": completed,
        }
        if assigned_to:
            payload["assignedTo"] = assigned_to
        if self.dry_run:
            logging.info(f"[DRY RUN] Would create task: {payload}")
            return payload
        else:
            url = f"{self.base_url}/contacts/{contact_id}/tasks"
            response = self._make_request("POST", url, json=payload)
            logging.info(f"Created task: {response}")
            return response

    def create_note(self, contact_id, note: Note, assigned_to=None):
        payload = {
            "body": note.content
        }
        if assigned_to:
            payload["assignedTo"] = assigned_to
        if self.dry_run:
            logging.info(f"[DRY RUN] Would create note: {payload}")
            return payload
        else:
            url = f"{self.base_url}/contacts/{contact_id}/notes"
            response = self._make_request("POST", url, json=payload)
            logging.info(f"Created note: {response}")
            return response

    def create_contact(self, contact: Contact):
        payload = {
            "email": contact.email,
            "firstName": contact.first_name,
            "lastName": contact.last_name,
            "companyName": contact.business_name,
            "phone": contact.phone,
            "additionalPhones": contact.additional_phones,
            "address1": contact.address.get("street"),
            "city": contact.address.get("city"),
            "state": contact.address.get("state"),
            "postalCode": contact.address.get("postalCode"),
            "country": contact.address.get("country"),
        }

        # Remove empty fields
        payload = {k: v for k, v in payload.items() if v}
        logging.info(f"Creating contact: {payload}")

        if self.dry_run:
            logging.info(f"[DRY RUN] Would create contact: {payload}")
            return {"id": f"mock-{contact.email}"}
        else:
            url = f"{self.base_url}/contacts/"
            response = self._make_request("POST", url, json=payload)
            logging.info(f"Created contact: {response}")
            return response
