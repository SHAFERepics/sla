#=========================================================------
#***PURPOSE***
#-------------
# Handle an API request to call a google apps script that can manage actions such as 
# connecting a google form's responses to a google sheet
# 

#import requests
#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request
from service_authentication import authenticate_service_account

#WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzu6eLbKVl-fEMbXb4Tn-gZG3Xjseg8BpuHi8gFtIOzhh6YNPYQBbVyM6sCZUSgfPfwyQ/exec" 
#Comes from the deploy section in the google app script we run

SCRIPT_ID = "1Eg52dawiUREWuE2Q6M7XcV3NEjZuX0JTir1DrWDA8AFChFt2CE3C-nZD"
#Comes from the url of the app script editor

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/script.external_request', 'https://www.googleapis.com/auth/script.scriptapp', 'https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/script.projects"]  
#Spreadsheets and forms scopes are required by the app script. Drive scope seemed to fix an authentication 401 error. The other two may or may not be necessary for calling app scripts, I'm not sure.


def call_google_apps_script(function, parameters):
    '''
    Attempts calling the google apps script file from WEB_APP_URL with the inputted parameters
    '''
    service = authenticate_service_account('script','v1', SCOPES)

    request = {
        "function": function,  
        "parameters": parameters,
        "devMode": True,
        
    }

    # Make the API call
    response = service.scripts().run(body=request, scriptId=SCRIPT_ID).execute()

    # Handle the response
    if 'error' in response:
        print("Script error:", response['error']['details'][0]['errorMessage'])
    else:
        print("Script result:", response)
        return response['response'].get('result')

if __name__ == '__main__':
    #My test call that successfully linked a form to a specific google sheet
    #params = {'function': 'linkFormToSheet', 'f_id': '17PoKFAum28Fd_WdggV5QUOUnJvcuMh_9U36MZcP2ncQ', 's_id': '1JQ6Qm55Ku-jQoNn9mDhxVUzCb8dE-Sk2oZ7x4hF1diI'}
    #call_google_apps_script(params)

    #My test call that succesfully duplicated an old form to a new one (with theme, questions, description, everything)
    #params = {'function':'duplicateForm', 'f_id':'19DiZMuiejDLgYUKLmP5sGO66BR7rhoiZrQ-_KjKLISI', 'title':'api_duplicated2'}
    #call_google_apps_script(params)

    op = call_google_apps_script("outputter", ["testing"])
    print(op)