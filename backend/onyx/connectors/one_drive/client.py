from typing import Any, Dict, Optional
import random
import requests
import time
import io
import json
from urllib.parse import urljoin

from .constants import RETRYABLE_STATUSES, TOKEN_URL, SCOPE, AUTH_URL

class OneDriveClientRequestFailedError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"OneDrive Client request failed with status {status_code}: {message}")

class OneDriveApiClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        refresh_token: str,
        access_token: Optional[str] = None,
        base_url: str = "https://graph.microsoft.com/v1.0",
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.refresh_token = refresh_token
        self.access_token = access_token
        self.base_url = base_url
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        if not access_token:
            self._refresh_access_token()

    def _refresh_access_token(self) -> None:
        if not all([self.client_id, self.client_secret, self.tenant_id, self.refresh_token]):
            raise OneDriveClientRequestFailedError(401, "Missing OAuth2 credentials")

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "scope": " ".join(SCOPE)
        }

        print("\nRefreshing token with data:", data)
        response = requests.post(TOKEN_URL, data=data)
        print(f"Token refresh response status: {response.status_code}")
        print(f"Token refresh response: {response.text}")
        
        if response.status_code != 200:
            raise OneDriveClientRequestFailedError(
                response.status_code,
                f"Failed to refresh access token: {response.text}"
            )

        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data["refresh_token"]

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, str] | None = None,
        stream: bool = False,
        json: Dict[str, Any] | None = None
    ) -> Any:
        url = urljoin(self.base_url.rstrip('/') + '/', endpoint.lstrip('/'))
        headers = self._build_headers()
        retries = 0

        while retries <= self.max_retries:
            try:
                print(f"\nMaking request to {url}")
                print(f"Method: {method}")
                print(f"Headers: {headers}")
                print(f"Params: {params}")
                print(f"JSON: {json}")
                
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    stream=stream,
                    json=json
                )

                print(f"Response status: {response.status_code}")
                print(f"Response headers: {response.headers}")
                
                if stream and response.ok:
                    return io.BytesIO(response.content)

                if response.status_code == 401 and self.refresh_token:
                    print("Got 401, refreshing token...")
                    self._refresh_access_token()
                    headers = self._build_headers()
                    retries += 1
                    continue

                if response.status_code in RETRYABLE_STATUSES and retries < self.max_retries:
                    print(f"Got retryable status {response.status_code}, retrying...")
                    sleep_time = self.backoff_factor * (2 ** retries) + random.uniform(0, 1)
                    time.sleep(sleep_time)
                    retries += 1
                    continue

                if not response.ok:
                    error_msg = response.text
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", response.text)
                    except:
                        pass
                    print(f"Request failed with status {response.status_code}: {error_msg}")
                    raise OneDriveClientRequestFailedError(response.status_code, error_msg)

                try:
                    return response.json()
                except Exception as e:
                    print(f"Failed to parse JSON response: {str(e)}")
                    return response.text

            except requests.exceptions.RequestException as e:
                print(f"Request exception: {str(e)}")
                if retries < self.max_retries:
                    sleep_time = self.backoff_factor * (2 ** retries) + random.uniform(0, 1)
                    time.sleep(sleep_time)
                    retries += 1
                    continue
                raise OneDriveClientRequestFailedError(500, str(e))

        raise OneDriveClientRequestFailedError(500, "Max retries exceeded")

    def get(
        self,
        endpoint: str,
        params: Dict[str, str] | None = None,
        stream: bool = False
    ) -> Any:
        return self._make_request("GET", endpoint, params=params, stream=stream)

    def post(
        self,
        endpoint: str,
        data: Dict[str, Any] | None = None,
        params: Dict[str, str] | None = None
    ) -> Any:
        return self._make_request("POST", endpoint, params=params, json=data)

    def put(
        self,
        endpoint: str,
        data: Dict[str, Any] | None = None,
        params: Dict[str, str] | None = None
    ) -> Any:
        return self._make_request("PUT", endpoint, params=params, json=data)

    def delete(
        self,
        endpoint: str,
        params: Dict[str, str] | None = None
    ) -> Any:
        return self._make_request("DELETE", endpoint, params=params)

    def get_file_content(self, file_id: str, drive_id: str | None = None) -> bytes:
        endpoint = f"/me/drive/items/{file_id}/content"
        if drive_id:
            endpoint = f"/drives/{drive_id}/items/{file_id}/content"
        return self.get(endpoint, stream=True).read()
