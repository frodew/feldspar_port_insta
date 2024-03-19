import pandas as pd
from datetime import datetime, timezone, timedelta
import re

# helper functions -----------------------------

def epoch_to_date(epoch_timestamp: str | int) -> str: #thanks ddp-inspector/ddpinspect/src/parserlib/stringparse.py
    """
    Convert epoch timestamp to an ISO 8601 string. Assumes UTC +1

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


# extraction functions --------------------------

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

    timestamps = [t['string_map_data']["Time"]['timestamp'] for t in ads_viewed_dict['impressions_history_ads_seen']] # get list with timestamps in epoch format (if author exists)
    dates = [epoch_to_date(t) for t in timestamps] # convert epochs to dates
    authors = [i["string_map_data"]["Author"]["value"] if "Author" in i["string_map_data"] else "unknownAuthor" for i in ads_viewed_dict['impressions_history_ads_seen'] ] # not for all viewed ads there is an author!
    
    adds_viewed_df = pd.DataFrame(
        {"date": dates,
        "authors_seen": authors}
    )
    aggregated_df = adds_viewed_df.groupby('date')['authors_seen'].agg(list).reset_index()

    return aggregated_df


    

# 5 ads_and_topics/posts_viewed -> count per day
def get_postViewsPerDay(posts_viewed_dict):
    """takes content of posts_viewed json file and returns dataframe with number of viewed posts/day"""
    timestamps = [t['string_map_data']['Time']['timestamp'] for t in posts_viewed_dict['impressions_history_posts_seen']] # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps] # convert epochs to dates
    postViewedDates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = postViewedDates_df.groupby(["date"])["date"].size() # count number of rows per day
    return aggregated_df.reset_index(name='postsViewed_count')

# 8 ads_and_topics/videos_watched -> count per day
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
    
    value = None # return None if key isnt known

    if subscription_for_no_ads_dict["label_values"][0]["value"] == "Inaktiv":
        value = False
    else:
        value = True

    return pd.DataFrame([value], columns=['adfree_subscription'])

# 15 followers_and_following/blocked_accounts -> count per day
def extract_blocked_accounts(blocked_accounts_dict):
    """extract count of blocked accounts per day"""
   
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in blocked_accounts_dict["relationships_blocked_users"]]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='blocked_accounts_count')

# 16 followers_and_following/close_friends -> count per day
def extract_close_friends(close_friends_dict):
    """extract count of close friends per day"""

    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in close_friends_dict["relationships_close_friends"]]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='close_friends_count') 

# 17 followers_and_following/followers_1 -> count per day
def extract_followers_1(followers_1_dict):
    """extract count of followers per day"""

    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in followers_1_dict]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='followers_dict')

# 18 followers_and_following/following -> count
def extract_following(following_dict):
    """extract count of accounts person is following"""
    if following_dict == None:
        count = 0
    else:
        following = [f for f in following_dict["relationships_following"]]
        count = len(following)

    return pd.DataFrame([count], columns=['following_count'])


# 19 followers_and_following/follow_requests_you've_received -> count per day
def extract_follow_requests_youve_received(follow_requests_youve_received_dict):
    """extract count of received follow requests per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in follow_requests_youve_received_dict["relationships_follow_requests_received"]]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='received_follow_requests_count')

# 20 followers_and_following/hide_story_from -> count per day
def extract_hide_story_from(hide_story_from_dict):
    """extract count of accounts story is hidden from per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in hide_story_from_dict["relationships_hide_stories_from"]]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='hide_story_from_count')

# 21 followers_and_following/pending_follow_requests -> count per day
def extract_pending_follow_requests(pending_follow_requests_dict):
    """extract count of pending follow requests per day"""

    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in pending_follow_requests_dict['relationships_follow_requests_sent']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='pending_follow_requests_count')

# 23 followers_and_following/recently_unfollowed_accounts -> count per day
def extract_recently_unfollowed_accounts(recently_unfollowed_accounts_dict):
    """extract count of recently unfollowed accounts per day"""

    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in recently_unfollowed_accounts_dict["relationships_unfollowed_users"]]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='recently_unfollowed_accounts_count')

# 24 followers_and_following/removed_suggestions -> count per day
def extract_removed_suggestions(removed_suggestions_dict):
    """extract count of removed suggestions per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in removed_suggestions_dict["relationships_dismissed_suggested_users"]]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='removed_suggestions_count') 

# 25 followers_and_following/restricted_accounts -> count per day
def extract_restricted_accounts(restricted_accounts_dict):
    """extract count of restricted accounts per day"""

    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in restricted_accounts_dict["relationships_restricted_users"]]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='restricted_accounts_count')

# 28 policy_updates_and_permissions/notification_of_privacy_policy_updates-> day and value
def extract_notification_of_privacy_policy_updates(notification_of_privacy_policy_updates_dict):
    """extract day of when you've viewed updates to the Meta Privacy Polic and consent status"""

    # extract and preprocess dates
    dates = [d["string_map_data"]["Impression Time"]["value"] for d in notification_of_privacy_policy_updates_dict["policy_updates_and_permissions_notification_of_privacy_policy_updates"]]
    dates = [datetime.strptime(d, '%b %d, %Y %I:%M:%S%p') for d in dates] 
    dates = [d.strftime('%Y-%m-%d') for d in dates] # use same format as in other tables

    consent_statuses = [v["string_map_data"]["Consent Status"]["value"] for v in notification_of_privacy_policy_updates_dict["policy_updates_and_permissions_notification_of_privacy_policy_updates"]]

    result = pd.DataFrame(
        {"date": dates,
        "consent_status": consent_statuses}
    )
    
    return result


# 37 personal_information/account_information.json -> dummy whether contact syncing enabled
def extract_account_information(account_information_dict):
    """extract dummy whether contact syncing is enabled"""

    value = None # return None if key isnt known

    for k in ['Contact Syncing', 'Kontaktsynchronisierung', "Synchronisation des contacts"]: # keys are language specific
        if k in account_information_dict["profile_account_insights"][0]["string_map_data"]:
            value = account_information_dict["profile_account_insights"][0]["string_map_data"][k]["value"]
            break  

    return pd.DataFrame([value], columns=['contact_syncing_enabled'])


# 41 personal_information/personal_information.json -> dummies whether user has profile image, email, phone, and private account
def extract_personal_information(personal_information_dict):
    """extract dummies whether user has profile image, email, phone, and private account"""

    
    profile_image, email, phone, private_account = None, None, None, None # return None if key isnt known
        
    for k in ['Profile Photo', 'Profilbild']: # keys are language specific
        if k in personal_information_dict["profile_user"][0]["media_map_data"]:
            profile_image = personal_information_dict["profile_user"][0]["media_map_data"][k]["uri"] != "False"
            break  

    for k in ['Email', 'E-Mail-Adresse']: # keys are language specific
        if k in personal_information_dict["profile_user"][0]['string_map_data']:
            email = personal_information_dict["profile_user"][0]['string_map_data'][k]['value'] !=False
            break 

    for k in ['Phone Confirmed', 'Telefonnummer bestätigt']: # keys are language specific
        if k in personal_information_dict["profile_user"][0]['string_map_data']:
            phone = personal_information_dict["profile_user"][0]['string_map_data'][k]['value'] != "False"
            break  

    for k in ['Private Account', 'Privates Konto']: # keys are language specific
        if k in personal_information_dict["profile_user"][0]['string_map_data']:
            private_account = personal_information_dict["profile_user"][0]['string_map_data'][k]['value']
            break         

    """extract used name and compare to list if real name"""
    
    name_to_check = None 
    real_name = False

    for k in ['Name']: # keys are language specific
        if k in personal_information_dict["profile_user"][0]['string_map_data']:
            name_to_check = personal_information_dict["profile_user"][0]['string_map_data'][k]['value']
            break 
 
    
    #split name at whitespace, dot, or underscore
    def split_name(name):
        parts = re.split(r'[\s._]+', name)
        parts = [part.strip() for part in parts if part.strip()]
        return parts
    
    names_to_check = split_name(name_to_check)
    
    def check_name(names_to_check):
        with open("vornamen.txt", "r") as file:
            # Read the names from the file and create a set
            names_set = {line.strip() for line in file}
        
        # Check if any name in names_to_check matches the names in the file
        for name in names_to_check:
            if name in names_set:
                return True  # Return True if any match is found
            
        return False  # Return False if no match is found

    real_name = check_name(names_to_check)

    result =pd.DataFrame(
                {"profile_image": [profile_image],
                "email": [email], 
                "phone": [phone], 
                "private_account": [private_account],
                "real_name_in_use": [real_name]
                 })

    return result


# 43 personal_information/profile_changes 43 -> day and what was changed
def extract_profile_changes(profile_changes_dict):
    """extract day and what was changed"""

    changes = [t["string_map_data"] for t in profile_changes_dict['profile_profile_change']]

    for k in ["Changed", "Ge\u00c3\u00a4ndert"]: # keys are language specific
        if any(k in d for d in changes):
            changed_values = [t[k]['value'] for t in changes]
            break

    for k in ["Change Date", "Datum \u00c3\u00a4ndern"]: # keys are language specific
        if any(k in d for d in changes):
            changed_dates = [epoch_to_date(t[k]['timestamp']) for t in changes]
            break

    changes_df = pd.DataFrame(
        {
            "date": changed_dates,
            "changes_made": changed_values
        })
    
    return changes_df


# 44 comments_allowed_from -> value
def extract_comments_allowed_from(comments_allowed_from_dict):
    """extract who can comment"""
    
    for k in ["Comments Allowed From", "Kommentieren gestattet fÃ¼r"]: # keys are language specific
        if k in comments_allowed_from_dict['settings_allow_comments_from'][0]["string_map_data"]:
            value = comments_allowed_from_dict['settings_allow_comments_from'][0]["string_map_data"][k]["value"]
            break  

    return pd.DataFrame([value], columns=['comments_allowed_from'])

# 45 comments_blocked_from -> count
def extract_comments_blocked_from(comments_blocked_from_dict):
    """extract count of blocked users from comment"""
    if comments_blocked_from_dict == None:
        count = 0
    else:
        count = len([f for f in comments_blocked_from_dict["settings_blocked_commenters"]])
    return pd.DataFrame([count], columns=['comments_blocked_from'])


# 47 your_topics -> topics list
def extract_topics_df(topics_dict):
    """takes the content of your_topics jsonfile, extracts topics and returns them as a dataframe"""
    
    topics_list = [t['string_map_data']['Name']['value'] for t in topics_dict['topics_your_topics']]
    topics_df = pd.DataFrame(topics_list, columns=['your_topics'])
    return topics_df


# 48 account_privacy_changes -> day and change to account type
def extract_account_privacy_changes(account_privacy_changes_dict):
    """extract """
    
    changes = [c for c in account_privacy_changes_dict["account_history_account_privacy_history"]]
    titles = [t['title'] for t in changes]
    timestamps = []

    for c in changes:
        for k in ['Time', 'Zeit']:
            if k in c["string_map_data"]:
                timestamp = c["string_map_data"][k]['timestamp']
                timestamps.append(epoch_to_date(timestamp))
                break
        
    changes_df = pd.DataFrame(
        {"date": timestamps,
        "change_account_type": titles}
    )        

    aggregated_df = changes_df.groupby('date')['change_account_type'].agg(list).reset_index()
    
    return aggregated_df


# 51 login_activity -> time and user agent
def extract_login_activity(login_activity_dict):
    """extract time and user agent of login"""
    logins = login_activity_dict['account_history_login_history']
    
    timestamps = [l["title"] for l in logins]
    dates = [str(datetime.fromisoformat(timestamp).date()) for timestamp in timestamps]
    times = [datetime.fromisoformat(timestamp).time() for timestamp in timestamps]

    user_agents = [l["string_map_data"]["User Agent"]["value"] for l in logins]
    
    login_df = pd.DataFrame(
            {"date": dates,
            "time": times,
            "user_agent": user_agents}
        ) 

    return login_df


# 52 logout_activity -> time and user agent
def extract_logout_activity(logout_activity_dict):
    """extract time and user agent of logout"""
    logouts = logout_activity_dict['account_history_logout_history']
    
    timestamps = [l["title"] for l in logouts]
    dates = [str(datetime.fromisoformat(timestamp).date()) for timestamp in timestamps]
    times = [datetime.fromisoformat(timestamp).time() for timestamp in timestamps]

    user_agents = [l["string_map_data"]["User Agent"]["value"] for l in logouts]
    
    logout_df = pd.DataFrame(
            {"date": dates,
            "time": times,
            "user_agent": user_agents}
        ) 

    return logout_df

# 53 signup_information -> dummy if real name is used
def extract_signup_information(signup_information_dict):
    """extract used name and compare to list if real name"""
    
    name_to_check = None 
    real_name = False

    for k in ['Username', 'Benutzername']: # keys are language specific
        if k in signup_information_dict['account_history_registration_info'][0]["string_map_data"]:
            name_to_check = signup_information_dict['account_history_registration_info'][0]["string_map_data"][k]["value"]
            break  
    
    #split name at whitespace, dot, or underscore
    def split_name(name):
        parts = re.split(r'[\s._]+', name)
        parts = [part.strip() for part in parts if part.strip()]
        return parts
    
    names_to_check = split_name(name_to_check)
    
    def check_name(names_to_check):
        with open("vornamen.txt", "r") as file:
            # Read the names from the file and create a set
            names_set = {line.strip() for line in file}
        
        # Check if any name in names_to_check matches the names in the file
        for name in names_to_check:
            if name in names_set:
                return True  # Return True if any match is found
            
        return False  # Return False if no match is found

    real_name = check_name(names_to_check)

    return pd.DataFrame([real_name], columns=['real_name_signup'])

# 55 recently_viewed_items -> list of items
def extract_recently_viewed_items(recently_viewed_items_dict):
    """extract """
    items = recently_viewed_items_dict["checkout_saved_recently_viewed_products"]
    products = [p["string_map_data"]["Product Name"]["value"] for p in items]
    products_df = pd.DataFrame(products, columns=['recently_viewed_items'])
    
    return products_df


# 56 post_comments_1 -> 
def extract_post_comments_1(post_comments_1_dict):
    """extract comments count per day"""
    dates = [epoch_to_date(t["string_map_data"]["Time"]["timestamp"]) for t in post_comments_1_dict]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day
    
    return aggregated_df.reset_index(name='postComments_count')

# 57 reels_comments -> count per day
def extract_reels_comments(reels_comments_dict):
    """extract count of reels comments per day """
    
    dates = [epoch_to_date(t["string_map_data"]["Time"]["timestamp"]) for t in reels_comments_dict['comments_reels_comments']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day
    
    return aggregated_df.reset_index(name='reelsComments_count')

# 58 archived_posts -> count per day
def extract_archived_posts(archived_posts_dict, picture_info):
    """extract archived posts count per day and how often additional info was included"""

    results = []

    for post in archived_posts_dict.get("ig_archived_post_media", []):
        for media in post.get("media", []):
            time = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any("latitude" in exif_data for exif_data in media.get("media_metadata", {}).get("photo_metadata", {}).get("exif_data", []))
            
            # Check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append({
                "time": time,
                "has_location": has_latitude_data,
                "face_visible": face_visible              
            })          

    archived_posts_df = pd.DataFrame(results) 

    return archived_posts_df

# 59 posts_1 -> count per day
def extract_posts_1(posts_1_dict, picture_info):
    """extract posts count per day and how often additional info was included"""

    results = []

    for post in posts_1_dict:
        for media in post.get("media", []):
            time = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any("latitude" in exif_data for exif_data in media.get("media_metadata", {}).get("photo_metadata", {}).get("exif_data", []))
            
            # Check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append({
                "time": time,
                "has_location": has_latitude_data,
                "face_visible": face_visible              
            })          

    posts_df = pd.DataFrame(results) 

    return posts_df

# 60 profile_photos -> dummy if face
def extract_profile_photos(profile_photos_dict, picture_info):
    """extract profile photo info if face is included"""

    uri = profile_photos_dict.get("ig_profile_picture", [])[0].get("uri", "")

    # Check if the URI is in the picture_info dictionary
    face_visible = picture_info.get(uri, False)

    face_in_picture = True if face_visible >=1 else False 

    return pd.DataFrame([face_in_picture], columns=['face_in_picture'])

# 61 recently_deleted_content -> count per day
def extract_recently_deleted_content(recently_deleted_content_dict, picture_info):
    """extract recently deleted posts count per day and how often additional info was included"""

    results = []

    for post in recently_deleted_content_dict.get("ig_recently_deleted_media", []):
        for media in post.get("media", []):
            time = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any("latitude" in exif_data for exif_data in media.get("media_metadata", {}).get("photo_metadata", {}).get("exif_data", []))
            
            # Check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append({
                "time": time,
                "has_location": has_latitude_data,
                "face_visible": face_visible              
            })          

    recently_deleted_content_df = pd.DataFrame(results) 

    return recently_deleted_content_df

# 62 reels -> count per day
def extract_reels(reels_dict):
    """extract count of reels per day """
    
    dates = [epoch_to_date(media.get("creation_timestamp")) for reel in reels_dict.get("ig_reels_media", []) for media in reel.get("media", [])]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day
    
    return aggregated_df.reset_index(name='reels_count')

# 63 stories -> count per day
def extract_stories(stories_dict):
    """extract stories count per day and how often additional info was included"""

    results = []

    for story in stories_dict.get("ig_stories", []):
        time = epoch_to_date(story.get("creation_timestamp", ""))
        has_latitude_data = any("latitude" in exif_data for exif_data in story.get("media_metadata", {}).get("photo_metadata", {}).get("exif_data", []))
            
        results.append({
            "time": time,
            "has_location": has_latitude_data,
        })          

    stories_df = pd.DataFrame(results) 

    return stories_df

# 68 liked_comments -> count per day
def extract_liked_comments(liked_comments_dict):
    """extract count of liked comments per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in liked_comments_dict['likes_comment_likes']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='likedComments_count')


# 69 liked_posts -> count per day
def extract_liked_posts(liked_posts_dict):
    """extract  count of liked posts per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in liked_posts_dict['likes_media_likes']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='likedPosts_count')

# 79 countdowns-> count per day
def extract_countdowns(countdowns_dict):
    """extract count of reaction to countdowns in a story per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in countdowns_dict['story_activities_countdowns']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='countdowns_count')


# 80 emoji_sliders -> count per day
def extract_emoji_sliders(emoji_sliders_dict):
    """extract count of reaction to emoji slider in a story per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in emoji_sliders_dict['story_activities_emoji_sliders']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='emojiSliderReaction_count')


# 81 polls-> count per day
def extract_polls(polls_dict):
    """extract count of reation to poll in story per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in polls_dict['story_activities_polls']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='pollReaction_count')


# 82 questions -> count per day
def extract_questions(questions_dict):
    """extract count of answers to question in story per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in questions_dict['story_activities_questions']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day
    
    return aggregated_df.reset_index(name='answeredStoryQuestion_count')


# 83 quizzes-> count per day
def extract_quizzes(quizzes_dict):
    """extract count of polls answered in story per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in quizzes_dict['story_activities_quizzes']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day

    return aggregated_df.reset_index(name='pollAnswered_count')


# 84 story_likes -> count per day
def extract_story_likes(story_likes_dict):
    """extract count of liked stories per day"""
    
    dates = [epoch_to_date(t["string_list_data"][0]["timestamp"]) for t in story_likes_dict['story_activities_story_likes']]
    dates_df = pd.DataFrame(dates, columns=['date']) # convert to df
    aggregated_df = dates_df.groupby(["date"])["date"].size() # count number of rows per day
    
    return aggregated_df.reset_index(name='likedStories_count')


