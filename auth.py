import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes for the APIs you want to access.
# These scopes will grant read-only access to GA4 and GSC,
# and management access to GMB (necessary for full data retrieval).
SCOPES = [
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/business.manage'
]

TOKEN_JSON_PATH = 'token.json'
CREDENTIALS_JSON_PATH = 'credentials.json'

def get_credentials():
    """
    Handles user authentication for Google APIs.

    This function manages the OAuth 2.0 flow. It will look for a `token.json`
    file which stores the user's access and refresh tokens. If the file isn't
    found or the credentials have expired, it will initiate a new authorization
    flow, prompting the user to log in and grant access.

    The `credentials.json` file, which is required for this process, must be
    obtained from the Google Cloud Console.

    Returns:
        google.oauth2.credentials.Credentials: The authenticated credentials object.
    """
    creds = None
    if os.path.exists(TOKEN_JSON_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_JSON_PATH, SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_JSON_PATH):
                print(f"ERROR: '{CREDENTIALS_JSON_PATH}' not found.")
                print("Please follow the instructions in the README.md file to download your API credentials.")
                return None # Return None to indicate failure

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_JSON_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(TOKEN_JSON_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds

if __name__ == '__main__':
    # This block allows you to test the authentication flow directly.
    # Running `python auth.py` will prompt you to authenticate.
    print("Attempting to get user credentials...")
    credentials = get_credentials()
    if credentials:
        print("Authentication successful! `token.json` has been created/updated.")
        print("This script is now ready to be used by other modules.")
    else:
        print("Authentication failed. Please check the error messages above.")
