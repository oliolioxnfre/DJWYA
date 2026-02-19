import pylast
import spotipy
from spotipy.oauth2 import SpotifyOAuth


LASTFM_API_KEY = "278dd2789daa67c37bb1369fb6311bb2"
LASTFM_API_SECRET = "b63a70bf592daacaa90092b153ef6ca7" 

# Initialize the network
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

def get_artist_genres(artist_name):
    try:
        # 2. Get the artist object
        artist = network.get_artist(artist_name)
        artistid = artist.get_mbid()
        print(artistid)
        
        # 3. Get the top tags (genres) assigned to this artist
        # Last.fm returns these as a list of "TopItem" objects
        top_tags = artist.get_top_tags(limit=7)
        
        # 4. Extract just the names
        # e.g., ['dubstep', 'electronic', 'bass music']
        genres = [tag.item.get_name().lower() for tag in top_tags]
        
        return genres
    except Exception as e:
        print(f"Couldn't find genres for {artist_name}")
        return []

# TEST IT:
my_genres = get_artist_genres("Subtronics")

print(f"Subtronics Genres: {my_genres}")


def get_song_genres(artist_name, song_name):
    try:
        # 2. Get the artist object
        song = network.get_track(artist_name, song_name)
        
        # 3. Get the top tags (genres) assigned to this artist
        # Last.fm returns these as a list of "TopItem" objects
        top_tags = song.get_top_tags(limit=7)
        
        # 4. Extract just the names
        # e.g., ['dubstep', 'electronic', 'bass music']
        genres = [tag.item.get_name().lower() for tag in top_tags]
        
        return genres
    except Exception as e:
        print(f"Couldn't find genres for {song_name}")
        return []

my_song_genres = get_song_genres("Subtronics", "Griztronics")

print(f"Griztronics Genres: {my_song_genres}")



SPOTIFY_CLIENT_ID = "82dac832ac914fbbb09196653244304f"
SPOTIFY_CLIENT_SECRET = "b31f8dfded994664af02b33fc14c820c"
REDIRECT_URI = "http://127.0.0.1:8000/callback"

# NEW SCOPE: We need permission to read your "Saved Tracks" (Liked Songs)
scope = "user-library-read "

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

# 2. Hardcode the target genre
target_genre = 'electronic'
print(f"Target Genre: {target_genre}")
print(f"\nFetching your Liked Songs... (This might take a minute if you have thousands)")

# 3. Pull ALL Liked Songs (Handling Pagination)
saved_tracks = []
results = sp.current_user_saved_tracks(limit=10) # 50 is the max Spotify allows per pull
for i in results['items']:
    print("Song: " + i['track']['name'])
    for artist in i['track']['artists']:
        print("Artist: " + artist['name'])
        print("Genre: " + artist['id'])
    print("\n")
    
