import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from googleapiclient.discovery import build
import subprocess
import os

# Spotify API Setup
SPOTIFY_CLIENT_ID = '4a477e5b6497416bba8da1a7d68e4a7c'
SPOTIFY_CLIENT_SECRET = 'f9b5f43e80ec4f7295a1b2aac662f5d2'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# YouTube API Setup
YOUTUBE_API_KEY = 'AIzaSyB0XyaohMpUpSL_64iFD96YPCukp-lJsIQ'
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Function to search for a song on Spotify
def search_spotify(song_name):
    results = sp.search(q=song_name, limit=1, type='track')
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
    query = f"{song_name} {artist}"
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

# Main workflow
if __name__ == "__main__":
    song_name = input("Enter the Spotify song name: ")
    spotify_data = search_spotify(song_name)

    if spotify_data:
        print(f"Found on Spotify: {spotify_data['name']} by {spotify_data['artist']}")
        youtube_url = search_youtube(spotify_data['name'], spotify_data['artist'])

        if youtube_url:
            print(f"Found on YouTube: {youtube_url}")
            download_audio(youtube_url)
            print("Download complete!")
        else:
            print("No matching video found on YouTube.")
    else:
        print("Song not found on Spotify.")
