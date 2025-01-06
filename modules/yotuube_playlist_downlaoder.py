from yt_dlp import YoutubeDL

def download_playlist(playlist_url, output_path="./data/playlist/downloads"):
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{output_path}/%(playlist_title)s/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

# Example usage

playlist_urls = [
    "https://www.youtube.com/watch?v=90dQQYp2QWM&list=PLKguDdSlO3ZYVR8Sb7KNBzgWo6dLe89S2",
    "https://www.youtube.com/watch?v=N05Bo0xZYKE&list=PLRa8CX71ZOLHefdhOjZVUWInniYA6ckVu",
    "https://www.youtube.com/watch?v=K2ku1A5Ox8U&list=PLPaEI-ja7rWNY8kYVc1qvUixNNLmSrJdS",
    "https://www.youtube.com/watch?v=dJUrK1ghZic&list=PLvhPX5BBWjyzYB3T7GRc7SlH2XSxd7yTj",
    "https://www.youtube.com/watch?v=zjvIy7PLx_U&list=PLGne1an2Cq4f1sknUhxW2BIOD91IjfbXK"
]

for playlist_url in playlist_urls:
    try:
        download_playlist(playlist_url)
    except Exception as e:
        print(f"An error occurred while downloading the playlist: {e}")
    finally:
        print(f"Playlist download completed: {playlist_url}")