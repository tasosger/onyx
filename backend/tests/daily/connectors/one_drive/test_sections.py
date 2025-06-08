import pytest
from unittest.mock import patch

from onyx.connectors.one_drive.client import OneDriveApiClient
from onyx.connectors.one_drive.section_extraction import (
    extract_sections_from_file,
    extract_sections_from_document,
)
from onyx.connectors.models import Document, TextSection

from .consts_and_utils import TEST_FILE_ID
from .mock_data import MOCK_FILE, MOCK_FILE_CONTENT


@patch("onyx.connectors.one_drive.section_extraction.extract_file_text")
def test_extract_sections_from_file(mock_extract_text, mock_api_client):
    mock_api_client.get.side_effect = [
        MOCK_FILE,  
        MOCK_FILE_CONTENT.encode('utf-8')  
    ]
    mock_extract_text.return_value = MOCK_FILE_CONTENT
    
    sections = extract_sections_from_file(MOCK_FILE, mock_api_client)
    
    assert sections is not None
    assert len(sections) > 0
    assert isinstance(sections[0], TextSection)
    assert sections[0].text == MOCK_FILE_CONTENT
    assert sections[0].link == MOCK_FILE["webUrl"]


@patch("onyx.connectors.one_drive.section_extraction.extract_file_text")
def test_extract_sections_from_document(mock_extract_text, mock_api_client):
    mock_api_client.get.side_effect = [
        MOCK_FILE, 
        MOCK_FILE_CONTENT.encode('utf-8') 
    ]
    mock_extract_text.return_value = MOCK_FILE_CONTENT
    
    doc = Document(
        id=MOCK_FILE["id"],
        sections=[TextSection(text="", link=MOCK_FILE["webUrl"])],
        source="onedrive",
        semantic_identifier=MOCK_FILE["name"],
        metadata={}
    )
    
    sections = extract_sections_from_document(doc, mock_api_client)
    
    assert sections is not None
    assert len(sections) > 0
    assert isinstance(sections[0], TextSection)
    assert sections[0].text == MOCK_FILE_CONTENT
    assert sections[0].link == MOCK_FILE["webUrl"] 