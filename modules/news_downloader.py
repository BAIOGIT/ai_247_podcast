import sqlite3
from datetime import datetime
import feedparser
import os

# Set the certificate file path
os.environ['SSL_CERT_FILE'] = '/etc/ssl/certs/ca-certificates.crt'

# Function to check if a news article already exists in the database
def news_exists(title, db_name="./db/podcast.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT COUNT(*) FROM news WHERE title = ?
    """, (title,))
    exists = cursor.fetchone()[0] > 0
    
    conn.close()
    return exists

# Function to add a new news article to the database
def add_news(title, description=None, db_name="./db/podcast.db"):
    # Check if the news article already exists
    if news_exists(title, db_name):
        print(f"News article '{title}' already exists in the database. Skipping.")
        return
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL UNIQUE,
        description TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Insert news article
    cursor.execute("""
    INSERT INTO news (title, description)
    VALUES (?, ?)
    """, (title, description))
    
    conn.commit()
    conn.close()
    print(f"News article '{title}' added to the database.")

# Function to fetch and store RSS feed data
def fetch_and_store_rss_feed(feed_url, db_name="./db/podcast.db"):
    # Parse the RSS feed
    feed = feedparser.parse(feed_url)
    print(f"Fetching RSS feed from: {feed_url}")
    
    if feed.bozo:
        print(f"Failed to fetch RSS feed: {feed.bozo_exception}")
        return
    
    print(f"Fetched {len(feed.entries)} articles from RSS feed.")
    
    for entry in feed.entries:
        title = entry.title
        description = entry.get("description", "")
        add_news(title, description, db_name)

# Main execution
if __name__ == "__main__":
    RSS_FEED_URL = "https://www.newsbtc.com/feed/"
    DB_NAME = "./db/podcast.db"
    
    # Fetch and store RSS feed data
    fetch_and_store_rss_feed(RSS_FEED_URL, DB_NAME)
