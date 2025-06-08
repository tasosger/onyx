import pytest
from unittest.mock import patch

from onyx.connectors.one_drive.connector import OneDriveConnector
from onyx.connectors.one_drive.file_retrieval import get_file_content
from .mock_data import MOCK_FILE, MOCK_FILE_CONTENT


def test_get_file_content(mock_api_client):
    mock_api_client.get.return_value = MOCK_FILE_CONTENT.encode('utf-8')
    
    content = get_file_content(
        client=mock_api_client,
        file_id=MOCK_FILE["id"],
        drive_id=MOCK_FILE["parentReference"]["driveId"]
    )
    
    mock_api_client.get.assert_called_with(
        f"/me/drive/items/{MOCK_FILE['id']}/content",
        stream=True
    )
    
    assert content == MOCK_FILE_CONTENT.encode('utf-8')


def test_get_file_content_error(mock_api_client):
    error_msg = "Failed to get file"
    mock_api_client.get.side_effect = Exception(error_msg)
    
    with pytest.raises(Exception) as exc_info:
        content = get_file_content(
            client=mock_api_client,
            file_id=MOCK_FILE["id"],
            drive_id=MOCK_FILE["parentReference"]["driveId"]
        )
    
    assert str(exc_info.value) == f"Failed to get file: {error_msg}" 