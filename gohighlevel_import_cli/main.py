# gohighlevel_import_cli/main.py

import argparse
import logging
import os
from dotenv import load_dotenv
from gohighlevel_import_cli.importer import Importer



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
    load_dotenv()  # Load environment variables from .env file

    parser = argparse.ArgumentParser(description="Import tasks and notes from CRM into GoHighLevel.")
    parser.add_argument("--api-key", help="GoHighLevel API key")
    parser.add_argument("--location-id", help="GoHighLevel location ID")
    parser.add_argument("--contacts", help="Path to Zoho Contacts Excel file")
    parser.add_argument("--tasks", help="Path to Zoho Tasks Excel file")
    parser.add_argument("--notes", help="Path to Zoho Notes Excel file")
    parser.add_argument("--live", action="store_true", help="If set, send data to GoHighLevel")
    args = parser.parse_args()

    importer = Importer(
        api_key=args.api_key or os.getenv("GHL_PRIVATE_INTEGRATION_TOKEN"),
        location_id=args.location_id or os.getenv("GHL_LOCATION_ID"),
        contacts_path=args.contacts or os.getenv("CONTACTS_PATH"),
        tasks_path=args.tasks or os.getenv("TASKS_PATH"),
        notes_path=args.notes or os.getenv("NOTES_PATH"),
        dry_run=not args.live
    )

    importer.run()


if __name__ == "__main__":
    main()
