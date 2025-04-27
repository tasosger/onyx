from typing import Any, Dict, List

import random
import requests
import time


RETRYABLE_STATUSES = {502, 503, 504}


class OneDriveClientRequestFailedError(ConnectionError):
    def __init__(self, status: int, error: str) -> None:
        self.status_code = status
        self.error = error
        super().__init__(
            f"OneDrive Client request failed with status {status}: {error}"
        )


class OneDriveApiClient:
    def __init__(
        self,
        access_token: str,
        max_retries: int = 5,
        backoff_factor: float = 2.0,
    ) -> None:
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def _build_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

    def get(self, endpoint: str, params: Dict[str, str] | None = None) -> Dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self._build_headers()
        retries = 0

        while retries <= self.max_retries:
            try:
                response = requests.get(url, headers=headers, params=params)

                try:
                    json_data = response.json()
                except Exception:
                    json_data = {}

                if response.status_code >= 300:
                    error = response.reason
                    response_error = json_data.get("error", {}).get("message", "")
                    if response_error:
                        error = response_error
                    raise OneDriveClientRequestFailedError(response.status_code, error)

                return json_data
            except OneDriveClientRequestFailedError as e:
                if e.status_code not in RETRYABLE_STATUSES:
                    raise e
                retries += 1
                if retries > self.max_retries:
                    raise
                sleep_time = self.backoff_factor * (2 ** (retries - 1)) + random.uniform(0, 1)
                time.sleep(sleep_time)
            except requests.RequestException as e:
                retries += 1
                if retries > self.max_retries:
                    raise OneDriveClientRequestFailedError(503, str(e))
                sleep_time = self.backoff_factor * (2 ** (retries - 1)) + random.uniform(0, 1)
                time.sleep(sleep_time)

        raise OneDriveClientRequestFailedError(500, "Maximum retries exceeded with no successful response")
