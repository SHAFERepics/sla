#=========================================================------
#***PURPOSE***
#-------------
# Update "program_data.json" to include new program details when
# an SLA employee enters information into the program creation form
#
#***Data required***
#-------------------
# The URL of the creation form to check

import json
import numpy as np
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from service_authentication import authenticate_service_account
from call_app_script import call_google_apps_script

CREATION_FORM_ID = "1GCE8SIKYwvZ8YNni_V0cHsCPmJD9pfps2NY1AjdBOJg"
#Id to the sheet that receives responses from the SLA Program Creation form

BASE_FEEDBACK_FORM_ID = "19DiZMuiejDLgYUKLmP5sGO66BR7rhoiZrQ-_KjKLISI"
#Id to the sheet that is duplicated for any newly created feedback form

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/spreadsheets']  
#Permissions we request


def perform_trigger():
    values, indices = read_new_rows(CREATION_FORM_ID)
    peform_actions(values, indices)

def get_sheet_range(spreadsheet_id, range_name):
    '''
    Retrieves a range from any spreadsheet
    Returns a result which you can access values from with .get("values", [])
    '''

    try:
        service = authenticate_service_account("sheets", "v4", SCOPES)

        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        print(f"{len(rows)} rows retrieved")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error
    
def read_new_rows(spreadsheet_id):
    '''
    Checks for any new rows in the given spreadsheet and returns the values and the indexes in the gsheet of the new values
    '''

    # Set the range to all rows and get the values from this range
    range_string = "A2:E"
    result = get_sheet_range(spreadsheet_id, range_string)
    all_values = np.array(result.get("values", []))

    # Filter out to new rows
    completed_column = all_values[:, 0]
    values = [all_values[index, 1:].tolist() for index, val in enumerate(completed_column) if val != 'TRUE']
    index_list = [index for index, condition in enumerate(completed_column) if condition != 'TRUE']

    return values, index_list

def peform_actions(values, indices):
    '''
    Takes in all rows and runs the new_row_action() function on each one
    '''
    for row, index in zip(values, indices):
        new_row_action(row, index)


def new_row_action(row_values, row_index):
    '''
    Peforms the standard action for a new row being added to a sheet.
    The standard action is to make a new form, then link the new form to a new spreadsheet, and finally save both these values for future use.
    Lastly, update the completed/uncompleted field in the spreadsheet row index to TRUE
    '''
    new_form_id = None
    new_sheet_id = None

    f_title = row_values[1]
    f_title = f_title.replace(" ", "_").lower()
    
    '''TODO write code here that checks if title is already in the list of active programs, then increment it with a while loop until its unique'''
    
    d_params = {
        'function':'duplicateForm',
        'f_id':BASE_FEEDBACK_FORM_ID,
        'title':f_title
    }

    d_response = call_google_apps_script(d_params)

    d_data = app_script_response_error_check(d_response)
    
    if d_data and d_data.get("formId"):
        new_form_id = d_data.get("formId")

        s_title = "responses_"+f_title
        c_params = {
            'function':'linkFormToNewSheet',
            'f_id':new_form_id,
            'title':s_title
        }

        c_response = call_google_apps_script(c_params)
        c_data = app_script_response_error_check(c_response)

        if c_data and c_data.get("sheetId"):
            new_sheet_id = c_data.get("sheetId")

    print("New row outputs: ")
    print(new_form_id, new_sheet_id)

def app_script_response_error_check(response):
    # Error checking for the response
    try:
        if response is None:
            data = None
            print("Response was an error or None")
        
        # Try parsing the response as JSON
        data = json.loads(response)
        
        #Check that data is a dictionary
        if not isinstance(data, dict):
            data = None
            print("The JSON was not properly converted to a dictionary.")

    except (json.JSONDecodeError, ValueError) as e:
        data = None
        print("Invalid response, was not converted to JSON:", e)

    return data

if __name__ == "__main__":
    perform_trigger()