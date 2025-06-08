from datetime import datetime, timezone
from typing import Generator
from unittest.mock import patch, MagicMock

import pytest

from onyx.configs.constants import DocumentSource
from onyx.connectors.one_drive.connector import OneDriveConnector
from onyx.connectors.models import Document
from .mock_data import MOCK_FILES_RESPONSE, MOCK_SHARED_FILES_RESPONSE, MOCK_TOKEN_RESPONSE


@pytest.fixture
def mock_api_client():
    with patch("onyx.connectors.one_drive.connector.OneDriveApiClient") as mock:
        client = mock.return_value
        client.list_my_files.return_value = MOCK_FILES_RESPONSE["value"]
        client.list_shared_files.return_value = MOCK_SHARED_FILES_RESPONSE["value"]
        client.refresh_token.return_value = MOCK_TOKEN_RESPONSE
        yield client


@pytest.fixture
def one_drive_connector(mock_api_client) -> OneDriveConnector:
    connector = OneDriveConnector(
        include_my_drives=True,
        include_files_shared_with_me=True,
    )
    
    connector.load_credentials({
        "token": "mock_token",
        "refresh_token": "mock_refresh_token",
    })
    return connector


def test_load_from_state(one_drive_connector: OneDriveConnector, mock_api_client) -> None:
    mock_api_client.get.side_effect = [
        MOCK_FILES_RESPONSE,
        MOCK_SHARED_FILES_RESPONSE
    ]
    
    docs = one_drive_connector.load_from_state()
    assert isinstance(docs, Generator)
    
    doc_list = list(docs)
    assert len(doc_list) > 0
    
    assert mock_api_client.get.call_count >= 1
    
    for doc in doc_list:
        assert isinstance(doc, Document)
        assert doc.source == DocumentSource.ONEDRIVE
        assert doc.id is not None


def test_poll_source(one_drive_connector: OneDriveConnector, mock_api_client) -> None:
    current = datetime.now(timezone.utc)
    one_day_ago = current.timestamp() - (24 * 60 * 60)
    
    mock_api_client.get.return_value = {
        "value": [
            {
                **MOCK_FILES_RESPONSE["value"][0],
                "lastModifiedDateTime": current.isoformat()
            }
        ]
    }
    
    docs = one_drive_connector.poll_source(
        start=one_day_ago,
        end=current.timestamp()
    )
    assert isinstance(docs, Generator)
    
    doc_list = list(docs)
    assert len(doc_list) > 0
    
    assert mock_api_client.get.call_count >= 1
    
    for doc in doc_list:
        assert isinstance(doc, Document)
        assert doc.source == DocumentSource.ONEDRIVE
        assert doc.id is not None 