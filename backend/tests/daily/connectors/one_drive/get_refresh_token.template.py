import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import requests
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.append(str(backend_dir))

from onyx.connectors.one_drive.constants import SCOPE, AUTH_URL, TOKEN_URL

# OAuth 2.0 settings - Replace these with your app's values
CLIENT_ID = ""          # Your app's client ID
CLIENT_SECRET = ""      # Your app's client secret
TENANT_ID = ""         # Your tenant ID
REDIRECT_URI = "http://localhost:8000/callback"

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the authorization code from the callback URL
        query_components = parse_qs(urlparse(self.path).query)
        
        if 'code' in query_components:
            # Get the authorization code
            auth_code = query_components['code'][0]
            
            # Exchange authorization code for tokens
            token_data = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'code': auth_code,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code',
                'scope': ' '.join(SCOPE)
            }
            
            response = requests.post(TOKEN_URL, data=token_data)
            tokens = response.json()
            
            if 'refresh_token' in tokens:
                # Save the refresh token
                print("\nRefresh Token obtained successfully!")
                print("\nHere's your new refresh token:")
                print(tokens['refresh_token'])
                print("\nUpdate this token in your set_test_env.ps1 script.")
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Success! You can close this window now.")
            else:
                print("\nError getting refresh token:")
                print(json.dumps(tokens, indent=2))
                
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Error getting refresh token. Check the console output.")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"No authorization code received")

def get_authorization_url():
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPE),
        'response_mode': 'query'
    }
    
    # Convert params to URL query string
    query_string = '&'.join(f"{k}={requests.utils.quote(v)}" for k, v in params.items())
    return f"{AUTH_URL}?{query_string}"

def main():
    # Start the local server
    server = HTTPServer(('localhost', 8000), OAuthCallbackHandler)
    print("Starting local server...")
    
    # Get and open the authorization URL
    auth_url = get_authorization_url()
    print("\nOpening browser to authorize the application...")
    print(f"\nIf the browser doesn't open automatically, visit this URL:\n{auth_url}")
    webbrowser.open(auth_url)
    
    # Wait for the callback
    print("\nWaiting for authorization...")
    server.handle_request()
    server.server_close()

if __name__ == '__main__':
    main() 