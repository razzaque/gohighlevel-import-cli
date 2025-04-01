# scripts/test_live_request.py

import logging
from gohighlevel_import_cli.gohighlevel_client import GoHighLevelClient
from gohighlevel_import_cli.models import Task, Note

# Set logging level to DEBUG for verbose output
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# Instantiate the client (not dry run)
client = GoHighLevelClient(dry_run=False)

# Replace this with a real email from your GHL location
test_email = "brian@brandtrellis.com"

# Create a dummy task
dummy_task = Task(
    subject="Test Task from Script",
    due_date="2025-04-01T10:00:00",
    description="This is a test task sent via API v2",
    status="Pending",
    priority="Medium"
)

# Create a dummy note
dummy_note = Note(
    title="Test Note from Script",
    content="This is a test note added via API v2",
    created_time="2025-04-01T09:00:00"
)

def run_test():
    logging.info(f"🔍 Attempting to find contact: {test_email}")
    contact = client.find_contact_by_email(test_email)
    
    if not contact:
        logging.warning(f"❌ Contact not found for email: {test_email}")
        return

    contact_id = contact["id"]
    logging.info(f"✅ Found contact: {contact_id}")

    logging.info("📤 Sending test task...")
    response_task = client.create_task(contact_id, dummy_task)
    logging.info(f"✅ Task response: {response_task}")

    logging.info("📤 Sending test note...")
    response_note = client.create_note(contact_id, dummy_note)
    logging.info(f"✅ Note response: {response_note}")

if __name__ == "__main__":
    run_test()
