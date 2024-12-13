import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox


# Spotify API Setup
<<<<<<< HEAD
SPOTIFY_CLIENT_ID = '4a477e5b6497416bba8da1a7d68e4a7c' 
SPOTIFY_CLIENT_SECRET = 'f9b5f43e80ec4f7295a1b2aac662f5d2'
SPOTIFY_REDIRECT_URI = 'http://localhost:8888/callback'
=======
SPOTIFY_CLIENT_ID = 'YOUTUBE_API_KEY' 
SPOTIFY_CLIENT_SECRET = 'SPOTIFY_CLIENT_SECRET'
>>>>>>> def123edba66601537f0249641dabf7078cf775d

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private"
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

# Function to fetch user's playlists
def get_user_playlists():
    playlists = sp.current_user_playlists()
    return {item['name']: item['id'] for item in playlists['items']}

# Function to process tracks from a playlist
def process_playlist(playlist_id):
    tracks = sp.playlist_tracks(playlist_id)['items']
    for item in tracks:
        track = item['track']
        artist_name = track['artists'][0]['name']
        song_name = track['name']
        spotify_data = search_spotify(song_name, artist_name)

        if spotify_data:
            youtube_url = search_youtube(spotify_data['name'], spotify_data['artist'])
            if youtube_url:
                download_audio(youtube_url)

# GUI Application
def run_app():
    def fetch_playlists():
        playlists = get_user_playlists()
        playlist_var.set("Select a playlist")
        playlist_menu['menu'].delete(0, 'end')
        for name in playlists.keys():
            playlist_menu['menu'].add_command(
                label=name, 
                command=tk._setit(playlist_var, name)
            )
        global user_playlists
        user_playlists = playlists

    def download_playlist():
        selected_playlist = playlist_var.get()
        if selected_playlist == "Select a playlist":
            messagebox.showerror("Error", "Please select a playlist.")
            return

        playlist_id = user_playlists[selected_playlist]
        process_playlist(playlist_id)
        messagebox.showinfo("Success", "Playlist processed and downloads complete!")

    # GUI Setup
    root = tk.Tk()
    root.title("Spotify to MP3 Downloader")

    tk.Label(root, text="Spotify Playlists:").grid(row=0, column=0, padx=10, pady=5)

    playlist_var = tk.StringVar(root)
    playlist_var.set("Fetching playlists...")
    playlist_menu = tk.OptionMenu(root, playlist_var, "Fetching playlists...")
    playlist_menu.grid(row=0, column=1, padx=10, pady=5)

    fetch_button = tk.Button(root, text="Fetch Playlists", command=fetch_playlists)
    fetch_button.grid(row=1, column=0, columnspan=2, pady=10)

    download_button = tk.Button(root, text="Download Playlist", command=download_playlist)
    download_button.grid(row=2, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    user_playlists = {}
    run_app()
