from port.extraction_functions import *

# defines which extraction functions are looped over and what titles are displayed

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