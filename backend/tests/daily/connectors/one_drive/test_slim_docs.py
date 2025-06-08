import pytest
from onyx.connectors.one_drive.client import OneDriveApiClient
from onyx.connectors.one_drive.connector import OneDriveConnector
from onyx.connectors.one_drive.doc_conversion import build_slim_document
from onyx.connectors.models import Document

from .consts_and_utils import TEST_FILE_ID, TEST_FOLDER_ID
from .mock_data import MOCK_FILE, MOCK_FILES_RESPONSE


def test_build_slim_document(mock_api_client):
    doc = build_slim_document(MOCK_FILE)
    
    assert isinstance(doc, Document)
    assert doc.id == MOCK_FILE["id"]
    assert doc.semantic_identifier == MOCK_FILE["name"]
    assert doc.source == "onedrive"
    assert not doc.sections
    assert doc.metadata["size"] == str(MOCK_FILE["size"])
    assert doc.metadata["file_type"] == MOCK_FILE["file"]["mimeType"]


def test_connector_list_documents_slim(one_drive_connector: OneDriveConnector, mock_api_client):
    mock_api_client.get.return_value = MOCK_FILES_RESPONSE
    
    docs = list(one_drive_connector.list_documents_slim())
    
    assert len(docs) > 0
    for doc in docs:
        assert isinstance(doc, Document)
        assert doc.source == "onedrive"
        assert not doc.sections
        assert doc.metadata["size"] == str(MOCK_FILES_RESPONSE["value"][0]["size"])
        assert doc.metadata["file_type"] == MOCK_FILES_RESPONSE["value"][0]["file"]["mimeType"]


def test_connector_list_folder_documents_slim(one_drive_connector: OneDriveConnector, mock_api_client):
    mock_api_client.get.return_value = MOCK_FILES_RESPONSE
    
    docs = list(one_drive_connector.list_folder_documents_slim(TEST_FOLDER_ID))
    
    assert len(docs) > 0
    for doc in docs:
        assert isinstance(doc, Document)
        assert doc.source == "onedrive"
        assert not doc.sections
        assert doc.metadata["size"] == str(MOCK_FILES_RESPONSE["value"][0]["size"])
        assert doc.metadata["file_type"] == MOCK_FILES_RESPONSE["value"][0]["file"]["mimeType"] 