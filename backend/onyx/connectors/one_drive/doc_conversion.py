from datetime import datetime, timezone
from typing import Optional, TypedDict

from onyx.connectors.models import Document, TextSection, BasicExpertInfo
from onyx.configs.constants import DocumentSource
from onyx.file_processing.extract_file_text import extract_file_text

from .client import OneDriveApiClient
from .models import OneDriveFileType, OneDriveMimeType


class OneDriveFileType(TypedDict):
    id: str
    name: str
    webUrl: str
    size: int
    lastModifiedDateTime: str
    file: dict
    parentReference: dict
    lastModifiedBy: dict


def convert_drive_item_to_document(
    file: OneDriveFileType,
    client: OneDriveApiClient,
) -> Optional[Document]:
    try:
        file_content = client.get(f"/me/drive/items/{file['id']}/content", stream=True)
        file_text = extract_file_text(
            file=file_content,
            file_name=file.get("name", ""),
            break_on_unprocessable=False
        )
    except Exception:
        return None

    last_modified = file.get("lastModifiedDateTime")
    if last_modified:
        try:
            last_modified = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
        except:
            last_modified = datetime.now(timezone.utc)
    else:
        last_modified = datetime.now(timezone.utc)

    owner = file.get("lastModifiedBy", {}).get("user", {})
    owner_info = None
    if owner:
        owner_info = BasicExpertInfo(
            display_name=owner.get("displayName", ""),
            email=owner.get("email", "")
        )

    file_id = file.get("remoteItem", {}).get("id") or file.get("id")

    return Document(
        id=file_id,
        sections=[TextSection(
            text=file_text,
            link=file.get("webUrl", "")
        )],
        source=DocumentSource.ONEDRIVE,
        semantic_identifier=file.get("name", ""),
        doc_updated_at=last_modified,
        primary_owners=[owner_info] if owner_info else [],
        metadata={
            "path": file.get("parentReference", {}).get("path", ""),
            "size": str(file.get("size", 0)),
            "file_type": file.get("file", {}).get("mimeType", "")
        }
    )


def build_slim_document(file: OneDriveFileType) -> Document:
    last_modified = file.get("lastModifiedDateTime")
    if last_modified:
        try:
            last_modified = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
        except:
            last_modified = datetime.now(timezone.utc)
    else:
        last_modified = datetime.now(timezone.utc)

    return Document(
        id=file["id"],
        sections=[],
        source=DocumentSource.ONEDRIVE,
        semantic_identifier=file.get("name", ""),
        doc_updated_at=last_modified,
        metadata={
            "path": file.get("parentReference", {}).get("path", ""),
            "size": str(file.get("size", 0)),
            "file_type": file.get("file", {}).get("mimeType", "")
        }
    ) 