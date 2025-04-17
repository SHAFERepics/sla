import os
import pickle
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def authenticate_google_account(SCOPES):
    '''
    Accesses or creates a token and initiates OAuth flow if necessary. Returns the credentials.
    '''
    creds = None
    #If we already have a token, go ahead and use that
    if os.path.exists('token.pickle'): 
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        if not creds.valid:
            print("Credentials are not currently valid")

    #If the token doesnt exist or needs to be refreshed, lets do that
    if not creds or not creds.valid: 
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            #The 'flow' will open in the browser and request you to select an account and approve the app to manage it
            flow = InstalledAppFlow.from_client_secrets_file(
                'api_data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080) #originally 0, a dynamically chosen port, but set now to specific so the API can work

        #Save the new token in the .pickle file
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def clear_token():
    '''
    Attempts to clear the current token by revoking it and deleting the file
    '''
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
        revoke_token(creds.token)

def revoke_token(token):
    '''
    Attempts to revoke the inputted token
    '''
    url = f'https://oauth2.googleapis.com/revoke?token={token}'
    response = requests.post(url)
    
    if response.status_code == 200:
        print("Token successfully revoked.")
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
            print("Token file deleted.")
    else:
        print(f"Failed to revoke token. Status code: {response.status_code}")