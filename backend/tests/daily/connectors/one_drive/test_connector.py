import pytest
from unittest.mock import patch
from onyx.connectors.one_drive.connector import OneDriveConnector
from onyx.connectors.models import Document, ConnectorMissingCredentialError

from tests.daily.connectors.one_drive.consts_and_utils import (
    TEST_CREDENTIALS,
    TEST_FILE_ID,
    TEST_FOLDER_ID,
    TEST_SHARED_FILE_ID,
)
from .mock_data import (
    MOCK_FILE,
    MOCK_FILES_RESPONSE,
    MOCK_SHARED_FILES_RESPONSE,
    MOCK_FILE_CONTENT,
)


def test_connector_validation(mock_api_client):
    connector = OneDriveConnector()
    
    with pytest.raises(ConnectorMissingCredentialError):
        connector.validate_connector_settings()
    
    connector.client = mock_api_client
    mock_api_client.get.return_value = {"id": "test_user"}
    connector.validate()


@patch("onyx.connectors.one_drive.doc_conversion.extract_file_text")
def test_connector_list_documents(mock_extract_text, one_drive_connector: OneDriveConnector, mock_api_client):
    mock_api_client.get.side_effect = [
        MOCK_FILES_RESPONSE,  # For list request
        MOCK_FILE_CONTENT.encode('utf-8')  # For content request
    ]
    mock_extract_text.return_value = MOCK_FILE_CONTENT
    
    docs = list(one_drive_connector.list_documents())
    
    assert len(docs) > 0
    for doc in docs:
        assert isinstance(doc, Document)
        assert doc.source == "onedrive"
        assert len(doc.sections) > 0
        assert doc.sections[0].text == MOCK_FILE_CONTENT


@patch("onyx.connectors.one_drive.doc_conversion.extract_file_text")
def test_connector_list_folder_documents(mock_extract_text, one_drive_connector: OneDriveConnector, mock_api_client):
    mock_api_client.get.side_effect = [
        MOCK_FILES_RESPONSE,  # For list request
        MOCK_FILE_CONTENT.encode('utf-8')  # For content request
    ]
    mock_extract_text.return_value = MOCK_FILE_CONTENT
    
    docs = list(one_drive_connector.list_folder_documents(TEST_FOLDER_ID))
    
    assert len(docs) > 0
    for doc in docs:
        assert isinstance(doc, Document)
        assert doc.source == "onedrive"
        assert len(doc.sections) > 0
        assert doc.sections[0].text == MOCK_FILE_CONTENT


@patch("onyx.connectors.one_drive.doc_conversion.extract_file_text")
def test_connector_get_document(mock_extract_text, one_drive_connector: OneDriveConnector, mock_api_client):
    mock_api_client.get.side_effect = [
        MOCK_FILE,  # For metadata request
        MOCK_FILE_CONTENT.encode('utf-8')  # For content request
    ]
    mock_extract_text.return_value = MOCK_FILE_CONTENT
    
    doc = one_drive_connector.get_document(TEST_FILE_ID)
    
    assert isinstance(doc, Document)
    assert doc.id == MOCK_FILE["id"]
    assert doc.source == "onedrive"
    assert len(doc.sections) > 0
    assert doc.sections[0].text == MOCK_FILE_CONTENT


@patch("onyx.connectors.one_drive.doc_conversion.extract_file_text")
def test_connector_get_shared_document(mock_extract_text, one_drive_connector: OneDriveConnector, mock_api_client):
    shared_file = MOCK_SHARED_FILES_RESPONSE["value"][0]
    mock_api_client.get.side_effect = [
        shared_file,  # For metadata request
        MOCK_FILE_CONTENT.encode('utf-8')  # For content request
    ]
    mock_extract_text.return_value = MOCK_FILE_CONTENT
    
    doc = one_drive_connector.get_document(TEST_SHARED_FILE_ID)
    
    assert isinstance(doc, Document)
    assert doc.id == shared_file["remoteItem"]["id"]
    assert doc.source == "onedrive"
    assert len(doc.sections) > 0
    assert doc.sections[0].text == MOCK_FILE_CONTENT 