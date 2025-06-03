from client import OneDriveApiClient  # or wherever your client class is

# Replace with a real access token for testing
ACCESS_TOKEN = ""

# test_one_drive_connector.py
import os
from connector import OneDriveConnector  # Update the import path

if __name__ == "__main__":
    # Set your OneDrive access token here

    if not ACCESS_TOKEN:
        raise ValueError("Please set the ONEDRIVE_ACCESS_TOKEN environment variable")

    connector = OneDriveConnector()

    # Load credentials
    connector.load_credentials({
        "access_token": ACCESS_TOKEN,
    })

    # Load documents
    try:
        docs = connector.load_from_state()
        print(f"Fetched {len(docs)} documents!")
        for doc in docs[:5]:  # Print first 5 docs
            print(f"ID: {doc.id}")
            print(f"Name: {doc.semantic_identifier}")
            print(f"Link: {doc.link}")
            print(f"Updated At: {doc.updated_at}")
            print("-" * 50)
    except Exception as e:
        print(f"Error during connector load: {e}")
