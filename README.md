# GoHighLevel CRM Importer

A command-line tool to import **Tasks** and **Notes** from another CRM (like Zoho) into GoHighLevel using the public API.

---

## 📦 Features

- Match contacts by **email address**
- Import associated **tasks** and **notes**
- Supports **dry run** (no API calls)
- Full logging and error handling
- Modular and extensible (OOP design)

---

## 📁 Project Structure

```
gohighlevel_import_cli/
├── main.py                 # CLI entry point
├── importer.py             # Orchestration logic
├── models.py               # Data classes: Contact, Task, Note
├── gohighlevel_client.py   # API interface with test/live modes
├── requirements.txt        # Dependencies
├── README.md               # This file
└── import_log.log          # Output log file
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run in Dry Run Mode (Default)
```bash
python main.py \
  --api-key YOUR_API_KEY \
  --contacts "CONTACT_EXPORT.xlsx" \
  --tasks "TASK_EXPORT.xlsx" \
  --notes "NOTES_EXPORT.xlsx" \
```

### 3. Run in Live Mode (Executes API Calls)
```bash
python main.py \
  --api-key YOUR_API_KEY \
  --contacts "CONTACT_EXPORT.xlsx" \
  --tasks "TASK_EXPORT.xlsx" \
  --notes "NOTES_EXPORT.xlsx" \
  --live
```

---

## 🧪 Testing

Tests are located in the `tests/` directory and use `unittest`.

```bash
python -m unittest discover tests
```

---

## 🛠 Requirements
- Python 3.8+
- GoHighLevel API Key
- CRM exports in Excel format (contacts, tasks, notes)

---

## 📝 License
MIT

---

## 📬 Support
For issues, suggestions, or improvements, feel free to open a pull request or GitHub issue.
