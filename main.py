import asyncio
import time
import ssl
import websockets
import queue
import threading
from modules.background_music import BackgroundMusic
from modules.news_processor import NewsProcessor
from modules.podcast import PodcastPlayer
from modules.utils.db import fetch_news_from_db
from modules.program import Program  # Assuming you've created the Program class in this module
import datetime

# WebSocket handler to send current song info
async def websocket_handler(websocket, path):
    try:
        while True:
            # Here you would send the currently playing song or any other relevant data
            message = "Currently playing song: Example Song"  # This should be dynamic from your background music
            await websocket.send(message)
            await asyncio.sleep(1)  # Sending data every second or as needed
    except websockets.exceptions.ConnectionClosed:
        print("WebSocket connection closed")
    finally:
        await websocket.close()

# WebSocket server setup
async def start_wss_server():
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # ssl_context.load_cert_chain(certfile="path_to_cert.pem", keyfile="path_to_key.pem")  # Specify your SSL certificate files
    start_server = await websockets.serve(websocket_handler, "localhost", 8765, ssl=ssl_context)
    print("WebSocket server started")
    await start_server.wait_closed()  # Wait for server to stop

# Function to launch the program periodically using datetime
async def launch_program_periodically(program, program_audio_path, fade_out_duration=3000, fade_in_duration=3000):
    # This function ensures that the program is launched exactly every 2 minutes.
    while True:
        # Get current time
        current_time = datetime.datetime.now()

        # Calculate how many seconds to wait until the next 2-minute mark
        next_trigger_time = current_time.replace(second=0, microsecond=0) + datetime.timedelta(minutes=2)
        wait_time = (next_trigger_time - current_time).total_seconds()

        print(f"Waiting for {wait_time} seconds until the next program launch...")
        await asyncio.sleep(wait_time)  # Sleep until the next 2-minute mark
        
        # Trigger the program override
        print("Launching program override...")
        program.override_background_music(program_audio_path, fade_out_duration, fade_in_duration)

async def main():
    # Configuration
    playlist_folder = "./data/playlist/downloads"
    voice_model = "tts_models/multilingual/multi-dataset/xtts_v2"
    speaker_wav_path = "./data/voices/a-better-future-with-the-tesla-powerwall-elon-musk-101soundboards.mp3"
    program_audio_path = "./data/voices/a-better-future-with-the-tesla-powerwall-elon-musk-101soundboards.mp3"  # Example program audio (could be a news or podcast)

    # Initialize components
    argument_queue = queue.Queue()
    background_music = BackgroundMusic(playlist_folder)
    news_processor = NewsProcessor(voice_model, speaker_wav_path)
    program = Program(background_music)
    podcast_player = PodcastPlayer(argument_queue, background_music, program)

    # Start threads for background music and news processing
    threading.Thread(target=background_music.start, daemon=True).start()
    threading.Thread(target=news_processor.start, daemon=True).start()
    threading.Thread(target=program.start, args=(program_audio_path, 3000, 3000, ), daemon=True).start()

    # Fetch processed news and enqueue them for playback
    def load_processed_news():
        while True:
            news = fetch_news_from_db(processed=True)
            for topic in news:
                argument_queue.put(topic)
            time.sleep(5)

    threading.Thread(target=load_processed_news, daemon=True).start()

    # Start podcast player
    asyncio.create_task(podcast_player.start())

    # Start WebSocket server in background
    asyncio.create_task(start_wss_server())


# Running the main function using asyncio
if __name__ == "__main__":
    asyncio.run(main())
