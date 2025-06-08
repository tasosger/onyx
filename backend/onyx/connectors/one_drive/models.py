from enum import Enum
from typing import Any, TypedDict


class OneDriveMimeType(str, Enum):
    WORD_DOC = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    POWERPOINT = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    PDF = "application/pdf"
    TEXT = "text/plain"
    MARKDOWN = "text/markdown"
    HTML = "text/html"
    ONENOTE = "application/onenote"


class OneDriveUser(TypedDict):
    displayName: str
    email: str


class OneDriveFile(TypedDict):
    id: str
    name: str
    webUrl: str
    size: int
    lastModifiedDateTime: str
    file: dict[str, Any]
    parentReference: dict[str, Any]
    lastModifiedBy: dict[str, Any]


OneDriveFileType = OneDriveFile 