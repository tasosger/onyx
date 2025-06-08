from typing import List, Optional

class OneDriveError(Exception):
    pass


class OneDriveAuthError(OneDriveError):
    def __init__(self, message: str):
        super().__init__(message)


class OneDriveCredentialsError(OneDriveError):
    def __init__(self, message: str, missing_fields: List[str]):
        self.missing_fields = missing_fields
        super().__init__(f"{message}: {', '.join(missing_fields)}")


class OneDriveNotFoundError(OneDriveError):
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(f"{resource_type} not found: {resource_id}")


class OneDriveRateLimitError(OneDriveError):
    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message)


class OneDriveRequestError(OneDriveError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"Request failed with status {status_code}: {message}")


class OneDriveServerError(OneDriveError):
    pass


class OneDriveClientRequestFailedError(OneDriveRequestError):
    pass 