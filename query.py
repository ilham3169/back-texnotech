from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

# Load credentials from token
creds = Credentials.from_authorized_user_file('token.json')

# Correct API name and version
service = build('webmasters', 'v3', credentials=creds)

SITE_URL = 'sc-domain:texnotech.com'

request = {
    'startDate': '2024-04-01',
    'endDate': '2024-04-30',
    'dimensions': ['date'],
    'rowLimit': 1000
}

response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()

# Print each row in readable JSON format
for row in response.get('rows', []):
    print(json.dumps(row, indent=2))
