import io
from unittest.mock import patch, MagicMock

from onyx.connectors.file.connector import _process_file
from onyx.connectors.models import Document, TextSection

def test_process_pdf_with_pages():
    test_pdf_content = b"%PDF-1.3\n..."
    pdf_file = io.BytesIO(test_pdf_content)
    
    with patch("onyx.connectors.file.connector.extract_text_and_images") as mock_extract:
        mock_extract.return_value = (
            [
                ("Page 1 content", 1),
                ("Page 2 content", 2),
                ("Page 3 content", 3)
            ],
            []          )
        
        metadata = {"link": "http://example.com/test.pdf"}
        
        docs = _process_file(
            file_name="test.pdf",
            file=pdf_file,
            metadata=metadata,
            pdf_pass=None,
            db_session=MagicMock()
        )
        
        assert len(docs) == 1
        doc = docs[0]
        assert len(doc.sections) == 3
        
        assert doc.sections[0].text == "Page 1 content"
        assert doc.sections[0].link == "http://example.com/test.pdf#page=1"
        
        assert doc.sections[1].text == "Page 2 content"
        assert doc.sections[1].link == "http://example.com/test.pdf#page=2"
        
        assert doc.sections[2].text == "Page 3 content"
        assert doc.sections[2].link == "http://example.com/test.pdf#page=3"

def test_process_pdf_without_link():
    test_pdf_content = b"%PDF-1.3\n..."
    pdf_file = io.BytesIO(test_pdf_content)
    
    with patch("onyx.connectors.file.connector.extract_text_and_images") as mock_extract:
        mock_extract.return_value = (
            [("Page 1 content", 1)],
            []
        )
        
        docs = _process_file(
            file_name="test.pdf",
            file=pdf_file,
            metadata={},
            pdf_pass=None,
            db_session=MagicMock()
        )
        
        assert len(docs) == 1
        doc = docs[0]
        assert len(doc.sections) == 1
        
        assert doc.sections[0].text == "Page 1 content"
        assert doc.sections[0].link == "" 