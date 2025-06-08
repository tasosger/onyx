from typing import Any, Dict, List, Optional, Generator
from datetime import datetime, timezone

from onyx.connectors.interfaces import LoadConnector
from onyx.connectors.models import Document, TextSection, BasicExpertInfo, ConnectorMissingCredentialError
from onyx.configs.constants import DocumentSource
from onyx.file_processing.extract_file_text import extract_file_text

from .client import OneDriveApiClient, OneDriveClientRequestFailedError
from .constants import SCOPE, AUTH_URL, TOKEN_URL
from .doc_conversion import convert_drive_item_to_document, build_slim_document
from .file_retrieval import get_all_files_in_drive
from .errors import (
    OneDriveError,
    OneDriveAuthError,
    OneDriveCredentialsError,
    OneDriveNotFoundError,
    OneDriveRateLimitError,
    OneDriveRequestError,
    OneDriveServerError
)


class OneDriveConnector(LoadConnector):
    def __init__(
        self,
        folder_id: Optional[str] = None,
        include_my_drives: bool = True,
        include_files_shared_with_me: bool = True,
    ) -> None:
        self.folder_id = folder_id
        self.include_my_drives = include_my_drives
        self.include_files_shared_with_me = include_files_shared_with_me
        self.client = None

    def load_credentials(self, credentials: Dict[str, Any]) -> Dict[str, str] | None:
        access_token = credentials.get("access_token") or credentials.get("token")
        client_id = credentials.get("client_id")
        client_secret = credentials.get("client_secret")
        tenant_id = credentials.get("tenant_id")
        refresh_token = credentials.get("refresh_token")

        if not access_token and not refresh_token:
            raise ConnectorMissingCredentialError("Missing access_token/token or refresh_token in credentials")

        self.client = OneDriveApiClient(
            access_token=access_token,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            refresh_token=refresh_token
        )
        return None

    def update_credentials(self, credentials: Dict[str, Any]) -> Dict[str, str] | None:
        return self.load_credentials(credentials)

    def refresh_token(self) -> Dict[str, str]:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")
        self.client._refresh_access_token()
        return {
            "access_token": self.client.access_token,
            "refresh_token": self.client.refresh_token
        }

    def validate_connector_settings(self) -> None:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")
        try:
            self.client.get("/me")
        except OneDriveClientRequestFailedError as e:
            if e.status_code == 401:
                try:
                    self.refresh_token()
                except:
                    raise ConnectorMissingCredentialError("Invalid credentials")
            else:
                raise

    def validate(self) -> None:
        self.validate_connector_settings()

    def _process_drive_item(self, item: Dict[str, Any]) -> Optional[Document]:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")

        if item.get("folder"):
            return None

        return convert_drive_item_to_document(item, self.client)

    def load_from_state(self) -> Generator[Document, None, None]:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")

        try:
            for item in get_all_files_in_drive(self.client, self.folder_id):
                doc = self._process_drive_item(item)
                if doc:
                    yield doc
        except Exception as e:
            raise OneDriveClientRequestFailedError(500, str(e))

    def poll_source(self, start: float, end: float) -> Generator[Document, None, None]:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")

        try:
            endpoint = "/me/drive/root/delta"
            if self.folder_id:
                endpoint = f"/me/drive/items/{self.folder_id}/delta"

            response = self.client.get(endpoint)
            items = response.get("value", [])
            for item in items:
                if item.get("deleted"):
                    continue

                last_modified = item.get("lastModifiedDateTime")
                if last_modified:
                    try:
                        last_modified_ts = datetime.fromisoformat(last_modified.replace('Z', '+00:00')).timestamp()
                        if not (start <= last_modified_ts <= end):
                            continue
                    except:
                        continue

                doc = self._process_drive_item(item)
                if doc:
                    yield doc
        except Exception as e:
            raise OneDriveClientRequestFailedError(500, str(e))

    def list_documents(self) -> Generator[Document, None, None]:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")

        try:
            response = self.client.get("/me/drive/root/children")
            items = response.get("value", [])
            for item in items:
                doc = self._process_drive_item(item)
                if doc:
                    yield doc
        except Exception as e:
            raise OneDriveClientRequestFailedError(500, str(e))

    def list_folder_documents(self, folder_id: str) -> Generator[Document, None, None]:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")

        try:
            response = self.client.get(f"/me/drive/items/{folder_id}/children")
            items = response.get("value", [])
            for item in items:
                doc = self._process_drive_item(item)
                if doc:
                    yield doc
        except Exception as e:
            raise OneDriveClientRequestFailedError(500, str(e))

    def get_document(self, file_id: str) -> Document:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")

        try:
            response = self.client.get(f"/me/drive/items/{file_id}")
            if response.get("folder"):
                raise OneDriveClientRequestFailedError(404, f"Document {file_id} not found or is a folder")
            
            doc = convert_drive_item_to_document(response, self.client)
            if not doc:
                raise OneDriveClientRequestFailedError(404, f"Document {file_id} not found or is a folder")
            return doc
        except Exception as e:
            raise OneDriveClientRequestFailedError(500, str(e))

    def list_documents_slim(self) -> Generator[Document, None, None]:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")

        try:
            response = self.client.get("/me/drive/root/children")
            items = response.get("value", [])
            for item in items:
                if item.get("folder"):
                    continue
                doc = build_slim_document(item)
                yield doc
        except Exception as e:
            raise OneDriveClientRequestFailedError(500, str(e))

    def list_folder_documents_slim(self, folder_id: str) -> Generator[Document, None, None]:
        if not self.client:
            raise ConnectorMissingCredentialError("Client not initialized - call load_credentials first")

        try:
            response = self.client.get(f"/me/drive/items/{folder_id}/children")
            items = response.get("value", [])
            for item in items:
                if item.get("folder"):
                    continue
                doc = build_slim_document(item)
                yield doc
        except Exception as e:
            raise OneDriveClientRequestFailedError(500, str(e))
