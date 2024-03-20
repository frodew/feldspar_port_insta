import port.api.props as props
from port.api.assets import *
from port.api.commands import (CommandSystemDonate, CommandSystemExit, CommandUIRender)

from port.extraction_functions import *
from port.extraction_functions_dict import extraction_dict

import zipfile
import cv2
from PIL import Image
import numpy as np
import time

import pandas as pd
import json
import time


############################
# MAIN FUNCTION INITIATING THE DONATION PROCESS
############################

def process(sessionId):
    print(read_asset("hello_world.txt"))

    key = "zip-contents-example"
    meta_data = []
    meta_data.append(("debug", f"{key}: start"))

    # STEP 1: Select DDP and extract automatically required data
    
    data = None

    while True:
        meta_data.append(("debug", f"{key}: prompt file"))

        # allow users to only upload zip-files and render file-input page 
        promptFile = prompt_file("application/zip")
        fileResult = yield render_donation_page(promptFile)
        
        # if user input
        if fileResult.__type__ == 'PayloadString':

            meta_data.append(("debug", f"{key}: extracting file"))

            # automatically extract required data
            extractionResult = extract_data(fileResult.value)

            if extractionResult != 'invalid_file':

                meta_data.append(("debug", f"{key}: extraction successful, go to consent form"))
                data = extraction_result
                break

            else:

                meta_data.append(("debug", f"{key}: prompt confirmation to retry file selection"))
                retry_result = yield render_donation_page(retry_confirmation())

                if retry_result.__type__ == 'PayloadTrue':
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue
                
                # deactivated options for users to continue without valid file

                # else:
                #     meta_data.append(("debug", f"{key}: skip due to invalid file"))
                #     break

    # STEP 2: Present user their extracted data and ask for consent

    meta_data.append(("debug", f"{key}: prompt consent"))
    # render donation page with extracted data
    prompt = prompt_consent(data, meta_data)
    consent_result = yield render_donation_page(prompt)

    # send data if consent
    if consent_result.__type__ == "PayloadJSON":
        meta_data.append(("debug", f"{key}: donate consent data"))
        yield donate(f"{sessionId}-{key}", consent_result.value)

    # send no data if no consent
    if consent_result.__type__ == "PayloadFalse":   
        value = json.dumps('{"status" : "donation declined"}')
        yield exit(f"{sessionId}-{key}", value)



############################
# Render pages used in step 1
############################

def render_donation_page(body):
    header = props.PropsUIHeader(props.Translatable({
        "en": "Port flow example",
        "de": "Port Beispiel",
        "nl": "Port voorbeeld flow"
    }))

    page = props.PropsUIPageDonation("Zip", header, body)
    return CommandUIRender(page)


def retry_confirmation():
    text = props.Translatable({
        "en": "Unfortunately, we cannot process your file. Continue, if you are sure that you selected the right file. Try again to select a different file.",
        "de": "Leider können wir Ihre Datei nicht bearbeiten. Fahren Sie fort, wenn Sie sicher sind, dass Sie die richtige Datei ausgewählt haben. Versuchen Sie, eine andere Datei auszuwählen.",
        "nl": "Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen."
    })
    ok = props.Translatable({
        "en": "Try again",
        "de": "Versuchen Sie es noch einmal",
        "nl": "Probeer opnieuw"
    })
    cancel = props.Translatable({
        "en": "Continue",
        "de": "Weiter",
        "nl": "Verder"
    })
    return props.PropsUIPromptConfirm(text, ok, cancel)


def prompt_file(extensions):
    description = props.Translatable({
        "en": "Please select any zip file stored on your device.",
        "de": "Wählen Sie eine beliebige Zip-Datei aus, die Sie auf Ihrem Gerät gespeichert haben.",
        "nl": "Selecteer een willekeurige zip file die u heeft opgeslagen op uw apparaat."
    })

    return props.PropsUIPromptFileInput(description, extensions)

def prompt_extraction_message(message, percentage):
    description = props.Translatable({
        "en": "One moment please. Information is now being extracted from the selected file.",
        "de": "Einen Moment bitte. Es werden nun Informationen aus der ausgewählten Datei extrahiert.",
        "nl": "Een moment geduld. Informatie wordt op dit moment uit het geselecteerde bestaand gehaald."
    })

    return props.PropsUIPromptProgress(description, message, percentage)

    data = []

def get_zipfile(filename):
    try:
        return zipfile.ZipFile(filename)
    except zipfile.error:
        return "invalid"
    
   
def get_files(zipfile_ref):
    try: 
        return zipfile_ref.namelist()
    except zipfile.error:
        return []
def render_donation_page(body):

    platform = "Instagram"

    header = props.PropsUIHeader(props.Translatable({
        "en": "Instagram Data Donation",
        "nl": "Port voorbeeld flow"
    }))
    
    page = props.PropsUIPageDonation(platform, header, body)

    return CommandUIRender(page)


def retry_confirmation():

    text = props.Translatable({
        "en": "Unfortunately, we cannot process your file. Are you sure that you selected the downloaded Instagram ZIP file?\nThe file should be named like \"instagram-USERNAME-DATE-...-.zip\". Make sure it is a zip file.",
        "nl": "Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen."
    })

    ok = props.Translatable({
        "en": "Try again",
        "nl": "Probeer opnieuw"
    })

    # cancel = props.Translatable({
    #     "en": "Continue",
    #     "nl": "Verder"
    # })

    # return props.PropsUIPromptConfirm(text, ok, cancel)
    return props.PropsUIPromptConfirm(text, ok)



############################
# Extraction scripts
############################

# Main function to process zip files
def extract_data(filename): 
    """takes zip folder, extracts relevant json file contents, then extracts & processes relevant information and returns them as dataframes"""
    
    if not check_if_valid_instagram_ddp(filename):
        return "invalid_file"

    # Check if and how many faces are in pictures
    picture_info = check_faces_in_zip(filename)

    data = []

    for file, v in extraction_dict.items():
        
        # Extract json from file name based on "key"
        file_json = extractJsonContentFromZipFolder(filename, file)

        try:
            # Call the "value" extraction function
            if "picture_info" in v:  # Check if picture_info is required for this extraction function
                file_json_df = v["extraction_function"](file_json, picture_info)
            else:
                file_json_df = v["extraction_function"](file_json)

        except Exception as e:
            # Fails if file does not exist
            print(file_json, e)
            file_json_df = pd.DataFrame(["file_does_not_exist"], columns=[str(file)])
        
        data.append(file_json_df)

    return data

def check_if_valid_instagram_ddp(filename):

#main content of consent page: displays all data in donation

def extract_file(zipfile_ref, filename):
    try:
        # make it slow for demo reasons only
        time.sleep(1)
        info = zipfile_ref.getinfo(filename)
        return (filename, info.compress_size, info.file_size)
    except zipfile.error:
        return "invalid"
    

def prompt_consent(data, meta_data):

    table_title = props.Translatable({
        "en": "Zip file contents",
        "de": "Inhalt der Zip-Datei",
        "nl": "Inhoud zip bestand"
    })

    log_title = props.Translatable({
        "en": "Log messages",
        "de": "Log Nachrichten",
        "nl": "Log berichten"
    })

    videos_watched_title = props.Translatable({
        "en": "Number of videos watched each day in the last week",
        "nl": "Inhoud zip bestand"
    })


    table_list = []
    i = 0

    for file, v in extraction_dict.items():
        table = props.PropsUIPromptConsentFormTable(file, props.Translatable(v["title"]), data[i])
        table_list.append(table)
        i += 1
    
    return props.PropsUIPromptConsentForm(table_list, [])


# ---
# helper files for extraction

def extractJsonContentFromZipFolder(zip_file_path, pattern):

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:

        # Get the list of file names in the zip file
        file_names = zip_ref.namelist()
        
        file_json_dict = {}

        for file_name in file_names:
            if (file_name.endswith('.json')) and (pattern in file_name):

                # Read the JSON file into a dictionary
                with zip_ref.open(file_name) as json_file:
                    json_content = json_file.read()
                    data = json.loads(json_content)
                    file_json_dict[file_name] = data

                break
            
            # checks if loop is at last item
            if file_name == file_names[-1]:

                print(f"File {pattern}.json does not exist")
                return None

    return file_json_dict[file_name]

############################
# Render pages and functions used in step 2
############################

# Main content of consent page: display all extracted data
def prompt_consent(data, meta_data):

    table_list = []
    i = 0
    
    if data is not None: #can happen if user submitts wrong file and still continues
        for file, v in extraction_dict.items():
            table = props.PropsUIPromptConsentFormTable(file, props.Translatable(v["title"]), data[i])
            table_list.append(table)
            i += 1
    
    return props.PropsUIPromptConsentForm(table_list, [])

# pass on user decision to donate or decline donation
def donate(key, json_string):
    return CommandSystemDonate(key, json_string)

# unsure what this function does...
def exit(code, info):
    return CommandSystemExit(code, info)
