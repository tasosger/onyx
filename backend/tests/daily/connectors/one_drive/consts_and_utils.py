import os
from typing import Dict, Any, List

TEST_USER_EMAIL = os.environ.get("ONEDRIVE_TEST_USER_EMAIL", "")

TEST_CREDENTIALS: Dict[str, Any] = {
    "client_id": os.environ.get("ONEDRIVE_CLIENT_ID", ""),
    "client_secret": os.environ.get("ONEDRIVE_CLIENT_SECRET", ""),
    "tenant_id": os.environ.get("ONEDRIVE_TENANT_ID", ""),
    "refresh_token": os.environ.get("ONEDRIVE_REFRESH_TOKEN", ""),
}

TEST_FILE_ID = os.environ.get("ONEDRIVE_TEST_FILE_ID", "")
TEST_FOLDER_ID = os.environ.get("ONEDRIVE_TEST_FOLDER_ID", "")
TEST_SHARED_FILE_ID = os.environ.get("ONEDRIVE_TEST_SHARED_FILE_ID", "")

TEST_USER_FILES: List[str] = os.environ.get("ONEDRIVE_TEST_USER_FILES", "").split(",")
TEST_SHARED_FILES: List[str] = os.environ.get("ONEDRIVE_TEST_SHARED_FILES", "").split(",")
TEST_FOLDER_FILES: List[str] = os.environ.get("ONEDRIVE_TEST_FOLDER_FILES", "").split(",")

TEST_FILE_NAME = "test_document.docx"
TEST_FOLDER_NAME = "Test Folder"
TEST_FILE_CONTENT = "This is a test document for OneDrive integration testing."

TEST_FOLDER_URL = os.environ.get("ONEDRIVE_TEST_FOLDER_URL", "")
TEST_SHARED_URL = os.environ.get("ONEDRIVE_TEST_SHARED_URL", "") 