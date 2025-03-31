# gohighlevel_import_cli/main.py

import argparse
import logging
from importer import Importer


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("import_log.log"),
            logging.StreamHandler()
        ]
    )


def main():
    setup_logger()

    parser = argparse.ArgumentParser(description="Import tasks and notes from CRM into GoHighLevel.")
    parser.add_argument("--api-key", required=True, help="GoHighLevel API key")
    parser.add_argument("--contacts", required=True, help="Path to Zoho Contacts Excel file")
    parser.add_argument("--tasks", required=True, help="Path to Zoho Tasks Excel file")
    parser.add_argument("--notes", required=True, help="Path to Zoho Notes Excel file")
    parser.add_argument("--live", action="store_true", help="If set, send data to GoHighLevel")
    args = parser.parse_args()

    importer = Importer(
        api_key=args.api_key,
        contacts_path=args.contacts,
        tasks_path=args.tasks,
        notes_path=args.notes,
        dry_run=not args.live
    )
    importer.run()


if __name__ == "__main__":
    main()
