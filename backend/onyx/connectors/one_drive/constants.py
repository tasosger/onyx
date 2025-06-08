SCOPE = ["Files.Read", "User.Read", "offline_access"]
MICROSOFT_AUTHORITY = "https://login.microsoftonline.com/common"
RETRYABLE_STATUSES = {502, 503, 504}
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
AUTH_URL = f"{MICROSOFT_AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_URL = f"{MICROSOFT_AUTHORITY}/oauth2/v2.0/token" 