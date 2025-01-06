import os
import random
import pygame
from pydub import AudioSegment

class BackgroundMusic:
    def __init__(self, playlist_folder):
        self.playlist_folder = playlist_folder
        self.playlists = self._load_playlists()
        self.current_volume = 1.0
        self.news_playing = False
        self.running = True
        self.current_track = None

        pygame.mixer.init()

    def _load_playlists(self):
        return [
            os.path.join(self.playlist_folder, folder)
            for folder in os.listdir(self.playlist_folder)
            if os.path.isdir(os.path.join(self.playlist_folder, folder))
        ]

    def _get_songs_from_playlist(self, playlist):
        return [
            os.path.join(playlist, song)
            for song in os.listdir(playlist)
            if os.path.isfile(os.path.join(playlist, song))
        ]

    def _play_song(self, file_path):
        try:
            self.current_track = file_path  # Track the current song path
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.current_volume)
            pygame.mixer.music.play()
            print(f"Now playing: {file_path}")
            while pygame.mixer.music.get_busy() and self.running:
                pygame.mixer.music.set_volume(self.current_volume)
                pygame.time.Clock().tick(10)
        except Exception as e:
            print(f"Error playing {file_path}: {e}")

    def start(self):
        while self.running:
            random.shuffle(self.playlists)
            for playlist in self.playlists:
                if not self.running:
                    break
                print(f"Switching to playlist: {playlist}")
                songs = self._get_songs_from_playlist(playlist)
                random.shuffle(songs)
                for song in songs:
                    if not self.running:
                        break
                    self._play_song(song)

    def stop(self):
        self.running = False
        pygame.mixer.music.stop()

    def get_volume(self):
        """Returns the current volume level."""
        return self.current_volume
    
    def set_volume(self, volume):
        self.current_volume = volume
        pygame.mixer.music.set_volume(self.current_volume)

    def get_current_track(self):
        """Returns the current track name or path."""
        return self.current_track

    def set_news_playing(self, status):
        self.news_playing = status