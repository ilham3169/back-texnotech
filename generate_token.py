import os
import json
from datetime import date
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Set required scope
SCOPES = ['https://www.googleapis.com/auth/webmasters']

TOKEN_PATH = 'token.json'
CREDENTIALS_PATH = 'client_secret.json'

# Step 1: Get credentials
def get_credentials():
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_PATH,
            scopes=SCOPES
        )
        creds = flow.run_local_server(
            port=8000,
            prompt='consent',
            access_type='offline'
        )
        with open(TOKEN_PATH, 'w') as token_file:
            json.dump(json.loads(creds.to_json()), token_file)
    return creds

# Step 2: Build the service
creds = get_credentials()
service = build('webmasters', 'v3', credentials=creds)

# Step 3: List verified sites
site_list = service.sites().list().execute()
print("Verified properties:")
for site in site_list.get('siteEntry', []):
    print("→", site['siteUrl'])

# Step 4: Choose a site and make a query
# Example: use 'sc-domain:texnotech.com' if that's what appears in the above list
site_url = 'sc-domain:texnotech.com'  # or 'https://texnotech.com/' if that's what is shown

request_body = {
    'startDate': str(date(2024, 4, 1)),
    'endDate': str(date(2024, 4, 30)),
    'dimensions': ['query'],
    'rowLimit': 10
}

try:
    response = service.searchanalytics().query(
        siteUrl=site_url,
        body=request_body
    ).execute()

    print("\nTop search queries:")
    for row in response.get('rows', []):
        print(f"Query: {row['keys'][0]}, Clicks: {row.get('clicks', 0)}")

except Exception as e:
    print("\n❌ API Error:")
    print(e)
