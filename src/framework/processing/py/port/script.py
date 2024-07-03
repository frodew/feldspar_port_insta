import port.api.props as props
from port.api.commands import CommandSystemDonate, CommandSystemExit, CommandUIRender

from port.extraction_functions import *
from port.extraction_functions_dict import extraction_dict

import zipfile
import cv2
from PIL import Image
import numpy as np
import pandas as pd
import time
import json

############################
# MAIN FUNCTION INITIATING THE DONATION PROCESS
############################


def process(sessionId):
    key = "instagram-data-donation"
    meta_data = []
    meta_data.append(("debug", f"{key}: start"))

    # STEP 1: Select DDP and extract automatically required data

    data = None

    while True:
        meta_data.append(("debug", f"{key}: prompt file"))

        # Allow users to only upload zip-files and render file-input page
        promptFile = prompt_file("application/zip")
        fileResult = yield render_donation_page(promptFile)

        # If user input
        if fileResult.__type__ == "PayloadString":
            check_ddp = check_if_valid_instagram_ddp(fileResult.value)

            if check_ddp == "valid":
                meta_data.append(("debug", f"{key}: extracting file"))

                # Automatically extract required data
                extract_gen = extract_data(fileResult.value)

                while True:
                    try:
                        # Get the next progress update from the generator
                        message, percentage, data = next(extract_gen)
                        # Create a progress message for the UI
                        promptMessage = prompt_extraction_message(message, percentage)
                        # Render the progress page
                        yield render_donation_page(promptMessage)
                    except StopIteration:
                        # The generator is exhausted, break the loop
                        break

                meta_data.append(
                    ("debug", f"{key}: extraction successful, go to consent form")
                )
                break

            elif check_ddp == "invalid_no_json":
                meta_data.append(
                    (
                        "debug",
                        f"{key}: prompt confirmation to retry file selection (invalid_no_json)",
                    )
                )
                retry_result = yield render_donation_page(retry_confirmation_no_json())

                if retry_result.__type__ == "PayloadTrue":
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue

            elif check_ddp == "invalid_no_ddp":
                meta_data.append(
                    (
                        "debug",
                        f"{key}: prompt confirmation to retry file selection (invalid_no_ddp)",
                    )
                )
                retry_result = yield render_donation_page(retry_confirmation_no_ddp())

                if retry_result.__type__ == "PayloadTrue":
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue

            else:
                meta_data.append(
                    (
                        "debug",
                        f"{key}: prompt confirmation to retry file selection (invalid_file)",
                    )
                )
                print(check_ddp)
                retry_result = yield render_donation_page(retry_confirmation_no_ddp())

                if retry_result.__type__ == "PayloadTrue":
                    meta_data.append(("debug", f"{key}: retry prompt file"))
                    continue

    # STEP 2: Present user their extracted data and ask for consent

    meta_data.append(("debug", f"{key}: prompt consent"))
    # Render donation page with extracted data
    prompt = prompt_consent(data, meta_data)
    consent_result = yield render_donation_page(prompt)

    # Send data if consent
    if consent_result.__type__ == "PayloadJSON":
        meta_data.append(("debug", f"{key}: donate consent data"))
        yield donate(f"{sessionId}-{key}", consent_result.value)

    # Send no data if no consent
    if consent_result.__type__ == "PayloadFalse":
        value = json.dumps('{"status" : "donation declined"}')
        yield donate(f"{sessionId}-{key}", value)


############################
# Render pages used in step 1
############################


def prompt_file(extensions):
    description = props.Translatable(
        {
            "en": 'Please select your Instagram data file. The downloaded file should be named like "instagram-USERNAME-DATE-...-.zip". Make sure it is a zip file.\nThe data processing can take up to a minute. Please do NOT reload the page during this process.',
            "de": 'Wählen Sie Ihre heruntergeladene Instagram-Datei aus. Die heruntergeladene Datei sollte etwa so heißen: "instagram-NUTZERNAME-DATUM-...-.zip".\nDas Verarbeiten der Datei kann bis zu einer Minute dauern. Bitte aktualisieren Sie diese Seite währenddessen NICHT.',
            "nl": "Selecteer een willekeurige zip file die u heeft opgeslagen op uw apparaat.",
        }
    )

    return props.PropsUIPromptFileInput(description, extensions)


def render_donation_page(body):
    platform = "Instagram"

    header = props.PropsUIHeader(
        props.Translatable(
            {
                "en": "Instagram Data Donation",
                "de": "Instagram Datenspende",
                "nl": "Instagram Data Donation",
            }
        )
    )

    page = props.PropsUIPageDonation(platform, header, body)
    return CommandUIRender(page)


def retry_confirmation_no_json():
    text = props.Translatable(
        {
            "en": 'Unfortunately, we cannot process your file. It seems like you submitted a HTML file of your Instagram data.\nPlease download your data from Instagram again and select the data format "JSON".\n The downloaded file should be named like "instagram-USERNAME-DATE-...-.zip". Make sure it is a zip file.',
            "de": 'Leider können wir Ihre Datei nicht verarbeiten. Es scheint so, dass Sie aus Versehen die HTML-Version beantragt haben.\nBitte beantragen Sie erneut eine Datenspende bei Instagram und wählen Sie dabei "JSON" als Dateivormat aus (wie in der Anleitung beschrieben).\nDie heruntergeladene Datei sollte etwa so heißen: "instagram-NUTZERNAME-DATUM-...-.zip".',
            "nl": "Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen.",
        }
    )

    ok = props.Translatable(
        {
            "en": "Try again with JSON file",
            "de": "Erneut versuchen mit JSON-Datei",
            "nl": "Probeer opnieuw",
        }
    )

    return props.PropsUIPromptConfirm(text, ok)


def retry_confirmation_no_ddp():
    text = props.Translatable(
        {
            "en": 'Unfortunately, we cannot process your file. Did you really select your downloaded Instagram ZIP file?\nThe downloades file should be named like "instagram-USERNAME-DATE-...-.zip". Make sure it is a zip file.',
            "de": 'Leider können wir Ihre Datei nicht verarbeiten. Haben Sie wirklich Ihre Instagram-Datei ausgewählt?\nDie heruntergeladene Datei sollte etwa so heißen: "instagram-NUTZERNAME-DATUM-...-.zip".',
            "nl": "Helaas, kunnen we uw bestand niet verwerken. Weet u zeker dat u het juiste bestand heeft gekozen? Ga dan verder. Probeer opnieuw als u een ander bestand wilt kiezen.",
        }
    )

    ok = props.Translatable(
        {"en": "Try again", "de": "Erneut versuchen", "nl": "Probeer opnieuw"}
    )

    return props.PropsUIPromptConfirm(text, ok)


def check_if_valid_instagram_ddp(filename):
    folder_name_check_ddp = "ads_information"
    file_name_check_html = "start_here.html"

    try:
        with zipfile.ZipFile(filename, "r") as zip_ref:
            found_folder_name_check_ddp = False
            found_file_name_check_html = False

            for file_info in zip_ref.infolist():
                if folder_name_check_ddp in file_info.filename:
                    found_folder_name_check_ddp = True

                elif file_name_check_html in file_info.filename:
                    found_file_name_check_html = True

            if found_folder_name_check_ddp:
                if found_file_name_check_html:
                    print(
                        f"Folder '{folder_name_check_ddp}' found and file {file_name_check_html} found in the ZIP file. Seems like a Instagram HTML DDP."
                    )
                    return "invalid_no_json"

                else:
                    print(
                        f"Folder '{folder_name_check_ddp}' found and file {file_name_check_html} not found in the ZIP file. Seems like a real Instagram JSON DDP."
                    )
                    return "valid"

            else:
                print(
                    f"Folder '{folder_name_check_ddp}' not found. Does not seem like an Instagram DDP."
                )
                return "invalid_no_ddp"

    except zipfile.BadZipFile:
        print("Invalid ZIP file.")
        return "invalid_file_zip"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "invalid_file_error"


def prompt_extraction_message(message, percentage):
    description = props.Translatable(
        {
            "en": "One moment please. Information is now being extracted from the selected file.",
            "de": "Einen Moment bitte. Es werden nun Informationen aus der ausgewählten Datei extrahiert.",
            "nl": "Een moment geduld. Informatie wordt op dit moment uit het geselecteerde bestaand gehaald.",
        }
    )
    return props.PropsUIPromptProgress(description, message, percentage)


############################
# Extraction scripts
############################


# Main function to process zip files
def extract_data(filename):
    """takes zip folder, extracts relevant json file contents, then extracts & processes relevant information and returns them as dataframes"""

    data = []

    # Check if and how many faces are in pictures
    picture_info = {}
    face_gen = check_faces_in_zip(filename)

    # Generator to check if faces in picture, which also updates the progress bar
    for message, percentage, face_dict in face_gen:
        picture_info = face_dict
        yield message, percentage, data

    for index, (file, v) in enumerate(extraction_dict.items(), start=1):
        # Extract json from file name based on "key"
        file_json = extractJsonContentFromZipFolder(filename, file)

        if file_json is not None:
            try:
                # Call the "value" extraction function
                if (
                    "picture_info" in v
                ):  # Check if picture_info is required for this extraction function
                    file_json_df = v["extraction_function"](file_json, picture_info)
                else:
                    file_json_df = v["extraction_function"](file_json)

            except Exception as e:
                # if it fails for some reason
                file_json_df = pd.DataFrame(
                    [f"extraction_failed__{file, type(e).__name__}"],
                    columns=[str(file)],
                )

        else:
            file_json_df = pd.DataFrame(["file_does_not_exist"], columns=[str(file)])

        data.append(file_json_df)

        # Yield progress update
        yield f"Extracting data from {file}", (index / len(extraction_dict)) * 100, data

    # Yield final progress update and the extracted data
    yield "Extracting of data completed", 100, data


# Count faces for each picture
def check_faces_in_zip(filename):
    """This function checks the number of faces in each image file within a zip file."""

    face_dict = {}

    # Load face cascade classifier
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Set the desired size for the images
    size = 200, 200

    # Open the zip file in read mode
    with zipfile.ZipFile(filename, "r") as zip_ref:
        # Iterate through each file in the zip file
        for index, file in enumerate(zip_ref.namelist(), start=1):
            # Check if the file is a jpg image and in the media folder
            if file.lower().endswith(".jpg") and file.lower().startswith("media"):
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
                    faces = face_cascade.detectMultiScale(
                        img_down_np, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30)
                    )

                    end_time = time.time()  # Record end time
                    processing_time = end_time - start_time  # Calculate processing time
                    print(
                        "PLI - Processing time for {}: {:.2f} seconds".format(
                            file, processing_time
                        )
                    )

                    # Count faces in picture
                    face_dict[file] = len(faces)

            percentage = (index / len(zip_ref.namelist())) * 100
            yield f"Checking faces in image {file}", percentage, face_dict

    # Return the dictionary containing the number of faces in each image
    yield "Checking faces in images completed", 100, face_dict


# Exract json content from given file
def extractJsonContentFromZipFolder(zip_file_path, pattern):
    with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
        # Get the list of file names in the zip file
        file_names = zip_ref.namelist()

        file_json_dict = {}

        for file_name in file_names:
            if (file_name.endswith(".json")) and (pattern in file_name):
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

    # Initialize a list to store binary data (title and value pairs)
    binary_data = []

    if data is not None:  # can happen if user submits wrong file and still continues
        for file, v in extraction_dict.items():
            df = data[i]

            # Check if the dataframe has only one row
            if len(df) == 1:
                # Extract the title from the 'en' translation
                translated_title = v["title"]["en"]
                # Combine values from all columns into a single string
                combined_value = " || ".join(
                    [f"{col}: {df.iloc[0][col]}" for col in df.columns]
                )
                binary_data.append([translated_title, combined_value])
            else:
                # Directly add multi-row dataframes to the table list
                table = props.PropsUIPromptConsentFormTable(
                    file, props.Translatable(v["title"]), df
                )
                table_list.append(table)

            i += 1

        # Create a dataframe for binary data if there are any single-row entries
        if binary_data:
            binary_df = pd.DataFrame(binary_data, columns=["Information", "Wert"])
            table = props.PropsUIPromptConsentFormTable(
                "binary_results",
                props.Translatable(
                    {
                        "en": "Overview of additional data",
                        "de": "Hier sind einige Ihrer Daten zusammengefasst",
                        "nl": "Binary data",
                    }
                ),
                binary_df,
            )
            table_list.append(table)
    return props.PropsUIPromptConsentForm(table_list, [])


# pass on user decision to donate or decline donation
def donate(key, json_string):
    return CommandSystemDonate(key, json_string)
