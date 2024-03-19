import port.api.props as props
from port.api.commands import (CommandSystemDonate, CommandSystemExit, CommandUIRender)

from datetime import datetime, timezone, timedelta
import zipfile
import cv2
from PIL import Image
import numpy as np
import time

import pandas as pd
import json

from port.extraction_functions import *
from port.extraction_functions_dict import extraction_dict

# MAIN FUNCTION INITIATING THE DONATION PROCESS

def process(sessionId):
    
    key = "instagram_data_donation"
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

            if extractionResult != 'invalid':

                meta_data.append(("debug", f"{key}: extraction successful, go to consent form"))
                data = extractionResult
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

    # STEP 2: Present user their extracted data and ask for consent

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

def prompt_file(extensions):
    description = props.Translatable({
        "en": "Please select your downloaded Instagram ZIP file from your device. The file should be named like \"instagram-USERNAME-DATE-...-.zip\".",
        "nl": "Selecteer een willekeurige zip file die u heeft opgeslagen op uw apparaat."
    })

    return props.PropsUIPromptFileInput(description, extensions)

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
        "en": "Unfortunately, we cannot process your file. Are you sure that you selected the downloaded Instagram ZIP file? The file should be named like \"instagram-USERNAME-DATE-...-.zip\". Make sure it is a zip file.",
        "nl": "Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen."
    })

    ok = props.Translatable({
        "en": "Try again",
        "nl": "Probeer opnieuw"
    })

    cancel = props.Translatable({
        "en": "Continue",
        "nl": "Verder"
    })

    return props.PropsUIPromptConfirm(text, ok, cancel)




# extraction of zip files -------------------------------------------------

#main function to process zip files
def extract_data(filename): 
    """takes zip folder, extracts relevant json file contents (your_topics, posts_viewed, videos_watched), then extracts & processes relevant information and returns them as dataframes"""
    
    def check_faces_in_zip(filename):
        """This function checks the number of faces in each image file within a zip file."""

        face_dict = {}

        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Set the desired size for the images
        size = 200, 200

        # Open the zip file in read mode
        with zipfile.ZipFile(filename, 'r') as zip_ref:

            # Iterate through each file in the zip file
            for file in zip_ref.namelist():

                # Check if the file is a jpg image and in the media folder
                if file.lower().endswith('.jpg') and file.lower().startswith('media'):

                    # Open the image file within the zip file
                    with zip_ref.open(file) as img_file:

                        start_time = time.time()  # Record start time

                        # Load the image from bytes
                        img_bytes = Image.open(img_file)

                        # Convert the image to grayscale
                        img_gray = img_bytes.convert("L")

                        # Resize the image to the desired size
                        img_gray.thumbnail(size, Image.Resampling.LANCZOS)

                        # Convert the image to a numpy array
                        img_down_np = np.array(img_gray)

                        # Detect faces in the image
                        faces = face_cascade.detectMultiScale(img_down_np, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))
                        
                        end_time = time.time()  # Record end time
                        processing_time = end_time - start_time  # Calculate processing time
                        print("PLI - Processing time for {}: {:.2f} seconds".format(file, processing_time))

                        # Count faces in picture
                        face_dict[file] = len(faces)

        # Return the dictionary containing the number of faces in each image
        return face_dict

    picture_info = check_faces_in_zip(filename)

    data = []

    for file, v in extraction_dict.items():
        
        target_file = extractJsonContentFromZipFolder(filename, file)

        try:
            if "picture_info" in v:  # Check if picture_info is required for this extraction function
                target_df = v["extraction_function"](target_file, picture_info)
            else:
                target_df = v["extraction_function"](target_file)

        except Exception as e:
            print(target_file, e)
            target_df = pd.DataFrame(["file_does_not_exist"], columns=[str(file)])
        
        data.append(target_df)


    return data


# helper function for extraction
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
