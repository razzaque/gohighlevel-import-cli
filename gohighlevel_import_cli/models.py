# gohighlevel_import_cli/models.py

from datetime import datetime
import pandas as pd

class Task:
    def __init__(self, subject, due_date=None, description=None, status=None, priority=None, completed=False):
        self.subject = subject
        self.due_date = due_date.isoformat() if isinstance(due_date, pd.Timestamp) else due_date
        self.description = description
        self.status = status
        self.priority = priority
        self.completed = completed

class Note:
    def __init__(self, content, title="Note", created_time=None):
        self.content = content
        self.title = title or "Note"
        self.created_time = created_time.isoformat() if isinstance(created_time, pd.Timestamp) else created_time

class Contact:
    def __init__(self, email, first_name=None, last_name=None, business_name=None,
                 phone=None, additional_phones=None, address=None, source_id=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.business_name = business_name
        self.phone = phone
        self.additional_phones = additional_phones or []
        self.address = address or {}  # dict with street, city, etc.
        self.source_id = source_id
        self.tasks = []
        self.notes = []

    def add_task(self, task):
        self.tasks.append(task)

    def add_note(self, note):
        self.notes.append(note)
