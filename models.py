# gohighlevel_import_cli/models.py

from datetime import datetime
import pandas as pd

class Task:
    def __init__(self, subject, due_date=None, description=None, status=None, priority=None):
        self.subject = subject
        self.due_date = due_date.isoformat() if isinstance(due_date, pd.Timestamp) else due_date
        self.description = description
        self.status = status
        self.priority = priority

class Note:
    def __init__(self, content, title="Note", created_time=None):
        self.content = content
        self.title = title or "Note"
        self.created_time = created_time.isoformat() if isinstance(created_time, pd.Timestamp) else created_time

class Contact:
    def __init__(self, email, first_name=None, last_name=None, source_id=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.source_id = source_id
        self.gohighlevel_id = None
        self.tasks = []
        self.notes = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def add_note(self, note: Note):
        self.notes.append(note)