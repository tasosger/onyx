import io
from unittest.mock import patch, MagicMock

from onyx.file_processing.extract_file_text import read_pdf_file, extract_text_and_images

def test_read_pdf_file():
    test_pdf_content = b"%PDF-1.3\n..."
    pdf_file = io.BytesIO(test_pdf_content)
    
    with patch("onyx.file_processing.extract_file_text.PdfReader") as mock_pdf_reader:
        mock_pages = []
        for i in range(3):
            mock_page = MagicMock()
            mock_page.extract_text.return_value = f"Page {i+1} content"
            mock_pages.append(mock_page)
        
        mock_pdf_reader.return_value.pages = mock_pages
        mock_pdf_reader.return_value.metadata = {"Title": "Test PDF"}
        mock_pdf_reader.return_value.is_encrypted = False
        
        text_chunks, metadata, images = read_pdf_file(pdf_file)
        
        assert len(text_chunks) == 3
        assert text_chunks[0] == ("Page 1 content", 1)
        assert text_chunks[1] == ("Page 2 content", 2)
        assert text_chunks[2] == ("Page 3 content", 3)
        assert metadata == {"Title": "Test PDF"}
        assert images == []

def test_read_pdf_file_with_images():
    test_pdf_content = b"%PDF-1.3\n..."
    pdf_file = io.BytesIO(test_pdf_content)
    
    with patch("onyx.file_processing.extract_file_text.PdfReader") as mock_pdf_reader, \
         patch("onyx.file_processing.extract_file_text.Image") as mock_image:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page with image"
        mock_page.images = [MagicMock()]
        mock_page.images[0].data = b"fake_image_data"
        mock_page.images[0].name = "test_image"
        
        mock_pdf_reader.return_value.pages = [mock_page]
        mock_pdf_reader.return_value.metadata = {}
        mock_pdf_reader.return_value.is_encrypted = False
        
        mock_image_instance = MagicMock()
        mock_image_instance.format = "PNG"
        mock_image.open.return_value = mock_image_instance
        
        text_chunks, metadata, images = read_pdf_file(pdf_file, extract_images=True)
        
        assert len(text_chunks) == 1
        assert text_chunks[0] == ("Page with image", 1)
        assert len(images) == 1
        assert images[0][1] == "page_1_image_test_image.png"

def test_extract_text_and_images_pdf():
    test_pdf_content = b"%PDF-1.3\n..."
    pdf_file = io.BytesIO(test_pdf_content)
    
    with patch("onyx.file_processing.extract_file_text.read_pdf_file") as mock_read_pdf:
        mock_read_pdf.return_value = (
            [("Page 1 content", 1), ("Page 2 content", 2)],
            {"Title": "Test PDF"},
            []
        )
        
        result, images = extract_text_and_images(pdf_file, "test.pdf")
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == ("Page 1 content", 1)
        assert result[1] == ("Page 2 content", 2)
        assert images == []

def test_extract_text_and_images_non_pdf():
    text_content = "Test content"
    text_file = io.BytesIO(text_content.encode())
    
    with patch("onyx.file_processing.extract_file_text.is_text_file_extension") as mock_is_text:
        mock_is_text.return_value = True
        
        result, images = extract_text_and_images(text_file, "test.txt")
        
        assert isinstance(result, str)
        assert result == text_content
        assert images == [] 