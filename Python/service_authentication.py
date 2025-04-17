from google.oauth2 import service_account
from googleapiclient.discovery import build

#SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/script.external_request', 'https://www.googleapis.com/auth/script.scriptapp', 'https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/spreadsheets']  

def authenticate_service_account(service, version, scopes):
    creds = service_account.Credentials.from_service_account_file(
        'service_account.json',
        scopes=scopes
    )

    service = build(service, version, credentials=creds)
    return service

