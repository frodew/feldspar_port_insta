from port.extraction_functions import *

# defines which extraction functions are used and what titles are displayed

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
            "en": "Number of accounts you have blocked by day",
            "nl": "Inhoud zip bestand"
            }
    },
    "close_friends": {
        "extraction_function": extract_close_friends,
        "title": {
            "en": "Number of close friends by day",
            "nl": "Inhoud zip bestand"
            }
    },
    "followers_1": {
        "extraction_function": extract_followers_1,
        "title": {
            "en": "Number of followers by day",
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
            "en": "Number of follow requests you have received by day",
            "nl": "Inhoud zip bestand"
            }
    },
    "hide_story_from": {
        "extraction_function": extract_hide_story_from,
        "title": {
            "en": "Number of account you have hidden your story from by day",
            "nl": "Inhoud zip bestand"
            }
    },
    "pending_follow_requests": {
        "extraction_function": extract_pending_follow_requests,
        "title": {
            "en": "Number of your pending follow requests by day",
            "nl": "Inhoud zip bestand"
            }
    },
    "recently_unfollowed_accounts": {
        "extraction_function": extract_recently_unfollowed_accounts,
        "title": {
            "en": "Number of accounts you recently unfollowed by day",
            "nl": "Inhoud zip bestand"
            }
    },
    "removed_suggestions": {
        "extraction_function": extract_removed_suggestions,
        "title": {
            "en": "Number of accounts that you've removed from your suggestions by day",
            "nl": "Inhoud zip bestand"
            }
    },
    "restricted_accounts": {
        "extraction_function": extract_restricted_accounts,
        "title": {
            "en": "Number of accounts that you've restricted by day",
            "nl": "Inhoud zip bestand"
            }
    },

    "notification_of_privacy_policy_updates": {
        "extraction_function": extract_notification_of_privacy_policy_updates,
        "title": {
            "en": "When did you view updates to the Meta Privacy Policy?",
            "nl": "Inhoud zip bestand"
        }
    },

    "account_information.json": {
        "extraction_function": extract_account_information,
        "title": {
            "en": "Have you enabled contact syncing?",
            "nl": "Inhoud zip bestand"
        }
    },

    "personal_information.json": {
        "extraction_function": extract_personal_information,
        "title": {
            "en": "Do you have a profile image, email, phone, a private account, and do you use your real name?",
            "nl": "Inhoud zip bestand"
        }
    },

    "profile_changes": {
        "extraction_function": extract_profile_changes,
        "title": {
            "en": "When did you change your personal information?",
            "nl": "Inhoud zip bestand"
        }
    },

    "comments_allowed_from": {
        "extraction_function": extract_comments_allowed_from,
        "title": {
            "en": "Which accounts do you allow comments from?",
            "nl": "Inhoud zip bestand"
        }
    },

    "comments_blocked_from": {
        "extraction_function": extract_comments_blocked_from,
        "title": {
            "en": "Number of account you blocked from commenting.",
            "nl": "Inhoud zip bestand"
        }
    },

    "your_topics": {
        "extraction_function": extract_topics_df,
        "title": {
            "en": "Your Topics inferred by Instagram",
            "nl": "Inhoud zip bestand"
            }
    },


    "account_privacy_changes": {
        "extraction_function": extract_account_privacy_changes,
        "title": {
            "en": "When did you switch your account to being public/private?",
            "nl": "Inhoud zip bestand"
        }
    },


    "login_activity": {
        "extraction_function": extract_login_activity,
        "title": {
            "en": "When and with which user agent did you log in to Instagram?",
            "nl": "Inhoud zip bestand"
        }
    },


    "logout_activity": {
        "extraction_function": extract_logout_activity,
        "title": {
            "en": "When and with which user agent did you log out of Instagram?",
            "nl": "Inhoud zip bestand"
        }
    },

    "signup_information": {
        "extraction_function": extract_signup_information,
        "title": {
            "en": "Did you use a real name to signup on Instagram?",
            "nl": "Inhoud zip bestand"
        }
    },

    "recently_viewed_items": {
        "extraction_function": extract_recently_viewed_items,
        "title": {
            "en": "Which shopping items have you recently viewed?",
            "nl": "Inhoud zip bestand"
        }
    },


    "post_comments_1": {
        "extraction_function": extract_post_comments_1,
        "title": {
            "en": "How often did you comment on posts per day?",
            "nl": "Inhoud zip bestand"
        }
    },


    "reels_comments": {
        "extraction_function": extract_reels_comments,
        "title": {
            "en": "How often did you comment on reels per day?",
            "nl": "Inhoud zip bestand"
        }
    },

    "archived_posts": {
        "extraction_function": extract_archived_posts,
        "picture_info": None,
        "title": {
            "en": "How often did you archive posts and what information was included?",
            "nl": "Inhoud zip bestand"
        }
    },


    "posts_1": {
        "extraction_function": extract_posts_1,
        "picture_info": None,
        "title": {
            "en": "How often did you post and what information was included?",
            "nl": "Inhoud zip bestand"
        }
    },

    "profile_photos": {
        "extraction_function": extract_profile_photos,
        "picture_info": None,
        "title": {
            "en": "Do you use a face in your profile photo?",
            "nl": "Inhoud zip bestand"
        }
    },

    "recently_deleted_content": {
        "extraction_function": extract_recently_deleted_content,
        "picture_info": None,
        "title": {
            "en": "How often did you delete posts and what information was included?",
            "nl": "Inhoud zip bestand"
        }
    },

    "reels": {
        "extraction_function": extract_reels,
        "title": {
            "en": "How often did you post reels?",
            "nl": "Inhoud zip bestand"
        }
    },

    "stories": {
        "extraction_function": extract_stories,
        "title": {
            "en": "How often did you post stories and did you include location information?",
            "nl": "Inhoud zip bestand"
        }
    },


    "liked_comments": {
        "extraction_function": extract_liked_comments,
        "title": {
            "en": "How often did you like comments per day?",
            "nl": "Inhoud zip bestand"
        }
    },


    "liked_posts": {
        "extraction_function": extract_liked_posts,
        "title": {
            "en": "How often did you like posts per day?",
            "nl": "Inhoud zip bestand"
        }
    },

    "countdowns": {
        "extraction_function": extract_countdowns,
        "title": {
            "en": "How often did you react to an countdown in a story per day?",
            "nl": "Inhoud zip bestand"
        }
    },


    "emoji_sliders": {
        "extraction_function": extract_emoji_sliders,
        "title": {
            "en": "How often did you react to an emoji slider in a story per day?",
            "nl": "Inhoud zip bestand"
        }
    },


    "polls": {
        "extraction_function": extract_polls,
        "title": {
            "en": "How often did you react to a poll in a story per day?",
            "nl": "Inhoud zip bestand"
        }
    },


    "questions": {
        "extraction_function": extract_questions,
        "title": {
            "en": "How often did you answer a question in a story per day?",
            "nl": "Inhoud zip bestand"
        }
    },


    "quizzes": {
        "extraction_function": extract_quizzes,
        "title": {
            "en": "How often did you answer a poll in story per day?",
            "nl": "Inhoud zip bestand"
        }
    },

    "story_likes": {
        "extraction_function": extract_story_likes,
        "title": {
            "en": "How often did you like a story per day?",
            "nl": "Inhoud zip bestand"
        }
    }

}
