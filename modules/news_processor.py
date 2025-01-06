import time
import os
from TTS.api import TTS
from modules.utils.db import fetch_news_from_db, update_news_status

class NewsProcessor:
    def __init__(self, voice_model, speaker_wav_path):
        self.tts = TTS(voice_model)
        self.tts.synthesizer.tts_model.length_scale = 1.05
        self.speaker_wav_path = speaker_wav_path
        self.output_dir = "./generated/speech/news"  # Directory for generated audio
        os.makedirs(self.output_dir, exist_ok=True)

    def _create_podcast_script(self, title):
        """Generates a podcast script based on the title."""
        return f"Today's title is {title}. Let's dive into it."

    def _generate_speech(self, title):
        """Generates TTS audio for the given title."""
        script = self._create_podcast_script(title)
        file_path = os.path.join(self.output_dir, f"{title.replace(' ', '_')}.wav")
        print(f"Generating speech for title: {title}")
        self.tts.tts_to_file(text=script, speaker_wav=self.speaker_wav_path, language="en", file_path=file_path)
        return file_path

    def start(self):
        """Continuously fetches and processes news titles."""
        while True:
            news_items = fetch_news_from_db(processed=False)  # Fetch unprocessed news
            if not news_items:
                print("No new news items to process. Waiting...")
                time.sleep(5)
                continue

            for news in news_items:
                title = news["title"]  # Assuming the returned dictionary has a 'title' key
                try:
                    audio_path = self._generate_speech(title)
                    update_news_status(title, processed=True, audio_path=audio_path)
                    print(f"Processed news: {title}, audio saved at {audio_path}")
                except Exception as e:
                    print(f"Error processing news '{title}': {e}")
