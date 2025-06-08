from datetime import datetime, timezone

MOCK_USER = {
    "displayName": "Test User",
    "mail": "test.user@example.com",
    "id": "test_user_id"
}

MOCK_FILE = {
    "id": "test_file_id",
    "name": "test_document.docx",
    "webUrl": "https://example.com/test_document.docx",
    "size": 12345,
    "lastModifiedDateTime": datetime.now(timezone.utc).isoformat(),
    "file": {
        "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    },
    "parentReference": {
        "driveId": "test_drive_id",
        "path": "/drive/root:/Documents"
    },
    "lastModifiedBy": {
        "user": MOCK_USER
    }
}

MOCK_FOLDER = {
    "id": "test_folder_id",
    "name": "Test Folder",
    "webUrl": "https://example.com/test_folder",
    "folder": {},
    "parentReference": {
        "driveId": "test_drive_id",
        "path": "/drive/root:"
    }
}

MOCK_DRIVE = {
    "id": "test_drive_id",
    "name": "Test Drive",
    "driveType": "personal"
}

MOCK_FILES_RESPONSE = {
    "value": [MOCK_FILE],
    "@odata.nextLink": None
}

MOCK_SHARED_FILES_RESPONSE = {
    "value": [{
        **MOCK_FILE,
        "id": "shared_file_id",
        "name": "shared_document.docx",
        "remoteItem": {
            "id": "remote_file_id",
            "parentReference": {
                "driveId": "shared_drive_id"
            }
        }
    }],
    "@odata.nextLink": None
}

MOCK_FILE_CONTENT = "This is mock content for testing purposes."

MOCK_TOKEN_RESPONSE = {
    "access_token": "mock_access_token",
    "refresh_token": "mock_refresh_token",
    "expires_in": 3600
} 