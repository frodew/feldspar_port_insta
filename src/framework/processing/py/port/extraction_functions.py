import pandas as pd
from datetime import datetime, timezone, timedelta
import re

############################
# Helper functions for extraction
############################


# convert timespamp
def epoch_to_date(epoch_timestamp: str | int) -> str:
    """
    Convert epoch timestamp to an ISO 8601 string. Assumes UTC +1

    If timestamp cannot be converted raise CannotConvertEpochTimestamp
    """

    try:
        epoch_timestamp = int(epoch_timestamp)
        out = datetime.fromtimestamp(
            epoch_timestamp, tz=timezone(timedelta(hours=1))
        ).isoformat()  # timezone = utc + 1

    except:
        # fake date if unable to convert
        out = "1999-01-01"

    out = pd.to_datetime(out)
    return str(out.date())  # convertion to string for display in browser


# split name at whitespace, dot, or underscore
def split_name(name):
    parts = re.split(r"[\s._]+", name)
    parts = [part.strip() for part in parts if part.strip()]
    return parts


# check if names in file
def check_name(names_to_check):
    with open("vornamen.txt", "r") as file:
        # read the names from the file and create a set
        names_set = {line.strip() for line in file}

    # check if any name in names_to_check matches the names in the file
    for name in names_to_check:
        if name in names_set:
            return True

    return False


############################
# Extraction functions
############################


def extract_ads_clicked(ads_clicked_dict):
    """extract ads_information/ads_and_topics/ads_clicked -> list of product names per day"""

    timestamps = [
        t["string_list_data"][0]["timestamp"]
        for t in ads_clicked_dict["impressions_history_ads_clicked"]
    ]  # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps]  # convert epochs to dates
    products = [i["title"] for i in ads_clicked_dict["impressions_history_ads_clicked"]]

    adds_clicked_df = pd.DataFrame({"date": dates, "ads_clicked": products})

    aggregated_df = (
        adds_clicked_df.groupby("date")["ads_clicked"].agg(list).reset_index()
    )

    return aggregated_df


def extract_ads_viewed(ads_viewed_dict):
    """extract ads_information/ads_and_topics/ads_viewed -> list of authors per day"""

    timestamps = [
        t["string_map_data"]["Time"]["timestamp"]
        for t in ads_viewed_dict["impressions_history_ads_seen"]
    ]  # get list with timestamps in epoch format (if author exists)
    dates = [epoch_to_date(t) for t in timestamps]  # convert epochs to dates
    authors = [
        i["string_map_data"]["Author"]["value"]
        if "Author" in i["string_map_data"]
        else "unknownAuthor"
        for i in ads_viewed_dict["impressions_history_ads_seen"]
    ]  # not for all viewed ads there is an author!

    adds_viewed_df = pd.DataFrame({"date": dates, "authors_seen": authors})

    aggregated_df = (
        adds_viewed_df.groupby("date")["authors_seen"].agg(list).reset_index()
    )

    return aggregated_df


def get_postViewsPerDay(posts_viewed_dict):
    """extract ads_information/ads_and_topics/posts_viewed -> count per day"""

    timestamps = [
        t["string_map_data"]["Time"]["timestamp"]
        for t in posts_viewed_dict["impressions_history_posts_seen"]
    ]  # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps]  # convert epochs to dates
    postViewedDates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = postViewedDates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="postsViewed_count")


def get_videoViewsPerDay(videos_watched_dict):
    """extract ads_information/ads_and_topics/videos_watched -> count per day"""

    timestamps = [
        t["string_map_data"]["Time"]["timestamp"]
        for t in videos_watched_dict["impressions_history_videos_watched"]
    ]  # get list with timestamps in epoch format
    dates = [epoch_to_date(t) for t in timestamps]  # convert epochs to dates
    videosViewedDates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = videosViewedDates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="videosViewed_count")


def extract_subscription_for_no_ads(subscription_for_no_ads_dict):
    """extract ads_information/instagram_ads_and_businesses/subscription_for_no_ads -> dummy whether user has such a subscription"""

    value = None

    if subscription_for_no_ads_dict["label_values"][0]["value"] == "Inaktiv":
        value = False
    else:
        value = True

    return pd.DataFrame([value], columns=["adfree_subscription"])


def extract_blocked_accounts(blocked_accounts_dict):
    """extract connections/followers_and_following/blocked_accounts -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in blocked_accounts_dict["relationships_blocked_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="blocked_accounts_count")


def extract_close_friends(close_friends_dict):
    """extract connections/followers_and_following/close_friends -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in close_friends_dict["relationships_close_friends"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="close_friends_count")


def extract_followers_1(followers_1_dict):
    """extract connections/followers_and_following/followers_1 -> count per day"""

    # file can just be dict and not list if only one follower
    if isinstance(followers_1_dict, dict):
        dates = [epoch_to_date(followers_1_dict["string_list_data"][0]["timestamp"])]
    else:
        dates = [
            epoch_to_date(t["string_list_data"][0]["timestamp"])
            for t in followers_1_dict
        ]

    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="followers_dict")


def extract_following(following_dict):
    """extract connections/followers_and_following/following -> count"""

    if following_dict is None:
        count = 0
    else:
        following = [
            f for f in following_dict["relationships_following"]
        ]  # get count of following
        count = len(following)

    return pd.DataFrame([count], columns=["following_count"])


def extract_follow_requests_youve_received(follow_requests_youve_received_dict):
    """extract connections/followers_and_following/follow_requests_you've_received_dict -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in follow_requests_youve_received_dict[
            "relationships_follow_requests_received"
        ]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="received_follow_requests_count")


def extract_hide_story_from(hide_story_from_dict):
    """extract connections/followers_and_following/hide_story_from -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in hide_story_from_dict["relationships_hide_stories_from"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="hide_story_from_count")


def extract_pending_follow_requests(pending_follow_requests_dict):
    """extract connections/followers_and_following/pending_follow_requests -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in pending_follow_requests_dict["relationships_follow_requests_sent"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="pending_follow_requests_count")


def extract_recently_unfollowed_accounts(recently_unfollowed_accounts_dict):
    """extract connections/followers_and_following/recently_unfollowed_accounts -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in recently_unfollowed_accounts_dict["relationships_unfollowed_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="recently_unfollowed_accounts_count")


def extract_removed_suggestions(removed_suggestions_dict):
    """extract connections/followers_and_following/removed_suggestions -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in removed_suggestions_dict["relationships_dismissed_suggested_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="removed_suggestions_count")


def extract_restricted_accounts(restricted_accounts_dict):
    """extract connections/followers_and_following/restricted_accounts -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in restricted_accounts_dict["relationships_restricted_users"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="restricted_accounts_count")


def extract_notification_of_privacy_policy_updates(
    notification_of_privacy_policy_updates_dict,
):
    """extract logged_information/policy_updates_and_permissions/notification_of_privacy_policy_updates -> day and value"""

    # extract and preprocess dates
    dates = [
        d["string_map_data"]["Impression Time"]["value"]
        for d in notification_of_privacy_policy_updates_dict[
            "policy_updates_and_permissions_notification_of_privacy_policy_updates"
        ]
    ]
    dates = [datetime.strptime(d, "%b %d, %Y %I:%M:%S%p") for d in dates]
    dates = [
        d.strftime("%Y-%m-%d") for d in dates
    ]  # use same format as in other tables

    consent_statuses = [
        v["string_map_data"]["Consent Status"]["value"]
        for v in notification_of_privacy_policy_updates_dict[
            "policy_updates_and_permissions_notification_of_privacy_policy_updates"
        ]
    ]

    result = pd.DataFrame({"date": dates, "consent_status": consent_statuses})

    return result


def extract_account_information(account_information_dict):
    """extract personal_information/personal_information/account_information -> dummy whether 'contact_syncing' is enabled"""

    value = None

    for k in [
        "Contact Syncing",
        "Kontaktsynchronisierung",
        "Synchronisation des contacts",
    ]:  # keys are language specific
        if (
            k
            in account_information_dict["profile_account_insights"][0][
                "string_map_data"
            ]
        ):
            value = account_information_dict["profile_account_insights"][0][
                "string_map_data"
            ][k]["value"]
            break

    return pd.DataFrame([value], columns=["contact_syncing_enabled"])


def extract_linked_meta_accounts(linked_meta_accounts_dict):
    """extract personal_information/personal_information/linked_meta_accounts -> list of connected accounts"""
    accounts = []

    for a in linked_meta_accounts_dict["profile_linked_meta_accounts"]:
        for k in ["Art des Kontos"]:  # keys are language specific
            if k in a["string_map_data"]:
                account_name = a["string_map_data"][k]["value"]
                accounts.append(account_name)

    accounts_df = pd.DataFrame({"connected_accounts": accounts})

    return accounts_df


def extract_personal_information(personal_information_dict):
    """
    extract personal_information/personal_information/personal_information.json -> dummies whether user has profile image, email, phone, and private account
    + extract whether used name is real name if compared against list of names ("vornamen.txt")

    """

    # check if information present

    profile_image, email, phone, private_account = None, None, None, None

    for k in ["Profile Photo", "Profilbild"]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["media_map_data"]:
            profile_image = (
                personal_information_dict["profile_user"][0]["media_map_data"][k]["uri"]
                != "False"
            )
            break

    for k in ["Email", "E-Mail-Adresse"]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["string_map_data"]:
            email = (
                personal_information_dict["profile_user"][0]["string_map_data"][k][
                    "value"
                ]
                != "False"
            )
            break

    for k in [
        "Phone Confirmed",
        "Telefonnummer best\u00c3\u00a4tigt",
    ]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["string_map_data"]:
            phone = (
                personal_information_dict["profile_user"][0]["string_map_data"][k][
                    "value"
                ]
                != "False"
            )
            break

    for k in ["Private Account", "Privates Konto"]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["string_map_data"]:
            private_account = personal_information_dict["profile_user"][0][
                "string_map_data"
            ][k]["value"]
            break

    # check if real name used in profile

    name_to_check = None
    real_name = False

    for k in ["Name"]:  # keys are language specific
        if k in personal_information_dict["profile_user"][0]["string_map_data"]:
            name_to_check = personal_information_dict["profile_user"][0][
                "string_map_data"
            ][k]["value"]
            break

    # split names to check
    names_to_check = split_name(name_to_check)

    # check if name in list of names
    real_name = check_name(names_to_check)

    result = pd.DataFrame(
        {
            "profile_image": [profile_image],
            "email": [email],
            "phone": [phone],
            "private_account": [private_account],
            "real_name_in_profile": [real_name],
        }
    )

    return result


def extract_profile_changes(profile_changes_dict):
    """extract personal_information/personal_information/profile_changes -> day and what was changed"""

    changed_dates, changed_values = None, None

    changes = [
        t["string_map_data"] for t in profile_changes_dict["profile_profile_change"]
    ]

    for k in ["Changed", "Ge\u00c3\u00a4ndert"]:  # keys are language specific
        if any(k in d for d in changes):
            changed_values = [t[k]["value"] for t in changes]
            break

    for k in ["Change Date", "Datum \u00c3\u00a4ndern"]:  # keys are language specific
        if any(k in d for d in changes):
            changed_dates = [epoch_to_date(t[k]["timestamp"]) for t in changes]
            break

    changes_df = pd.DataFrame({"date": changed_dates, "changes_made": changed_values})

    return changes_df


def extract_comments_allowed_from(comments_allowed_from_dict):
    """extract preferences/media_settings/comments_allowed_from -> value"""

    value = None

    for k in [
        "Comments Allowed From",
        "Kommentieren gestattet f\u00c3\u00bcr",
    ]:  # keys are language specific
        if (
            k
            in comments_allowed_from_dict["settings_allow_comments_from"][0][
                "string_map_data"
            ]
        ):
            value = comments_allowed_from_dict["settings_allow_comments_from"][0][
                "string_map_data"
            ][k]["value"]
            break

    return pd.DataFrame([value], columns=["comments_allowed_from"])


def extract_comments_blocked_from(comments_blocked_from_dict):
    """extract preferences/media_settings/comments_blocked_from -> count"""

    if comments_blocked_from_dict is None:
        count = 0
    else:
        count = len(
            [f for f in comments_blocked_from_dict["settings_blocked_commenters"]]
        )

    return pd.DataFrame([count], columns=["comments_blocked_from"])


def extract_consents(consents_dict):
    """extract preferences/media_settings/consents -> day and value"""

    # extract and preprocess dates
    date = epoch_to_date(consents_dict["timestamp"])

    consents = [v["label"] for v in consents_dict["label_values"]]

    result = pd.DataFrame({"date": date, "consent_message": consents})

    return result


def extract_use_crossapp_messaging(use_cross_app_messaging_dict):
    """extract preferences/media_settings/use_cross-app_messaging_dict -> value if enabled"""

    enabled = None

    for a in use_cross_app_messaging_dict["settings_upgraded_to_cross_app_messaging"]:
        for k in [
            "Aktualisierung auf App-\u00c3\u00bcbergreifendes Messaging durchgef\u00c3\u00bchrt"
        ]:  # keys are language specific
            print(enabled, a["string_map_data"])
            if k in a["string_map_data"]:
                enabled = a["string_map_data"][k]["value"]
                print(enabled)

    return pd.DataFrame([enabled], columns=["cross_app_messaging"])


def extract_topics_df(topics_dict):
    """extract preferences/your_topics -> list of topics"""

    topics_list = [
        t["string_map_data"]["Name"]["value"] for t in topics_dict["topics_your_topics"]
    ]
    topics_df = pd.DataFrame(topics_list, columns=["your_topics"])

    return topics_df


def extract_account_privacy_changes(account_privacy_changes_dict):
    """extract security_and_login_information/login_and_account_creation/account_privacy_changes -> day and type-change"""

    changes = [
        c
        for c in account_privacy_changes_dict["account_history_account_privacy_history"]
    ]
    titles = [t["title"] for t in changes]
    timestamps = []

    for c in changes:
        for k in ["Time", "Zeit"]:  # keys are language specific
            if k in c["string_map_data"]:
                timestamp = c["string_map_data"][k]["timestamp"]
                timestamps.append(epoch_to_date(timestamp))
                break

    changes_df = pd.DataFrame({"date": timestamps, "change_account_type": titles})

    aggregated_df = (
        changes_df.groupby("date")["change_account_type"].agg(list).reset_index()
    )

    return aggregated_df


def extract_login_activity(login_activity_dict):
    """extract security_and_login_information/login_and_account_creation/login_activity -> time and user agent"""

    logins = login_activity_dict["account_history_login_history"]

    timestamps = [t["title"] for t in logins]
    dates = [str(datetime.fromisoformat(timestamp).date()) for timestamp in timestamps]
    times = [datetime.fromisoformat(timestamp).time() for timestamp in timestamps]

    user_agents = [t["string_map_data"]["User Agent"]["value"] for t in logins]

    login_df = pd.DataFrame({"date": dates, "time": times, "user_agent": user_agents})

    return login_df


def extract_logout_activity(logout_activity_dict):
    """extract security_and_login_information/login_and_account_creation/logout_activity -> time and user agent"""

    logouts = logout_activity_dict["account_history_logout_history"]

    timestamps = [t["title"] for t in logouts]
    dates = [str(datetime.fromisoformat(timestamp).date()) for timestamp in timestamps]
    times = [datetime.fromisoformat(timestamp).time() for timestamp in timestamps]

    user_agents = [t["string_map_data"]["User Agent"]["value"] for t in logouts]

    logout_df = pd.DataFrame({"date": dates, "time": times, "user_agent": user_agents})

    return logout_df


def extract_signup_information(signup_information_dict):
    """extract security_and_login_information/login_and_account_creation/signup_information -> dummy if real name is used"""

    name_to_check = None
    real_name = False

    for k in ["Username", "Benutzername"]:  # keys are language specific
        if (
            k
            in signup_information_dict["account_history_registration_info"][0][
                "string_map_data"
            ]
        ):
            name_to_check = signup_information_dict[
                "account_history_registration_info"
            ][0]["string_map_data"][k]["value"]
            break

    # split names to check
    names_to_check = split_name(name_to_check)

    # check if name in list of names
    real_name = check_name(names_to_check)

    return pd.DataFrame([real_name], columns=["real_name_signup"])


def extract_recently_viewed_items(recently_viewed_items_dict):
    """extract your_instagram_activity/shopping/recently_viewed_items -> list of items"""

    items = recently_viewed_items_dict["checkout_saved_recently_viewed_products"]
    products = [p["string_map_data"]["Product Name"]["value"] for p in items]

    products_df = pd.DataFrame(products, columns=["recently_viewed_items"])

    return products_df


def extract_post_comments_1(post_comments_1_dict):
    """extract your_instagram_activity/comments/post_comments_1 -> count per day"""

    # file can just be dict and not list if only one posted comment
    if isinstance(post_comments_1_dict, dict):
        dates = [
            epoch_to_date(post_comments_1_dict["string_map_data"]["Time"]["timestamp"])
        ]
    else:
        dates = [
            epoch_to_date(t["string_map_data"]["Time"]["timestamp"])
            for t in post_comments_1_dict
        ]  # get list with timestamps in epoch format

    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="postComments_count")


def extract_reels_comments(reels_comments_dict):
    """extract your_instagram_activity/comments/reels_comments -> count per day"""

    dates = [
        epoch_to_date(t["string_map_data"]["Time"]["timestamp"])
        for t in reels_comments_dict["comments_reels_comments"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="reelsComments_count")


def extract_archived_posts(archived_posts_dict, picture_info):
    """extract your_instagram_activity/content/archived_posts -> count per day + info about face and location"""

    results = []

    for post in archived_posts_dict.get("ig_archived_post_media", []):
        for media in post.get("media", []):
            time = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any(
                "latitude" in exif_data
                for exif_data in media.get("media_metadata", {})
                .get("photo_metadata", {})
                .get("exif_data", [])
            )

            # check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append(
                {
                    "time": time,
                    "has_location": has_latitude_data,
                    "face_visible": face_visible,
                }
            )

    archived_posts_df = pd.DataFrame(results)

    return archived_posts_df


def extract_posts_1(posts_1_dict, picture_info):
    """extract your_instagram_activity/content/posts_1 -> count per day + info about face and location"""

    results = []

    # file can just be dict and not list if only one post
    if isinstance(posts_1_dict, dict):
        for media in posts_1_dict.get("media", []):
            time = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any(
                "latitude" in exif_data
                for exif_data in media.get("media_metadata", {})
                .get("photo_metadata", {})
                .get("exif_data", [])
            )

            # check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append(
                {
                    "time": time,
                    "has_location": has_latitude_data,
                    "face_visible": face_visible,
                }
            )

    else:
        for post in posts_1_dict:
            for media in post.get("media", []):
                time = epoch_to_date(media.get("creation_timestamp", ""))
                uri = media.get("uri", "")
                has_latitude_data = any(
                    "latitude" in exif_data
                    for exif_data in media.get("media_metadata", {})
                    .get("photo_metadata", {})
                    .get("exif_data", [])
                )

                # check if the URI is in the picture_info dictionary
                face_visible = picture_info.get(uri, False)

                results.append(
                    {
                        "time": time,
                        "has_location": has_latitude_data,
                        "face_visible": face_visible,
                    }
                )

    posts_df = pd.DataFrame(results)

    return posts_df


def extract_profile_photos(profile_photos_dict, picture_info):
    """extract your_instagram_activity/content/profile_photos -> info about face"""

    uri = profile_photos_dict.get("ig_profile_picture", [])[0].get("uri", "")

    # check if the URI is in the picture_info dictionary
    face_visible = picture_info.get(uri, False)

    face_in_picture = True if face_visible >= 1 else False

    return pd.DataFrame([face_in_picture], columns=["face_in_picture"])


def extract_recently_deleted_content(recently_deleted_content_dict, picture_info):
    """extract your_instagram_activity/content/recently_deleted_content -> count per day + info about face and location"""

    results = []

    for post in recently_deleted_content_dict.get("ig_recently_deleted_media", []):
        for media in post.get("media", []):
            time = epoch_to_date(media.get("creation_timestamp", ""))
            uri = media.get("uri", "")
            has_latitude_data = any(
                "latitude" in exif_data
                for exif_data in media.get("media_metadata", {})
                .get("photo_metadata", {})
                .get("exif_data", [])
            )

            # Check if the URI is in the picture_info dictionary
            face_visible = picture_info.get(uri, False)

            results.append(
                {
                    "time": time,
                    "has_location": has_latitude_data,
                    "face_visible": face_visible,
                }
            )

    recently_deleted_content_df = pd.DataFrame(results)

    return recently_deleted_content_df


def extract_reels(reels_dict):
    """extract your_instagram_activity/content/reels -> count per day"""

    dates = [
        epoch_to_date(media.get("creation_timestamp"))
        for reel in reels_dict.get("ig_reels_media", [])
        for media in reel.get("media", [])
    ]
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="reels_count")


def extract_stories(stories_dict, picture_info):
    """extract your_instagram_activity/content/stories -> count per day + info about face and location"""

    results = []

    for story in stories_dict.get("ig_stories", []):
        time = epoch_to_date(story.get("creation_timestamp", ""))
        uri = story.get("uri", "")
        has_latitude_data = any(
            "latitude" in exif_data
            for exif_data in story.get("media_metadata", {})
            .get("photo_metadata", {})
            .get("exif_data", [])
        )

        # check if the URI is in the picture_info dictionary
        face_visible = picture_info.get(uri, False)

        results.append(
            {
                "time": time,
                "has_location": has_latitude_data,
                "face_visible": face_visible,
            }
        )

    stories_df = pd.DataFrame(results)

    return stories_df


def extract_liked_comments(liked_comments_dict):
    """extract your_instagram_activity/likes/liked_comments -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in liked_comments_dict["likes_comment_likes"]
    ]
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="likedComments_count")


def extract_liked_posts(liked_posts_dict):
    """extract your_instagram_activity/likes/liked_posts -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in liked_posts_dict["likes_media_likes"]
    ]
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="likedPosts_count")


def extract_saved_collections(saved_collections_dict):
    """extract your_instagram_activity/saved/saved_collections -> count per day"""

    dates = []

    # get list with timestamps in epoch format and skip all collection titles
    for t in saved_collections_dict["saved_saved_collections"]:
        for k in ["Added Time"]:  # keys are language specific
            if k in t["string_map_data"]:
                try:
                    dates.append(epoch_to_date(t["string_map_data"][k]["timestamp"]))
                except:
                    continue
                break

    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="saved_collections_count")


def extract_saved_posts(saved_posts_dict):
    """extract your_instagram_activity/saved/saved_posts -> count per day"""

    dates = []

    # get list with timestamps in epoch format
    for t in saved_posts_dict["saved_saved_media"]:
        for k in ["Saved on"]:  # keys are language specific
            if k in t["string_map_data"]:
                dates.append(epoch_to_date(t["string_map_data"][k]["timestamp"]))
            break

    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="saved_posts_count")


def extract_countdowns(countdowns_dict):
    """extract your_instagram_activity/story_sticker_interactions/countdowns -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in countdowns_dict["story_activities_countdowns"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="countdowns_count")


def extract_emoji_sliders(emoji_sliders_dict):
    """extract your_instagram_activity/story_sticker_interactions/emoji_sliders -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in emoji_sliders_dict["story_activities_emoji_sliders"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="emojiSliderReaction_count")


def extract_polls(polls_dict):
    """extract your_instagram_activity/story_sticker_interactions/polls -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in polls_dict["story_activities_polls"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="pollReaction_count")


def extract_questions(questions_dict):
    """extract your_instagram_activity/story_sticker_interactions/questions -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in questions_dict["story_activities_questions"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="answeredStoryQuestion_count")


def extract_quizzes(quizzes_dict):
    """extract your_instagram_activity/story_sticker_interactions/quizzes -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in quizzes_dict["story_activities_quizzes"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="pollAnswered_count")


def extract_story_likes(story_likes_dict):
    """extract your_instagram_activity/story_sticker_interactions/story_likes -> count per day"""

    dates = [
        epoch_to_date(t["string_list_data"][0]["timestamp"])
        for t in story_likes_dict["story_activities_story_likes"]
    ]  # get list with timestamps in epoch format
    dates_df = pd.DataFrame(dates, columns=["date"])  # convert to df

    aggregated_df = dates_df.groupby(["date"])[
        "date"
    ].size()  # count number of rows per day

    return aggregated_df.reset_index(name="likedStories_count")
