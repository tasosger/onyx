import os
from typing import Generator

import pytest
from onyx.connectors.one_drive.client import OneDriveApiClient
from onyx.connectors.one_drive.connector import OneDriveConnector
from unittest.mock import patch, MagicMock

from .consts_and_utils import TEST_CREDENTIALS
from onyx.utils.logger import setup_logger
from .mock_data import MOCK_TOKEN_RESPONSE

logger = setup_logger()


@pytest.fixture(scope="session")
def mock_env_vars_session():
    os.environ["ENABLE_PAID_ENTERPRISE_EDITION_FEATURES"] = "True"
    os.environ["ONEDRIVE_CLIENT_ID"] = "mock_client_id"
    os.environ["ONEDRIVE_CLIENT_SECRET"] = "mock_client_secret"
    os.environ["ONEDRIVE_TENANT_ID"] = "mock_tenant_id"
    os.environ["ONEDRIVE_REFRESH_TOKEN"] = "mock_refresh_token"
    os.environ["ONEDRIVE_TEST_FILE_ID"] = "test_file_id"
    os.environ["ONEDRIVE_TEST_FOLDER_ID"] = "test_folder_id"
    os.environ["ONEDRIVE_TEST_SHARED_FILE_ID"] = "shared_file_id"
    os.environ["ONEDRIVE_TEST_USER_EMAIL"] = "test@example.com"
    os.environ["ONEDRIVE_TEST_USER_FILES"] = "test_file_1,test_file_2"
    os.environ["ONEDRIVE_TEST_SHARED_FILES"] = "shared_file_1,shared_file_2"
    os.environ["ONEDRIVE_TEST_FOLDER_FILES"] = "folder_file_1,folder_file_2"
    os.environ["ONEDRIVE_TEST_FOLDER_URL"] = "https://example.com/folder"
    os.environ["ONEDRIVE_TEST_SHARED_URL"] = "https://example.com/shared"
    yield
    for key in [
        "ENABLE_PAID_ENTERPRISE_EDITION_FEATURES",
        "ONEDRIVE_CLIENT_ID",
        "ONEDRIVE_CLIENT_SECRET",
        "ONEDRIVE_TENANT_ID",
        "ONEDRIVE_REFRESH_TOKEN",
        "ONEDRIVE_TEST_FILE_ID",
        "ONEDRIVE_TEST_FOLDER_ID",
        "ONEDRIVE_TEST_SHARED_FILE_ID",
        "ONEDRIVE_TEST_USER_EMAIL",
        "ONEDRIVE_TEST_USER_FILES",
        "ONEDRIVE_TEST_SHARED_FILES",
        "ONEDRIVE_TEST_FOLDER_FILES",
        "ONEDRIVE_TEST_FOLDER_URL",
        "ONEDRIVE_TEST_SHARED_URL",
    ]:
        os.environ.pop(key, None)


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch, mock_env_vars_session):
    pass


@pytest.fixture
def mock_api_client():
    client = MagicMock(spec=OneDriveApiClient)
    client.access_token = "mock_access_token"
    client.refresh_token = "mock_refresh_token"
    client.client_id = "mock_client_id"
    client.client_secret = "mock_client_secret"
    client.tenant_id = "mock_tenant_id"
    return client


@pytest.fixture
def one_drive_connector(mock_api_client):
    connector = OneDriveConnector()
    connector.load_credentials({
        "token": "mock_access_token",
        "refresh_token": "mock_refresh_token",
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "tenant_id": "mock_tenant_id"
    })
    connector.client = mock_api_client
    return connector 