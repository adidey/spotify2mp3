import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import subprocess
import os
import tkinter as tk
from tkinter import messagebox

# Spotify API Setup
SPOTIFY_CLIENT_ID = 'YOUTUBE_API_KEY' 
SPOTIFY_CLIENT_SECRET = 'SPOTIFY_CLIENT_SECRET'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# YouTube API Setup
YOUTUBE_API_KEY = 'YOUTUBE_API_KEY'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Function to search for a song on Spotify
def search_spotify(song_name, artist_name):
    query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=query, limit=1, type='track')
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'duration_ms': track['duration_ms'] // 1000
        }
    return None

# Function to search YouTube for the song
def search_youtube(song_name, artist):
    query = f"{song_name} {artist} official audio"
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=1
    )
    response = request.execute()
    if response['items']:
        return f"https://www.youtube.com/watch?v={response['items'][0]['id']['videoId']}"
    return None

# Function to download audio using yt-dlp
def download_audio(youtube_url, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    command = [
        'yt-dlp',
        '-x', '--audio-format', 'mp3',
        '--output', f"{output_path}/%(title)s.%(ext)s",
        youtube_url
    ]
    subprocess.run(command)

# GUI Application
def run_app():
    def search_song():
        artist_name = artist_entry.get()
        song_name = song_entry.get()

        if not artist_name or not song_name:
            messagebox.showerror("Error", "Please enter both artist and song name.")
            return

        spotify_data = search_spotify(song_name, artist_name)

        if spotify_data:
            result_label.config(text=f"Spotify: {spotify_data['name']} by {spotify_data['artist']}")
            youtube_url = search_youtube(spotify_data['name'], spotify_data['artist'])

            if youtube_url:
                youtube_label.config(text=f"YouTube: {youtube_url}")
                download_button.config(state=tk.NORMAL)
                global current_youtube_url
                current_youtube_url = youtube_url
            else:
                youtube_label.config(text="YouTube: No match found.")
                download_button.config(state=tk.DISABLED)
        else:
            result_label.config(text="Spotify: No match found.")
            youtube_label.config(text="")
            download_button.config(state=tk.DISABLED)

    def download_song():
        if current_youtube_url:
            download_audio(current_youtube_url)
            messagebox.showinfo("Success", "Download complete!")
        else:
            messagebox.showerror("Error", "No song to download.")

    # GUI Setup
    root = tk.Tk()
    root.title("Spotify to MP3 Downloader")

    tk.Label(root, text="Artist Name:").grid(row=0, column=0, padx=10, pady=5)
    artist_entry = tk.Entry(root, width=30)
    artist_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(root, text="Song Name:").grid(row=1, column=0, padx=10, pady=5)
    song_entry = tk.Entry(root, width=30)
    song_entry.grid(row=1, column=1, padx=10, pady=5)

    search_button = tk.Button(root, text="Search", command=search_song)
    search_button.grid(row=2, column=0, columnspan=2, pady=10)

    result_label = tk.Label(root, text="", wraplength=400, justify="left")
    result_label.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    youtube_label = tk.Label(root, text="", wraplength=400, justify="left")
    youtube_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5)

    download_button = tk.Button(root, text="Download", state=tk.DISABLED, command=download_song)
    download_button.grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    current_youtube_url = None
    run_app()
