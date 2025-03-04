import praw
import os
import requests
import threading
from fastapi import FastAPI
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Reddit API Credentials from .env
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

# Discord Webhook URL from .env
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Subreddit to monitor
subreddit_name = ["hiphopheads", "askreddit", "memes"]  # Change this to your target subreddit
subreddit = reddit.subreddit("+".join(subreddit_name))

print(f"Listening for new posts in r/{subreddit.display_name}...")


def start_bot():
    """Function to stream new posts and send them to Discord."""
    for submission in subreddit.stream.submissions(skip_existing=True):
         reddit_post_link = f"https://www.reddit.com{submission.permalink}"
    
    if submission.is_self:
        # If it's a text post, just send the Reddit link
        post_message = f"**New Post in r/{subreddit_name}!** \n\n**{submission.title}**\n🔗 [View Post]({reddit_post_link}) | 👍 {submission.score} upvotes"
    else:
        # If it's a link post, show both Reddit and external link
        post_message = f"**New Post in r/{subreddit_name}!** \n\n**{submission.title}**\n🔗 [View on Reddit]({reddit_post_link})\n🔗 [External Link]({submission.url}) | 👍 {submission.score} upvotes"

        # Send message to Discord
        payload = {"content": post_message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

        if response.status_code == 204:
            print(f"Sent to Discord: {submission.title}")
        else:
            print(f"Failed to send: {response.text}")


# Run the bot in a separate thread
threading.Thread(target=start_bot, daemon=True).start()


@app.get("/")
def home():
    """Home route to check if the bot is running."""
    return {"status": "Bot is running!"}
