import port.api.props as props
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


############################
# MAIN FUNCTION INITIATING THE DONATION PROCESS
############################

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

            check_ddp = check_if_valid_instagram_ddp(fileResult.value)

            if check_ddp == "valid":

                meta_data.append(("debug", f"{key}: extracting file"))

                # automatically extract required data
                data = extract_data(fileResult.value)

                meta_data.append(("debug", f"{key}: extraction successful, go to consent form"))

                break

            elif check_ddp == "invalid_no_json":

                meta_data.append(("debug", f"{key}: prompt confirmation to retry file selection (invalid_no_json)"))
                retry_result = yield render_donation_page(retry_confirmation_no_json())

                if retry_result.__type__ == 'PayloadTrue':
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue

            elif check_ddp == "invalid_no_ddp":

                meta_data.append(("debug", f"{key}: prompt confirmation to retry file selection (invalid_no_ddp)"))
                retry_result = yield render_donation_page(retry_confirmation_no_ddp())

                if retry_result.__type__ == 'PayloadTrue':
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue
                
            else:
                
                meta_data.append(("debug", f"{key}: prompt confirmation to retry file selection (invalid_file)"))
                print(check_ddp)
                retry_result = yield render_donation_page(retry_confirmation_no_ddp())

                if retry_result.__type__ == 'PayloadTrue':
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue

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
        yield donate(f"{sessionId}-{key}", value)



############################
# Render pages used in step 1
############################

def prompt_file(extensions):
    description = props.Translatable({
        "en": "Please select your downloaded Instagram ZIP file from your device. The file should be named like \"instagram-USERNAME-DATE-...-.zip\".\nDepending on the number of pictures you have, the extraction may take some time (~ 120 pictures/minute).\nFor example, if you have posted a picture each day over the last three months, the uploading should take arould one minute.",
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


def retry_confirmation_no_json():

    text = props.Translatable({
        "en": "Unfortunately, we cannot process your file. It seems like you submitted a HTML file of your Instagram data.\nPlease download your data from Instagram again and select the data format \"JSON\".\n The downloades file should be named like \"instagram-USERNAME-DATE-...-.zip\". Make sure it is a zip file.",
        "nl": "Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen."
    })

    ok = props.Translatable({
        "en": "Try again with JSON file",
        "nl": "Probeer opnieuw"
    })

    return props.PropsUIPromptConfirm(text, ok)

def retry_confirmation_no_ddp():

    text = props.Translatable({
        "en": "Unfortunately, we cannot process your file. Did you really select your downloaded Instagram ZIP file?\nThe downloades file should be named like \"instagram-USERNAME-DATE-...-.zip\". Make sure it is a zip file.",
        "nl": "Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen."
    })

    ok = props.Translatable({
        "en": "Try again",
        "nl": "Probeer opnieuw"
    })

    return props.PropsUIPromptConfirm(text, ok)

def check_if_valid_instagram_ddp(filename):

    folder_name_check_ddp = "ads_information"
    file_name_check_html = "start_here.html"

    try:

        with zipfile.ZipFile(filename, 'r') as zip_ref:

            found_folder_name_check_ddp = False
            found_file_name_check_html = False

            for file_info in zip_ref.infolist():

                if folder_name_check_ddp in file_info.filename:

                    found_folder_name_check_ddp = True
                
                elif file_name_check_html in file_info.filename:

                    found_file_name_check_html = True

            if found_folder_name_check_ddp:

                if found_file_name_check_html:

                    print(f"Folder '{folder_name_check_ddp}' found and file {file_name_check_html} found in the ZIP file. Seems like a Instagram HTML DDP.")
                    return "invalid_no_json"

                else:

                    print(f"Folder '{folder_name_check_ddp}' found and file {file_name_check_html} not found in the ZIP file. Seems like a real Instagram JSON DDP.")
                    return "valid"

            else:

                print(f"Folder '{folder_name_check_ddp}' not found. Does not seem like an Instagram DDP.")
                return "invalid_no_ddp"
    
    except zipfile.BadZipFile:

        print("Invalid ZIP file.")
        return "invalid_file_zip"

    except Exception as e:

        print(f"An error occurred: {e}")
        return "invalid_file_error"

############################
# Extraction scripts
############################

# Main function to process zip files
def extract_data(filename): 
    """takes zip folder, extracts relevant json file contents, then extracts & processes relevant information and returns them as dataframes"""
    
    # Check if and how many faces are in pictures
    picture_info = check_faces_in_zip(filename)

    data = []

    for file, v in extraction_dict.items():

        # Extract json from file name based on "key"
        file_json = extractJsonContentFromZipFolder(filename, file)

        if file_json is not None:
            
            try:
                # Call the "value" extraction function
                if "picture_info" in v:  # Check if picture_info is required for this extraction function
                    file_json_df = v["extraction_function"](file_json, picture_info)
                else:
                    file_json_df = v["extraction_function"](file_json)

            except Exception as e:
                # if it fails for some reason
                file_json_df = pd.DataFrame([f"extraction_failed__{file, type(e).__name__}"], columns=[str(file)])

        else:      
            
            file_json_df = pd.DataFrame(["file_does_not_exist"], columns=[str(file)])
        
        data.append(file_json_df)

    return data

# Count faces for each picture
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

# Exract json content from given file
def extractJsonContentFromZipFolder(zip_file_path, pattern):

    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:

        # Get the list of file names in the zip file
        file_names = zip_ref.namelist()
        
        file_json_dict = {}

        for file_name in file_names:
            if (file_name.endswith('.json')) and (pattern in file_name):

                try:
                    # Read the JSON file into a dictionary
                    with zip_ref.open(file_name) as json_file:
                        json_content = json_file.read()
                        data = json.loads(json_content)
                        file_json_dict[file_name] = data

                    break

                except:
                    
                    return None
            
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

    print(meta_data)

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
