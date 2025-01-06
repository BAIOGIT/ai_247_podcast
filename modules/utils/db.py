import sqlite3

# SQLite database setup
DB_PATH = "./db/podcast.db"

def fetch_news_from_db(processed=False):
    """Fetch news from the database based on their processed status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, audio_path FROM news WHERE processed = ?", (processed,))
    rows = cursor.fetchall()
    conn.close()
    return [{"title": row[0], "audio_path": row[1]} for row in rows]

def update_news_status(title, processed, audio_path):
    """Update the processed status and audio path of a news in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE news SET processed = ?, audio_path = ? WHERE title = ?",
        (processed, audio_path, title),
    )
    conn.commit()
    conn.close()
