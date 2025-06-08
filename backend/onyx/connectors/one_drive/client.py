from typing import Any, Dict, Optional
import random
import requests
import time
import io
import json
from urllib.parse import urljoin

from .constants import RETRYABLE_STATUSES, TOKEN_URL, SCOPE, AUTH_URL
from .errors import (
    OneDriveAuthError,
    OneDriveCredentialsError,
    OneDriveNotFoundError,
    OneDriveRateLimitError,
    OneDriveRequestError,
    OneDriveServerError
)

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
        # Validate required credentials
        missing_fields = []
        if not client_id:
            missing_fields.append("client_id")
        if not client_secret:
            missing_fields.append("client_secret")
        if not tenant_id:
            missing_fields.append("tenant_id")
        if not refresh_token and not access_token:
            missing_fields.append("refresh_token or access_token")
        
        if missing_fields:
            raise OneDriveCredentialsError("Missing required credentials", missing_fields)

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
            raise OneDriveCredentialsError(
                "Missing OAuth2 credentials for token refresh",
                [f for f in ["client_id", "client_secret", "tenant_id", "refresh_token"]
                 if not getattr(self, f)]
            )

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "scope": " ".join(SCOPE)
        }

        try:
            response = requests.post(TOKEN_URL, data=data)
            
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                raise OneDriveRateLimitError(int(retry_after) if retry_after else None)
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", response.text)
                if response.status_code == 401:
                    raise OneDriveAuthError(error_msg)
                raise OneDriveRequestError(response.status_code, error_msg)

            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data["refresh_token"]

        except requests.exceptions.RequestException as e:
            raise OneDriveServerError(f"Failed to refresh token: {str(e)}")

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
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    stream=stream,
                    json=json
                )
                
                if stream and response.ok:
                    return io.BytesIO(response.content)

                if response.status_code == 401 and self.refresh_token:
                    self._refresh_access_token()
                    headers = self._build_headers()
                    retries += 1
                    continue

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    if retries < self.max_retries:
                        sleep_time = int(retry_after) if retry_after else (
                            self.backoff_factor * (2 ** retries) + random.uniform(0, 1)
                        )
                        time.sleep(sleep_time)
                        retries += 1
                        continue
                    raise OneDriveRateLimitError(int(retry_after) if retry_after else None)

                if response.status_code in RETRYABLE_STATUSES and retries < self.max_retries:
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

                    if response.status_code == 404:
                        raise OneDriveNotFoundError("Resource", endpoint)
                    elif response.status_code == 401:
                        raise OneDriveAuthError(error_msg)
                    elif response.status_code >= 500:
                        raise OneDriveServerError(error_msg)
                    else:
                        raise OneDriveRequestError(response.status_code, error_msg)

                try:
                    return response.json()
                except Exception as e:
                    return response.text

            except requests.exceptions.RequestException as e:
                if retries < self.max_retries:
                    sleep_time = self.backoff_factor * (2 ** retries) + random.uniform(0, 1)
                    time.sleep(sleep_time)
                    retries += 1
                    continue
                raise OneDriveServerError(f"Request failed: {str(e)}")

        raise OneDriveServerError("Max retries exceeded")

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
