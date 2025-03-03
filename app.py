import praw
import os
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Reddit API Credentials from .env
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Discord Webhook URL from .env
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Subreddit to monitor
subreddit_name = ["hiphopheads", "memes", "indiasocial"]  # Change this to your target subreddit
subreddit = reddit.subreddit("+".join(subreddit_name))

print(f"Listening for new posts in r/{subreddit.display_name}...")

# Stream new posts and send them to Discord
for submission in subreddit.stream.submissions(skip_existing=True):
    post_message = f"🚨 **New Post in r/{subreddit_name}!** 🚨\n\n**{submission.title}**\n🔗 [View Post]({submission.url}) | 👍 {submission.score} upvotes"
    
    # Send message to Discord
    payload = {"content": post_message}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    
    if response.status_code == 204:
        print(f"Sent to Discord: {submission.title}")
    else:
        print(f"Failed to send: {response.text}")
