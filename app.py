import praw
import os
import requests
import threading
import time
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

# Discord Webhook URLs (you can add more)
WEBHOOK_CONFIGS = [
    {
        "subreddits": ["hiphopheads"],
        "webhook_url": os.getenv("DISCORD_WEBHOOK_URL_1")
    },
    {
        "subreddits": ["conspiracy"],
        "webhook_url": os.getenv("DISCORD_WEBHOOK_URL_2")
    }
]

def process_submission(submission, webhook_url):
    """Process a single submission and send to Discord."""
    # Create the full Reddit URL by adding the permalink to the Reddit domain
    reddit_post_url = f"https://www.reddit.com{submission.permalink}"
    
    # Start building the message
      post_message = f"🚨 New Post in r/{submission.subreddit.display_name}! 🚨\n\n{submission.title}\n👤 OP: u/{submission.author.name}\n🔗 [View Post]({reddit_post_url}) | 👍 {submission.score} upvotes"

    # Handle text posts (self posts)
    if submission.is_self:
        # Truncate text if it's too long
        if submission.selftext:
            post_message += f"\n\n📝 **Post Text:**\n{submission.selftext[:1000]}..."

    # Handle link posts
    if submission.is_self is False:
        post_message += f"\n📌 [External Link]({submission.url})"

    # Send message to Discord
    payload = {"content": post_message}
    response = requests.post(webhook_url, json=payload)

    if response.status_code == 204:
        print(f"Sent to Discord: {submission.title}")
    else:
        print(f"Failed to send: {response.text}")

def start_bot(subreddits, webhook_url):
    """Function to stream new posts and send them to Discord."""
    subreddit = reddit.subreddit("+".join(subreddits))
    print(f"Listening for new posts in r/{subreddit.display_name}...")

    for submission in subreddit.stream.submissions(skip_existing=True):
        # Only process recent posts (less than 10 minutes old)
        current_time = time.time()
        if current_time - submission.created_utc < 600:
            process_submission(submission, webhook_url)

def start_all_bots():
    """Start bot threads for all webhook configurations."""
    threads = []
    for config in WEBHOOK_CONFIGS:
        thread = threading.Thread(
            target=start_bot, 
            args=(config['subreddits'], config['webhook_url']), 
            daemon=True
        )
        thread.start()
        threads.append(thread)
    return threads

# Start all bot threads
start_all_bots()

def keep_alive():
    """Periodically ping our own endpoint to prevent Render from sleeping"""
    while True:
        try:
            # Replace this URL with your actual Render URL
            requests.get("https://your-app-name.onrender.com")
            print("Pinged self to stay awake")
        except Exception as e:
            print(f"Self-ping failed: {e}")
        time.sleep(840)  # 14 minutes

# Add the keep-alive thread
threading.Thread(target=keep_alive, daemon=True).start()

@app.get("/")
def home():
    """Home route to check if the bot is running."""
    return {"status": "Bot is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
