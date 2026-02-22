import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.environ.get("SPOTIFY_CLIENT_ID"),
    client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI"),
    scope="playlist-read-private playlist-read-collaborative"
))
try:
    playlists = sp.user_playlists('spotify')
    print("Spotify Playlists count:", len(playlists['items']))
except Exception as e:
    print(e)
