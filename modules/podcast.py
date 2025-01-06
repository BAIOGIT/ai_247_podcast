import time
import threading
import asyncio
import json
import os
from pydub import AudioSegment
from pydub.playback import play
import websockets

class PodcastPlayer:
    def __init__(self, argument_queue, background_music, program, websocket_music_port=8765, websocket_news_port=8766):
        self.argument_queue = argument_queue
        self.program = program
        self.background_music = background_music
        self.websocket_music_port = websocket_music_port
        self.websocket_news_port = websocket_news_port
        self.current_song = None  # Store the current song name
        self.current_news = None  # Store the current news info
        self.music_clients = set()  # Store all connected WebSocket clients for music
        self.news_clients = set()  # Store all connected WebSocket clients for news

    async def start_music_websocket_server(self):
        """Starts a WebSocket server that sends updates about the current song."""
        async with websockets.serve(self._send_music_update, "localhost", self.websocket_music_port):
            await asyncio.Future()  # Run forever

    async def start_news_websocket_server(self):
        """Starts a WebSocket server that sends news updates."""
        async with websockets.serve(self._send_news_update, "localhost", self.websocket_news_port):
            await asyncio.Future()  # Run forever

    async def _send_music_update(self, websocket):
        """Sends the current track to connected WebSocket clients."""
        self.music_clients.add(websocket)  # Add the client to the list of connected clients
        try:
            while True:
                if self.background_music.get_current_track():
                    # Send the current track (song) information
                    current_track = self.background_music.get_current_track()
                    data = {"song": os.path.basename(current_track).split(".")[0]}
                    await websocket.send(json.dumps(data))  # Send data as a JSON string
                await asyncio.sleep(1)  # Send updates every second
        except websockets.exceptions.ConnectionClosed:
            print("Music WebSocket connection closed")
        finally:
            self.music_clients.remove(websocket)

    async def _send_news_update(self, websocket):
        """Sends the current news data to connected WebSocket clients."""
        self.news_clients.add(websocket)  # Add the client to the list of connected clients
        try:
            while True:
                if self.current_news:
                    # Send the current news content
                    data = {"news": self.current_news}
                    await websocket.send(json.dumps(data))  # Send data as a JSON string
                await asyncio.sleep(1)  # Send updates every second
        except websockets.exceptions.ConnectionClosed:
            print("News WebSocket connection closed")
        finally:
            self.news_clients.remove(websocket)

    def start(self):
        """Fetches processed audio files and plays them with background music."""
        # Start the WebSocket servers in separate threads
        music_thread = threading.Thread(target=self._start_music_websocket)
        music_thread.start()

        news_thread = threading.Thread(target=self._start_news_websocket)
        news_thread.start()

        while True:
            if not self.argument_queue.empty():
                news_info = self.argument_queue.get()
                audio_path = news_info["audio_path"]
                song_name = news_info["title"]  # Get the song name from the news info

                print(f"Playing processed news: {news_info['title']}")

                # Update the current song and news info for WebSocket clients
                self.current_song = song_name
                self.current_news = news_info["title"]  # Assuming the news content is in `news_info["content"]`

                try:
                    speech_audio = AudioSegment.from_file(audio_path)

                    # Override the background music smoothly before playing the news audio
                    self._override_background_music(speech_audio)
                    time.sleep(60)
                except Exception as e:
                    print(f"Error playing audio for news '{news_info['title']}': {e}")
                    
            else:
                time.sleep(1)

    def _start_music_websocket(self):
        """Start the music WebSocket server using asyncio."""
        asyncio.run(self.start_music_websocket_server())

    def _start_news_websocket(self):
        """Start the news WebSocket server using asyncio."""
        asyncio.run(self.start_news_websocket_server())

    def _override_background_music(self, speech_audio):
        fade_out_duration = 3500  # Duration for fade-out (milliseconds)
        fade_in_duration = 3500  # Duration for fade-in (milliseconds)

        # Check if background music or program audio is playing, if so, skip fades
        if not self.program.is_playing:
            print("Fading out background music before overriding...")
            self._fade_out_music(duration=fade_out_duration)
        else:
            print("Skipping fade-out, as program is already playing.")

        # Play the new audio (news or podcast)
        self._play_audio(speech_audio)
        
        # Only fade in the background music if no audio is playing
        if not self.program.is_playing:
            print("Fading in background music after overriding...")
            self._fade_in_music(duration=fade_in_duration)
        else:
            print("Skipping fade-in, as program is already playing.")

    def _play_audio(self, audio):
        """Plays the audio content passed to it."""
        self.background_music.set_news_playing(True)  # Set news playing status
        self.program.pause()  # Pause the program audio
        play(audio)
        self.background_music.set_news_playing(False)  # Set news playing status
        self.program.resume()  # Pause the program audio

    def _fade_out_music(self, duration=2000):
        """Fade the current volume down to 20% over the specified duration."""
        fade_steps = 20
        fade_step_duration = duration / fade_steps
        start_volume = self.background_music.get_volume()
        print(f"Fading out music from {start_volume} to 0.2 over {duration}ms.")
        target_volume = 0.2
        volume_change_per_step = (start_volume - target_volume) / fade_steps

        for i in range(fade_steps):
            new_volume = max(target_volume, start_volume - (volume_change_per_step * i))
            self.background_music.set_volume(new_volume)
            time.sleep(fade_step_duration / 1000.0)

    def _fade_in_music(self, duration=2000):
        """Fade the volume back to the original level over the specified duration."""
        fade_steps = 20
        fade_step_duration = duration / fade_steps
        start_volume = self.background_music.get_volume()
        print(f"Fading in music from {start_volume} to 1 over {duration}ms.")
        target_volume = 1  # Original volume before fade-out
        volume_change_per_step = (target_volume - start_volume) / fade_steps

        for i in range(fade_steps):
            new_volume = min(target_volume, start_volume + (volume_change_per_step * i))
            self.background_music.set_volume(new_volume)
            time.sleep(fade_step_duration / 1000.0)


