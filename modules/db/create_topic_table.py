import sqlite3
from datetime import datetime

# Function to initialize the database
def initialize_db(db_name="./db/podcast.db"):
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create a table for storing podcast topics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"Database '{db_name}' initialized successfully.")

# Function to add a new topic to the database
def add_topic(title, description=None, db_name="./db/podcast.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Insert topic into the database
    cursor.execute("""
    INSERT INTO topics (title, description)
    VALUES (?, ?)
    """, (title, description))
    
    conn.commit()
    conn.close()
    print(f"Topic '{title}' added to the database.")

# Function to fetch all topics from the database
def fetch_all_topics(db_name="./db/podcast.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Fetch all topics
    cursor.execute("SELECT * FROM topics ORDER BY timestamp DESC")
    topics = cursor.fetchall()
    
    conn.close()
    return topics

# Example usage
if __name__ == "__main__":
    # Initialize the database
    initialize_db()
    
    # Add a new topic
    # add_topic("The impact of AI on the job market")
    # add_topic("Future of space exploration")
    add_topic("Exploring how AI is reshaping employment and opportunities.")
    add_topic("What lies ahead in humanity's quest to explore the cosmos?")
    
    # Fetch and display all topics
    topics = fetch_all_topics()
    print("Stored Topics:")
    for topic in topics:
        print(f"ID: {topic[0]}, Title: {topic[1]}, Description: {topic[2]}, Timestamp: {topic[3]}")
