import spotipy
from spotipy.oauth2 import SpotifyOAuth
from googleapiclient.discovery import build
import subprocess
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from io import BytesIO
from PIL import ImageTk, Image
import requests


# Spotify API Setup
SPOTIFY_CLIENT_ID = 'SPOTIFY_CLIENT_ID' 
SPOTIFY_CLIENT_SECRET = 'SPOTIFY_CLIENT_SECRET'
SPOTIFY_REDIRECT_URI = 'SPOTIFY_REDIRECT_URI'

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
        album_art_url = track['album']['images'][0]['url']  # Get highest res image
        return {
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'duration_ms': track['duration_ms'] // 1000,
            'album_art': album_art_url
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
def download_audio(youtube_url, spotify_data, output_path='downloads'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    command = [
        'yt-dlp',
        '-x', '--audio-format', 'mp3',
        '--embed-thumbnail', # Embed thumbnail in metadata (if available)
        '--output', f"{output_path}/%(title)s.%(ext)s",
        youtube_url
    ]
    subprocess.run(command)
    if spotify_data and spotify_data.get('album_art'):
        try:
            response = requests.get(spotify_data['album_art'])
            response.raise_for_status() # Raise an exception for bad status codes
            image = Image.open(BytesIO(response.content))
            image.save(f"{output_path}/{spotify_data['name']}.jpg")  # Save as jpg
        except requests.exceptions.RequestException as e:
            print(f"Error downloading album art: {e}")

#Function to get whether user wants to download individual song 
def download_individual_song():
    song_name = input("Enter the name of the song: ")
    artist_name = input("Enter the name of the artist: ")
    spotify_data = search_spotify(song_name, artist_name)
    if spotify_data:
        youtube_url = search_youtube(song_name, artist_name)
        if youtube_url:
            download_audio(youtube_url, spotify_data)
            print("Download complete!")
        else:
            print("Song not found on YouTube.")
    else:
        print("Song not found on Spotify.")
        
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
                download_audio(youtube_url, spotify_data)

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

    def download_individual_song():
        song_name = song_name_entry.get()
        artist_name = artist_name_entry.get()
        if not song_name or not artist_name:
            messagebox.showerror("Error", "Please enter both song name and artist name.")
            return
        spotify_data = search_spotify(song_name, artist_name)
        if spotify_data:
            youtube_url = search_youtube(spotify_data['name'], spotify_data['artist'])
            if youtube_url:
                download_audio(youtube_url, spotify_data)
                messagebox.showinfo("Success", "Download complete!")
            else:
                messagebox.showerror("Error", "Song not found on YouTube.")
        else:
            messagebox.showerror("Error", "Song not found on Spotify.")

    def add_cover_art():
        selected_playlist = playlist_var.get()
       
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

     # Individual song download section
    tk.Label(root, text="Download Individual Song:").grid(row=3, column=0, columnspan=2, pady=10)

    tk.Label(root, text="Song Name:").grid(row=4, column=0, padx=10, pady=5)
    song_name_entry = tk.Entry(root)
    song_name_entry.grid(row=4, column=1, padx=10, pady=5)

    tk.Label(root, text="Artist Name:").grid(row=5, column=0, padx=10, pady=5)
    artist_name_entry = tk.Entry(root)
    artist_name_entry.grid(row=5, column=1, padx=10, pady=5)

    individual_download_button = tk.Button(root, text="Download Song", command=download_individual_song)
    individual_download_button.grid(row=6, column=0, columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    user_playlists = {}
    run_app()
