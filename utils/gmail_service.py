import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_PATH = 'credentials/credentials.json'
TOKEN_PATH = 'credentials/token.json'

def get_gmail_service():
    """Create and return Gmail API service"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def get_emails(service, max_results=500):
    """Retrieve emails from Gmail"""
    result = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = result.get('messages', [])
    
    emails = []
    for message in messages:
        email = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        emails.append(email)
    
    return emails

def extract_email_data(email):
    """Extract relevant data from email"""
    headers = email['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
    from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
    
    # Extract body
    body = ""
    if 'parts' in email['payload']:
        for part in email['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
    elif 'body' in email['payload'] and 'data' in email['payload']['body']:
        body = base64.urlsafe_b64decode(email['payload']['body']['data']).decode('utf-8')
    
    return {
        'subject': subject,
        'from': from_email,
        'date': date,
        'body': body[:1000],  # Truncate to first 1000 chars
        'thread_id': email['threadId'],
        'email_id': email['id']
    }
