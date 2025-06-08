from typing import Optional, List

from onyx.connectors.models import Document, TextSection
from onyx.file_processing.extract_file_text import extract_file_text

from .client import OneDriveApiClient
from .models import OneDriveFileType


def extract_sections_from_file(
    file: OneDriveFileType,
    client: OneDriveApiClient,
) -> Optional[List[TextSection]]:
    try:
        file_content = client.get(f"/me/drive/items/{file['id']}/content", stream=True)
        file_text = extract_file_text(
            file=file_content,
            file_name=file.get("name", ""),
            break_on_unprocessable=False
        )
    except Exception:
        return None

    return [TextSection(
        text=file_text,
        link=file.get("webUrl", "")
    )]


def extract_sections_from_document(
    document: Document,
    client: OneDriveApiClient,
) -> Optional[List[TextSection]]:
    try:
        file_content = client.get(f"/me/drive/items/{document.id}/content", stream=True)
        file_text = extract_file_text(
            file=file_content,
            file_name=document.semantic_identifier,
            break_on_unprocessable=False
        )
    except Exception:
        return None

    return [TextSection(
        text=file_text,
        link=document.sections[0].link if document.sections else ""
    )] 