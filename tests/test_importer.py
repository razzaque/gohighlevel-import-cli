# tests/test_importer.py

import unittest
from models import Contact, Task, Note
from gohighlevel_client import GoHighLevelClient

class TestModels(unittest.TestCase):

    def test_create_task(self):
        task = Task("Follow Up", "2025-01-01", "Check-in", "Open", "High")
        self.assertEqual(task.subject, "Follow Up")
        self.assertEqual(task.priority, "High")

    def test_create_note(self):
        note = Note("Discussed terms", "Meeting")
        self.assertEqual(note.title, "Meeting")
        self.assertIn("terms", note.content)

    def test_create_contact(self):
        contact = Contact("test@example.com")
        task = Task("Test Task")
        note = Note("Test Note")
        contact.add_task(task)
        contact.add_note(note)
        self.assertEqual(contact.email, "test@example.com")
        self.assertEqual(len(contact.tasks), 1)
        self.assertEqual(len(contact.notes), 1)

class TestClientDryRun(unittest.TestCase):

    def setUp(self):
        self.client = GoHighLevelClient(api_key="dummy", dry_run=True)

    def test_find_contact_dry(self):
        contact = self.client.find_contact_by_email("someone@example.com")
        self.assertEqual(contact["id"], "mock-someone@example.com")

    def test_create_task_payload(self):
        task = Task("Call back", "2025-01-01", "Follow up", "Pending", "Medium")
        payload = self.client.create_task("mock-id", task)
        self.assertEqual(payload["title"], "Call back")

    def test_create_note_payload(self):
        note = Note("Intro call", "Intro")
        payload = self.client.create_note("mock-id", note)
        self.assertEqual(payload["title"], "Intro")

if __name__ == '__main__':
    unittest.main()
