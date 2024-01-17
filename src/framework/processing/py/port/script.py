import port.api.props as props
from port.api.assets import *
from port.api.commands import (CommandSystemDonate, CommandSystemExit, CommandUIRender)

from datetime import datetime, timezone, timedelta
import zipfile
#from ddpinspect import instagram

import pandas as pd
import json


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
            meta_data.append(("debug", f"{key}: extracting file"))
            extractionResult = doSomethingWithTheFile(fileResult.value)
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
        "nl": "Port voorbeeld flow"
    }))

    page = props.PropsUIPageDonation("Zip", header, body)
    return CommandUIRender(page)


def retry_confirmation():
    text = props.Translatable({
        "en": "Unfortunately, we cannot process your file. Continue, if you are sure that you selected the right file. Try again to select a different file.",
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


def prompt_file(extensions):
    description = props.Translatable({
        "en": "Please select any zip file stored on your device.",
        "nl": "Selecteer een willekeurige zip file die u heeft opgeslagen op uw apparaat."
    })

    return props.PropsUIPromptFileInput(description, extensions)

#main function to process zip files




def doSomethingWithTheFile(filename): 
    """takes zip folder, extracts relevant json file contents (your_topics, posts_viewed, videos_watched), then extracts & processes relevant information and returns them as dataframes"""

    data = []

    for file, v in extraction_dict.items():
        
        target_file = extractJsonContentFromZipFolder(filename, file)

        try:
            target_df = v["extraction_function"](target_file)
        
        except:
            target_df = pd.DataFrame(["Empty"], columns=[str(file)])
        
        data.append(target_df)


    return data


#main content of consent page: displays all data in donation

def prompt_consent(data, meta_data):

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





def epoch_to_date(epoch_timestamp: str | int) -> str: #thanks ddp-inspector/ddpinspect/src/parserlib/stringparse.py
    """
    Convert epoch timestamp to an ISO 8601 string. Assumes UTC. -> UTC +1

    If timestamp cannot be converted raise CannotConvertEpochTimestamp
    """
    try:
        epoch_timestamp = int(epoch_timestamp)
        out = datetime.fromtimestamp(epoch_timestamp, tz=timezone(timedelta(hours=1))).isoformat() # timezone = utc + 1
    except (OverflowError, OSError, ValueError, TypeError) as e:
        logger.error("Could not convert epoch time timestamp, %s", e)
        raise CannotConvertEpochTimestamp("Cannot convert epoch timestamp") from e

    out = pd.to_datetime(out)
    return str(out.date()) # convertion to string for display in browser


# 3 ads_and_topics/ads_clicked -> list of product names per day
def extract_ads_clicked(ads_clicked_dict):
    """extract list of product names per day from ads_and_topics/ads_clicked"""

    timestamps = [t['string_list_data'][0]['timestamp'] for t in ads_clicked_dict['impressions_history_ads_clicked']] # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps] # convert epochs to dates
    products = [i["title"] for i in ads_clicked_dict['impressions_history_ads_clicked']]
    
    adds_clicked_df = pd.DataFrame(
        {"date": dates,
        "ads_clicked": products}
    )
    aggregated_df = adds_clicked_df.groupby('date')['ads_clicked'].agg(list).reset_index()
    return aggregated_df

# 4 ads_and_topics/ads_viewed -> list of authors per day
def extract_ads_viewed(ads_viewed_dict):
    """extract list of authors per day from ads_and_topics/ads_viewed"""


    timestamps = [t['string_map_data']["Time"]['timestamp'] for t in ads_viewed_dict['impressions_history_ads_seen']] # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps] # convert epochs to dates
    authors = [i["string_map_data"]["Author"]["value"] for i in ads_viewed_dict['impressions_history_ads_seen']]
    
    adds_viewed_df = pd.DataFrame(
        {"date": dates,
        "authors_seen": authors}
    )
    aggregated_df = adds_viewed_df.groupby('date')['authors_seen'].agg(list).reset_index()
    return aggregated_df

# 5 ads_and_topics/posts_viewed -> count per day
# probably want to restrict the days to those within the study period?
def get_postViewsPerDay(posts_viewed_dict):
    """takes content of posts_viewed json file and returns dataframe with number of viewed posts/day"""
    timestamps = [t['string_map_data']['Time']['timestamp'] for t in posts_viewed_dict['impressions_history_posts_seen']] # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps] # convert epochs to dates
    postViewedDates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = postViewedDates_df.groupby(["date"])["date"].size() # count number of rows per day
    return aggregated_df.reset_index(name='postsViewed_count')

# 8 ads_and_topics/videos_watched -> count per day
# maybe combine results from get_postViewsPerDay and get_videoViewsPerDay in one dataframe? columns:  date | postsViewed_count | videosViewed_count
def get_videoViewsPerDay(videos_watched_dict):
    """takes content of videos_watched json file and returns dataframe with number of viewed posts/day"""
    timestamps = [t['string_map_data']['Time']['timestamp'] for t in videos_watched_dict["impressions_history_videos_watched"]] # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps] # convert epochs to dates
    videosViewedDates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = videosViewedDates_df.groupby(["date"])["date"].size() # count number of rows per day
    return aggregated_df.reset_index(name='videosViewed_count')

# 11 instagram_ads_and_businesses/subscription_for_no_ads -> dummy whether user has such a subscription
def extract_subscription_for_no_ads(subscription_for_no_ads_dict):
    """return whether user has subscription for ad-free usage"""
    
    addfree_subscription = (subscription_for_no_ads_dict != None)
    return pd.DataFrame([addfree_subscription], columns=['adfree_substription'])


# 15 followers_and_following/blocked_accounts -> count
# so far no example file...
def extract_blocked_accounts(blocked_accounts_dict):
    """extract count of blocked accounts"""
    
    if blocked_accounts_dict == None:
        count = 0
    else:
        count = "Empty" # include extraction from existing file here!!
    return pd.DataFrame([count], columns=['blocked_accounts_count'])

# 16 followers_and_following/close_friends -> count
def extract_close_friends(close_friends_dict):
    """extract count of close friends"""
    if close_friends_dict == None:
        count = 0
    else:
        friends = [f for f in close_friends_dict["relationships_close_friends"]]
        count = len(friends)

    return pd.DataFrame([count], columns=['close_friends_count'])

# 17 followers_and_following/followers_1 -> count
def extract_followers_1(followers_1_dict):
    """extract count of followers"""

    if followers_1_dict == None:
        count = 0

    else:
        count = len(followers_1_dict)
    return pd.DataFrame([count], columns=['followers_count'])

# 18 followers_and_following/following -> count
def extract_following(following_dict):
    """extract count of accounts person is following"""
    if following_dict == None:
        count = 0
    else:
        following = [f for f in following_dict["relationships_following"]]
        count = len(following)

    return pd.DataFrame([count], columns=['following_count'])

# 19 followers_and_following/follow_requests_you've_received -> count
def extract_follow_requests_youve_received(follow_requests_youve_received_dict):
    """extract count of received follow requests"""
    if follow_requests_youve_received_dict == None:
        count = 0
    else:
        requests = [f for f in follow_requests_youve_received_dict["relationships_follow_requests_received"]]
        count = len(requests)

    return pd.DataFrame([count], columns=['received_follow_requests_count'])

# 20 followers_and_following/hide_story_from -> count
# no example file!
def extract_hide_story_from(hide_story_from_dict):
    """extract count of accounts story is hidden from"""

    if hide_story_from_dict == None:
        count = 0
    else:
        count = "Empty" # include extraction from existing file here!!
    return pd.DataFrame([count], columns=['hide_story_from_count'])

# 21 followers_and_following/pending_follow_requests -> count
def extract_pending_follow_requests(pending_follow_requests_dict):
    """extract count of pending follow requests"""
    if pending_follow_requests_dict == None:
        count = 0
    else:
        pending = [f for f in pending_follow_requests_dict["relationships_follow_requests_sent"]]
        count = len(pending)
    return pd.DataFrame([count], columns=['pending_follow_requests_count'])

# 23 followers_and_following/recently_unfollowed_accounts -> count
# no example file!
def extract_recently_unfollowed_accounts(recently_unfollowed_accounts_dict):
    """extract count of recently unfollowed accounts"""
    if recently_unfollowed_accounts_dict == None:
        count = 0
    else:
        count = "Empty" # include extraction from existing file here!!
    return pd.DataFrame([count], columns=['recently_unfollowed_accounts_count'])

# 24 followers_and_following/removed_suggestions -> count
def extract_removed_suggestions(removed_suggestions_dict):
    """extract count of removed suggestions"""
    if removed_suggestions_dict == None:
        suggestions = 0 # assume there are no suggestions if file doesnt exist
    else:
        suggestions = len([f for f in removed_suggestions_dict["relationships_dismissed_suggested_users"]])
    return pd.DataFrame([suggestions], columns=['removed_suggestions_count'])

# 25 followers_and_following/restricted_accounts -> count
# no example file!
def extract_restricted_accounts(restricted_accounts_dict):
    """extract count of restricted accounts"""
    if restricted_accounts_dict == None:
        count = 0
    else:
        count = "Empty" # include extraction from existing file here!!
    return pd.DataFrame([count], columns=['restricted_accounts_count'])

# 47 your_topics -> topics list
def extract_topics_df(topics_dict):
    """takes the content of your_topics jsonfile, extracts topics and returns them as a dataframe"""
    
    topics_list = [t['string_map_data']['Name']['value'] for t in topics_dict['topics_your_topics']]
    topics_df = pd.DataFrame(topics_list, columns=['your_topics'])
    return topics_df

extraction_dict = {
    "ads_clicked": {
        "extraction_function": extract_ads_clicked,
        "title": {
            "en": "Product names (ads) clicked per day", 
            "nl": "Inhoud zip bestand"
        }
    }, 
    "ads_viewed": {
        "extraction_function": extract_ads_viewed,
        "title": {
            "en": "Clicked ads' authors per day", 
            "nl": "Inhoud zip bestand"
        }
    },
    "posts_viewed": {
        "extraction_function": get_postViewsPerDay,
        "title": {
            "en": "Number of posts viewed each day in the last week",
            "nl": "Inhoud zip bestand"
        }
    },
    "videos_watched": {
        "extraction_function": get_videoViewsPerDay, 
        "title": {
            "en": "Number of videos watched each day in the last week",
            "nl": "Inhoud zip bestand"
        }
    },
    "subscription_for_no_ads": {
        "extraction_function": extract_subscription_for_no_ads,
        "title": {
            "en": "Ad-free subscription?", 
            "nl": "Inhoud zip bestand"
        }
    },
    "blocked_accounts": {
        "extraction_function": extract_blocked_accounts,
        "title": {
            "en": "Number of accounts you have blocked",
            "nl": "Inhoud zip bestand"
            }
    },
    "close_friends": {
        "extraction_function": extract_close_friends,
        "title": {
            "en": "Number of close friends",
            "nl": "Inhoud zip bestand"
            }
    },
    "followers_1": {
        "extraction_function": extract_followers_1,
        "title": {
            "en": "Number of followers",
            "nl": "Inhoud zip bestand"
            }
    },
    "followers_and_following/following": {
        "extraction_function": extract_following,
        "title": {
            "en": "Number of accounts you are following",
            "nl": "Inhoud zip bestand"
            }
    },
    "follow_requests_you've_received": {
        "extraction_function": extract_follow_requests_youve_received,
        "title": {
            "en": "Number of follow requests you have received",
            "nl": "Inhoud zip bestand"
            }
    },
    "hide_story_from": {
        "extraction_function": extract_hide_story_from,
        "title": {
            "en": "Number of account you have hidden your story from",
            "nl": "Inhoud zip bestand"
            }
    },
    "pending_follow_requests": {
        "extraction_function": extract_pending_follow_requests,
        "title": {
            "en": "Number of your pending follow requests",
            "nl": "Inhoud zip bestand"
            }
    },
    "recently_unfollowed_accounts": {
        "extraction_function": extract_recently_unfollowed_accounts,
        "title": {
            "en": "Number of accounts you recently unfollowed",
            "nl": "Inhoud zip bestand"
            }
    },
    "removed_suggestions": {
        "extraction_function": extract_removed_suggestions,
        "title": {
            "en": "Number of accounts that you've removed from your suggestions",
            "nl": "Inhoud zip bestand"
            }
    },
    "restricted_accounts": {
        "extraction_function": extract_restricted_accounts,
        "title": {
            "en": "Number of accounts that you've restricted",
            "nl": "Inhoud zip bestand"
            }
    },
    "your_topics": {
        "extraction_function": extract_topics_df,
        "title": {
            "en": "Your Topics inferred by Instagram",
            "nl": "Inhoud zip bestand"
            }
    }
}

# unedited from PORT, best leave like that :)

def donate(key, json_string):
    return CommandSystemDonate(key, json_string)


def exit(code, info):
    return CommandSystemExit(code, info)
