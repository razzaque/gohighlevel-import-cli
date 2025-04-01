# GoHighLevel Import CLI – Developer Guide

This script-based tool allows you to import **tasks** and **notes** from Zoho CRM into GoHighLevel using their API v2 (Private Integrations). It intelligently maps the relationship between tasks, notes, and contacts using a combination of Zoho Record IDs and email addresses.

---

## 📂 Input Files

| File            | Purpose                          |
|-----------------|----------------------------------|
| `contacts.xlsx` | Master file of all Zoho contacts |
| `tasks.xlsx`    | Tasks linked to contacts         |
| `notes.xlsx`    | Notes linked to contacts         |

---

## 🔗 Mapping Logic

### Step 1: Match Tasks and Notes to Emails

- **Tasks** contain a `Contact Name.id`
- **Notes** contain a `Parent ID.id`
- These are matched to `Record Id` in the **Contacts file**
- We enrich both `tasks` and `notes` with the corresponding contact **email**

### Step 2: Create Contact Objects

We group all tasks and notes under `Contact` objects by email:

```python
contacts_dict = {
    "jane@example.com": Contact(email, tasks=[...], notes=[...]),
    ...
}
```

### Step 3: Lookup Contacts in GoHighLevel

Each contact’s email is used to find its corresponding GoHighLevel ID via the API:

```json
POST /contacts/search
{
  "locationId": "...",
  "filters": [
    { "field": "email", "operator": "contains", "value": "jane@example.com" }
  ],
  "page": 1,
  "pageLimit": 1
}
```

### Step 4: Create Tasks & Notes in GoHighLevel

If a contact is found:

- Tasks are created via `POST /contacts/{id}/tasks`
- Notes are created via `POST /contacts/{id}/notes`

---

## ✅ Task Completion Logic

If a task's `"Status"` is `"Completed"` (case-insensitive), it is marked as `completed = True`.

---

## 🔐 Environment Variables

Set these in a `.env` file:

```env
GHL_PRIVATE_INTEGRATION_TOKEN=your_api_key
GHL_LOCATION_ID=your_location_id
CONTACTS_PATH=CONTACTS_FROM_ZOHO.xlsx
TASKS_PATH=TASKS_FROM_ZOHO.xlsx
NOTES_PATH=NOTES_FROM_ZOHO.xlsx
PYTHONPATH=.
```

---

## 📤 CLI Usage

```bash
python -m gohighlevel_import_cli.main --live
```

Use `--live` to send data to GoHighLevel. Omit it to run in dry-run mode.

---

## 🧪 Test Script

Use `scripts/test_live_request.py` to test a single contact’s task/note creation with live output.
