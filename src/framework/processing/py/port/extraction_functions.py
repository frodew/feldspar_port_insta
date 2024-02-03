import pandas as pd
from datetime import datetime, timezone, timedelta

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
    
    addfree_subscription = (subscription_for_no_ads_dict != None)
    return pd.DataFrame([addfree_subscription], columns=['adfree_subscription'])


# 15 followers_and_following/blocked_accounts -> count
def extract_blocked_accounts(blocked_accounts_dict):
    """extract count of blocked accounts"""
    
    if blocked_accounts_dict == None:
        count = 0
    else:
        count = len([a for a in blocked_accounts_dict["relationships_blocked_users"]])
        
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
def extract_hide_story_from(hide_story_from_dict):
    """extract count of accounts story is hidden from"""

    if hide_story_from_dict == None:
        count = 0
    else:
        count = len([x for x in hide_story_from_dict["relationships_hide_stories_from"]])
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
def extract_recently_unfollowed_accounts(recently_unfollowed_accounts_dict):
    """extract count of recently unfollowed accounts"""
    if recently_unfollowed_accounts_dict == None:
        count = 0
    else:
        count = len([x for x in recently_unfollowed_accounts_dict["relationships_unfollowed_users"]])
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
def extract_restricted_accounts(restricted_accounts_dict):
    """extract count of restricted accounts"""
    if restricted_accounts_dict == None:
        count = 0
    else:
        count = len([f for f in restricted_accounts_dict["relationships_restricted_users"]])
    return pd.DataFrame([count], columns=['restricted_accounts_count'])


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

    
    result =pd.DataFrame(
                {"profile_image": [profile_image],
                "email": [email], 
                "phone": [phone], 
                "private_account": [private_account]})

    return result


# 43 personal_information/profile_changes 43 -> day and what was changed
def extract_profile_changes(profile_changes_dict):
    """extract day and what was changed"""
    
    changes = [t["string_map_data"] for t in profile_changes_dict['profile_profile_change']]
    change_values = [t["Changed"]['value'] for t in changes]
    change_dates = [epoch_to_date(t['Change Date']["timestamp"]) for t in changes]

    changes_df = pd.DataFrame(
        {"date": change_dates,
        "changes_made": change_values}
    )
    
    aggregated_df = changes_df.groupby('date')['changes_made'].agg(list).reset_index()
    
    return aggregated_df


# 44 comments_allowed_from -> value
def extract_comments_allowed_from(comments_allowed_from_dict):
    """extract who can comment"""
    
    for k in ["Comments Allowed From", "Kommentieren gestattet fÃ¼r"]: # keys are language specific
        if k in comments_allowed_from_dict['settings_allow_comments_from'][0]["string_map_data"]:
            value = comments_allowed_from_dict['settings_allow_comments_from'][0]["string_map_data"][k]["value"]
            break  

    return pd.DataFrame([value], columns=['comments_allowed_from'])


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


