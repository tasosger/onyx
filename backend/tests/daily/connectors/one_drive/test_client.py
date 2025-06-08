import os
import pytest
from unittest.mock import patch, Mock

from onyx.connectors.one_drive.client import OneDriveApiClient
from .mock_data import MOCK_USER, MOCK_FILES_RESPONSE, MOCK_TOKEN_RESPONSE

@patch("onyx.connectors.one_drive.client.requests.post")
@patch("onyx.connectors.one_drive.client.requests.request")
def test_onedrive_client(mock_request, mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = MOCK_TOKEN_RESPONSE

    mock_request.side_effect = [
        Mock(ok=True, json=lambda: MOCK_USER),
        Mock(ok=True, json=lambda: MOCK_FILES_RESPONSE)
    ]

    print("\nInitializing OneDrive client...")
    client = OneDriveApiClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        tenant_id="test_tenant_id",
        refresh_token="test_refresh_token"
    )

    print("\nTesting connection...")
    user_info = client.get("/me")
    print(f"Connected as: {user_info.get('displayName', 'Unknown')} ({user_info.get('mail', 'No email')})")

    print("\nListing files...")
    files = client.get("/me/drive/root/children")
    print(f"Found {len(files.get('value', []))} files in root")
    for file in files.get('value', [])[:3]:
        print(f"- {file.get('name')} ({file.get('id')})")

if __name__ == "__main__":
    test_onedrive_client() 