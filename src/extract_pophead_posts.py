import json
import praw


if __name__ == "__main__":
    reddit = praw.Reddit("popHeadsPlaylist")
    submission_details = []
    
    for post in reddit.subreddit("popheads").top(time_filter="month"):
        submission_details.append({
            "post_title": post.title,
            "post_text": post.selftext
        })
        
    with open("data/reddit_posts/reddit_posts.json", "a+") as f:
        json.dump(submission_details, f, indent=2)
