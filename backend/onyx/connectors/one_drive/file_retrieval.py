from typing import Any, Dict, Generator, Iterator, Optional

from .client import OneDriveApiClient
from .models import OneDriveFileType


def get_file_content(
    client: OneDriveApiClient,
    file_id: str,
    drive_id: Optional[str] = None
) -> bytes:
    try:
        return client.get(f"/me/drive/items/{file_id}/content", stream=True)
    except Exception as e:
        raise Exception(f"Failed to get file: {str(e)}")


def get_all_files_in_drive(
    client: OneDriveApiClient,
    folder_id: Optional[str] = None
) -> Generator[Dict[str, Any], None, None]:
    endpoint = "/me/drive/root/children"
    if folder_id:
        endpoint = f"/me/drive/items/{folder_id}/children"

    try:
        response = client.get(endpoint)
        items = response.get("value", [])
        for item in items:
            if item.get("folder"):
                continue
            yield item

        next_link = response.get("@odata.nextLink")
        while next_link:
            response = client.get(next_link)
            items = response.get("value", [])
            for item in items:
                if item.get("folder"):
                    continue
                yield item
            next_link = response.get("@odata.nextLink")
    except Exception as e:
        raise Exception(f"Failed to list files: {str(e)}")


def get_folder_children(
    client: OneDriveApiClient,
    folder_id: str,
) -> Iterator[OneDriveFileType]:
    endpoint = f"/me/drive/items/{folder_id}/children"
    while True:
        response = client.get(endpoint)
        items = response.get("value", [])
        for item in items:
            yield item

        next_link = response.get("@odata.nextLink")
        if not next_link:
            break
        endpoint = next_link


def crawl_folders_for_files(
    client: OneDriveApiClient,
    folder_id: Optional[str] = None,
) -> Iterator[OneDriveFileType]:
    endpoint = "/me/drive/root/children"
    if folder_id:
        endpoint = f"/me/drive/items/{folder_id}/children"

    folders_to_process = []
    while True:
        response = client.get(endpoint)
        items = response.get("value", [])
        for item in items:
            if item.get("folder"):
                folders_to_process.append(item["id"])
            else:
                yield item

        next_link = response.get("@odata.nextLink")
        if next_link:
            endpoint = next_link
            continue

        if not folders_to_process:
            break

        folder_id = folders_to_process.pop(0)
        for item in get_folder_children(client, folder_id):
            if item.get("folder"):
                folders_to_process.append(item["id"])
            else:
                yield item


def get_shared_files(client: OneDriveApiClient) -> Iterator[OneDriveFileType]:
    endpoint = "/me/drive/sharedWithMe"
    while True:
        response = client.get(endpoint)
        items = response.get("value", [])
        for item in items:
            if not item.get("folder"):
                yield item

        next_link = response.get("@odata.nextLink")
        if not next_link:
            break
        endpoint = next_link 