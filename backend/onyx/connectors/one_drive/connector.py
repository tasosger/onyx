from typing import Any, Dict, List, Optional
from onyx.connectors.interfaces import LoadConnector
from onyx.connectors.models import Document
from onyx.configs.constants import DocumentSource

from client import OneDriveApiClient

class OneDriveConnector(LoadConnector):
    def __init__(self, folder_id: Optional[str] = None) -> None:
        
        self.folder_id = folder_id
        self.client: Optional[OneDriveApiClient] = None

    def load_credentials(self, credentials: Dict[str, Any]) -> None:
        
        access_token = credentials.get("access_token")
        if not access_token:
            raise ValueError("Missing access_token in credentials")
        self.client = OneDriveApiClient(access_token=access_token)

    
    def load_from_state(self):
        drive_items = self.client.get("/me/drive/root/children").get("value", [])
        
        documents = []
        for item in drive_items:
            documents.append({
                "id": item["id"],  
                "text": item.get("name", ""), 
                "source": DocumentSource.ONEDRIVE,  
                "metadata": {
                    "name": item.get("name"),
                    "path": item.get("parentReference", {}).get("path", ""),
                    "last_modified": item.get("lastModifiedDateTime"),
                },
                "sections": [],  
            })
        return documents
