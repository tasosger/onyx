import pytest
from unittest.mock import patch, Mock

from onyx.connectors.models import ConnectorMissingCredentialError
from onyx.connectors.one_drive.connector import OneDriveConnector
from onyx.connectors.one_drive.client import OneDriveApiClient, OneDriveClientRequestFailedError
from .mock_data import MOCK_TOKEN_RESPONSE

from .consts_and_utils import TEST_CREDENTIALS


def test_missing_credentials():
    connector = OneDriveConnector()
    with pytest.raises(ConnectorMissingCredentialError) as exc_info:
        connector.validate_connector_settings()
    assert "Client not initialized" in str(exc_info.value)


@patch("onyx.connectors.one_drive.client.requests.post")
def test_refresh_token(mock_post, mock_api_client):
    connector = OneDriveConnector()
    connector.load_credentials({
        "token": "old_token",
        "refresh_token": "old_refresh_token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "tenant_id": "test_tenant_id"
    })
    
    # Setup mock
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = MOCK_TOKEN_RESPONSE
    
    # Refresh token
    new_token = connector.refresh_token()
    
    assert new_token["access_token"] == MOCK_TOKEN_RESPONSE["access_token"]
    assert new_token["refresh_token"] == MOCK_TOKEN_RESPONSE["refresh_token"]


@patch("onyx.connectors.one_drive.client.requests.post")
@patch("onyx.connectors.one_drive.client.requests.request")
def test_validate_credentials(mock_request, mock_post, mock_api_client):
    connector = OneDriveConnector()
    
    # Test with valid credentials
    connector.load_credentials({
        "token": "valid_token",
        "refresh_token": "valid_refresh_token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "tenant_id": "test_tenant_id"
    })
    mock_request.return_value = Mock(ok=True, json=lambda: {"id": "test_user"})
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = MOCK_TOKEN_RESPONSE
    
    connector.validate_connector_settings()


@patch("onyx.connectors.one_drive.client.requests.post")
def test_invalid_credentials(mock_post, mock_api_client):
    connector = OneDriveConnector()
    invalid_creds = {
        "client_id": "invalid",
        "client_secret": "invalid",
        "tenant_id": "invalid",
        "refresh_token": "invalid"
    }
    
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Invalid credentials"
    
    with pytest.raises(OneDriveClientRequestFailedError) as exc_info:
        connector.update_credentials(invalid_creds)
    
    assert exc_info.value.status_code == 400
    assert "Invalid credentials" in str(exc_info.value)


@patch("onyx.connectors.one_drive.client.requests.post")
@patch("onyx.connectors.one_drive.client.requests.request")
def test_valid_credentials(mock_request, mock_post, mock_api_client):
    connector = OneDriveConnector()
    connector.load_credentials({
        "token": "valid_token",
        "refresh_token": "valid_refresh_token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "tenant_id": "test_tenant_id"
    })
    mock_request.return_value = Mock(ok=True, json=lambda: {"id": "test_user"})
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = MOCK_TOKEN_RESPONSE
    
    connector.validate_connector_settings()


@patch("onyx.connectors.one_drive.client.requests.post")
@patch("onyx.connectors.one_drive.client.requests.request")
def test_refresh_token_flow(mock_request, mock_post, mock_api_client):
    connector = OneDriveConnector()
    connector.load_credentials({
        "token": "valid_token",
        "refresh_token": "valid_refresh_token",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "tenant_id": "test_tenant_id"
    })
    
    # First call succeeds
    mock_request.return_value = Mock(ok=True, json=lambda: {"id": "test_user"})
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = MOCK_TOKEN_RESPONSE
    
    response = connector.client.get("/me")
    assert response == {"id": "test_user"}
    
    # Second call fails with 401, triggering token refresh
    mock_request.side_effect = [
        Mock(ok=False, status_code=401, text="Token expired"),
        Mock(ok=True, json=lambda: {"id": "test_user"})
    ]
    
    response = connector.client.get("/me")
    assert response == {"id": "test_user"}


def test_token_refresh_with_invalid_refresh_token():
    connector = OneDriveConnector()
    with pytest.raises(ConnectorMissingCredentialError) as exc_info:
        connector.refresh_token()
    assert "Client not initialized" in str(exc_info.value) 