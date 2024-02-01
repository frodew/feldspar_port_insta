import port.api.props as props
from port.api.assets import *
from port.api.commands import (CommandSystemDonate, CommandSystemExit, CommandUIRender)

from datetime import datetime, timezone, timedelta
import zipfile
#from ddpinspect import instagram

import pandas as pd
import json
import time

from port.extraction_functions import *
from port.extraction_functions_dict import extraction_dict



# all functions during the donation process are called here

def process(sessionId):
    print(read_asset("hello_world.txt"))

    key = "zip-contents-example"
    meta_data = []
    meta_data.append(("debug", f"{key}: start"))

    # STEP 1: select the file
    data = None
    while True:
        meta_data.append(("debug", f"{key}: prompt file"))
        promptFile = prompt_file("application/zip, text/plain")
        fileResult = yield render_donation_page(promptFile)
        if fileResult.__type__ == 'PayloadString':
            # Extracting the zipfile
            meta_data.append(("debug", f"{key}: extracting file"))
            extraction_result = []
            zipfile_ref = get_zipfile(fileResult.value)
            print(zipfile_ref, fileResult.value)
            files = get_files(zipfile_ref)
            fileCount = len(files)
            for index, filename in enumerate(files):
                percentage = ((index+1)/fileCount)*100
                promptMessage = prompt_extraction_message(f"Extracting file: {filename}", percentage)   
                yield render_donation_page(promptMessage)   
                file_extraction_result = extract_file(zipfile_ref, filename)
                extraction_result.append(file_extraction_result)

            if len(extraction_result) >= 0:
                meta_data.append(("debug", f"{key}: extraction successful, go to consent form"))
                data = extraction_result
                break
            else:
                meta_data.append(("debug", f"{key}: prompt confirmation to retry file selection"))
                retry_result = yield render_donation_page(retry_confirmation())
                if retry_result.__type__ == 'PayloadTrue':
                    meta_data.append(("debug", f"{key}: skip due to invalid file"))
                    continue
                else:
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    break

    # STEP 2: ask for consent
    meta_data.append(("debug", f"{key}: prompt consent"))
    prompt = prompt_consent(data, meta_data)
    consent_result = yield render_donation_page(prompt)
    if consent_result.__type__ == "PayloadJSON":
        meta_data.append(("debug", f"{key}: donate consent data"))
        yield donate(f"{sessionId}-{key}", consent_result.value)
    if consent_result.__type__ == "PayloadFalse":   
        value = json.dumps('{"status" : "donation declined"}')
        yield donate(f"{sessionId}-{key}", value)



# render pages used in process

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

        try:
            target_df = v["extraction_function"](target_file)
        
        except:
            target_df = pd.DataFrame(["Empty"], columns=[str(file)])
        
        data.append(target_df)


    return data


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
        
        targetdict = {}

        for file_name in file_names:
                if (file_name.endswith('.json')) and (pattern in file_name):
                    # Read the JSON file into a dictionary
                    with zip_ref.open(file_name) as json_file:
                        json_content = json_file.read()
                        data = json.loads(json_content)
                        targetdict[file_name] = data
                    break

                if file_name == file_names[-1]:
                    print(f"File {pattern}.json is not contained")
                    return None

    return targetdict[file_name]



#main content of consent page: displays all data in donation

def prompt_consent(data, meta_data):

    table_list = []
    i = 0

    for file, v in extraction_dict.items():
        table = props.PropsUIPromptConsentFormTable(file, props.Translatable(v["title"]), data[i])
        table_list.append(table)
        i += 1
    
    return props.PropsUIPromptConsentForm(table_list, [])



# unedited from PORT, best leave like that :)

def donate(key, json_string):
    return CommandSystemDonate(key, json_string)


def exit(code, info):
    return CommandSystemExit(code, info)
