# OneDrive Test Environment Variables
$env:ONEDRIVE_TEST_USER_EMAIL = ""  # Add your Microsoft account email here

# Credentials from get_refresh_token.py
$env:ONEDRIVE_CLIENT_ID = ""        # Your app's client ID
$env:ONEDRIVE_CLIENT_SECRET = ""    # Your app's client secret
$env:ONEDRIVE_TENANT_ID = ""        # Your tenant ID
$env:ONEDRIVE_REFRESH_TOKEN = ""    # Get this from get_refresh_token.py

# Test File/Folder IDs (Get these from OneDrive web URLs)
$env:ONEDRIVE_TEST_FILE_ID = ""     # Test file ID
$env:ONEDRIVE_TEST_USER_FILES = ""  # Test file
$env:ONEDRIVE_TEST_FOLDER_ID = ""   # Test folder ID
$env:ONEDRIVE_TEST_SHARED_FILE_ID = ""  # Shared folder ID
$env:ONEDRIVE_TEST_SHARED_FILES = ""    # Using the shared folder ID

# URLs
$env:ONEDRIVE_TEST_FOLDER_URL = ""      # Regular folder URL
$env:ONEDRIVE_TEST_SHARED_URL = ""      # Shared folder URL

# Folder contents (if you have files in the folder, add their IDs here)
$env:ONEDRIVE_TEST_FOLDER_FILES = ""    # Add any file IDs that are in your test folder 