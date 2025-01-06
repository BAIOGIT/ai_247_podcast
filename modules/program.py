import time
import threading
from pydub import AudioSegment
from pydub.playback import play
import datetime
import queue

class Program:
    def __init__(self, background_music):
        self.background_music = background_music
        self.argument_queue = queue.Queue()
        self.is_playing = False  # Track if the program audio is playing

    def override_background_music(self, program_audio_path, fade_out_duration=3500, fade_in_duration=3500):
        """Override background music with a new program for a smooth transition."""
        print("Overriding background music...")
        try:
            # Check if something is already playing, if so, wait or skip the override
            if self.is_playing:
                print("Audio is already playing. Skipping override.")
                return

            speech_audio = AudioSegment.from_file(program_audio_path)

            # Check if background music or program audio is playing, if so, skip fades
            if not self.background_music.news_playing:
                print("Fading out background music before overriding...")
                # Fade out the background music
                self._fade_out_music(duration=fade_out_duration)
            else:
                print("Skipping fade-out, as news is already playing.")

            # Set the program as playing
            self.is_playing = True
            # self.background_music.stop()  # Stop background music

            # Play the program audio
            play(speech_audio)
            
            self.is_playing = False  # Reset the is_playing flag

            # Check if background music or program audio is playing, if so, skip fades
            if not self.background_music.news_playing:
                print("Fading in background music before overriding...")
                # Fade the background music back in
                self._fade_in_music(duration=fade_in_duration)
            else:
                print("Skipping fade-in, as news is already playing.")
                
            # self.background_music.start()  # Resume background music
            print("Program override complete.")
        except Exception as e:
            print(f"Error overriding background music: {e}")

    def _fade_out_music(self, duration=2000):
        """Fade out the background music smoothly to 10% of the current volume."""
        fade_steps = 20
        fade_step_duration = duration / fade_steps
        start_volume = self.background_music.get_volume()
        print(f"Fading out music from {start_volume} to 0.1 over {duration}ms.")
        target_volume = 0.1  # 20% of the current volume
        volume_change_per_step = (start_volume - target_volume) / fade_steps

        for i in range(fade_steps):
            new_volume = max(target_volume, start_volume - (volume_change_per_step * i))
            self.background_music.set_volume(new_volume)
            time.sleep(fade_step_duration / 1000.0)

    def _fade_in_music(self, duration=2000):
        """Fade in the background music smoothly back to its original volume."""
        fade_steps = 20
        fade_step_duration = duration / fade_steps
        start_volume = self.background_music.get_volume()  # Original volume before fade-out
        print(f"Fading in music from {start_volume} to 1 over {duration}ms.")
        target_volume = 1  # Starting at 10% of the target volume
        volume_change_per_step = (target_volume - start_volume) / fade_steps

        for i in range(fade_steps):
            new_volume = min(target_volume, start_volume + (volume_change_per_step * i))
            self.background_music.set_volume(new_volume)
            time.sleep(fade_step_duration / 1000.0)

    def launch_program_periodically(self, program_audio_path, fade_out_duration=3000, fade_in_duration=3000):
        """Launch the program override every 2 minutes at real hour intervals."""
        while True:
            # Get current time
            current_time = datetime.datetime.now()

            # Calculate the next multiple of 2 minutes within the current hour
            current_minute = current_time.minute
            next_trigger_minute = (current_minute // 2 + 1) * 2  # Calculate the next even minute
            if next_trigger_minute == 60:
                next_trigger_minute = 0  # If it's 60, reset to the top of the hour

            # Calculate how many seconds to wait until the next trigger time
            next_trigger_time = current_time.replace(minute=next_trigger_minute, second=0, microsecond=0)
            wait_time = (next_trigger_time - current_time).total_seconds()

            # If we are past the next trigger time, wait until the next hour's 2-minute mark
            if wait_time < 0:
                next_trigger_time = next_trigger_time.replace(hour=(current_time.hour + 1) % 24)
                wait_time = (next_trigger_time - current_time).total_seconds()

            print(f"Waiting for {wait_time} seconds until the next program launch at {next_trigger_time.strftime('%H:%M')}...")
            time.sleep(wait_time)  # Sleep until the next trigger time

            # Trigger the program override
            print("Launching program override...")
            self.override_background_music(program_audio_path, fade_out_duration, fade_in_duration)

    def start(self, program_audio_path, fade_out_duration=3000, fade_in_duration=3000):
        """Start the program and initiate periodic overrides."""
        # Start the periodic override process in a separate thread
        threading.Thread(target=self.launch_program_periodically, args=(program_audio_path, fade_out_duration, fade_in_duration), daemon=True).start()

        # Other program-related logic can go here
        while True:
            # Main loop to keep the program alive
            time.sleep(1)  # Keeps the program running

    def pause(self):
        self.running = False

    def resume(self):
        self.running = True
