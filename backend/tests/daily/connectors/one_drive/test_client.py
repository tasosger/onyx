import os
from onyx.connectors.one_drive.client import OneDriveApiClient

def test_onedrive_client():
    """Test basic OneDrive client functionality."""
    print("\nChecking environment variables:")
    required_vars = [
        "ONEDRIVE_CLIENT_ID",
        "ONEDRIVE_CLIENT_SECRET",
        "ONEDRIVE_TENANT_ID",
        "ONEDRIVE_REFRESH_TOKEN",
    ]
    
    for var in required_vars:
        value = os.environ.get(var, '')
        print(f"{var}: {'✓ Set' if value else '✗ Missing'}")
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")

    # Initialize client
    print("\nInitializing OneDrive client...")
    client = OneDriveApiClient(
        client_id=os.environ["ONEDRIVE_CLIENT_ID"],
        client_secret=os.environ["ONEDRIVE_CLIENT_SECRET"],
        tenant_id=os.environ["ONEDRIVE_TENANT_ID"],
        refresh_token=os.environ["ONEDRIVE_REFRESH_TOKEN"]
    )

    # Test connection
    print("\nTesting connection...")
    user_info = client.get("/me")
    print(f"Connected as: {user_info.get('displayName', 'Unknown')} ({user_info.get('mail', 'No email')})")

    # List files
    print("\nListing files...")
    files = client.get("/me/drive/root/children")
    print(f"Found {len(files.get('value', []))} files in root")
    for file in files.get('value', [])[:3]:
        print(f"- {file.get('name')} ({file.get('id')})")

if __name__ == "__main__":
    test_onedrive_client() 