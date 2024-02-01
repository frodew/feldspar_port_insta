# helper functions -----------------------------

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