import pylast
import spotipy
from spotipy.oauth2 import SpotifyOAuth


LASTFM_API_KEY = "278dd2789daa67c37bb1369fb6311bb2"
LASTFM_API_SECRET = "b63a70bf592daacaa90092b153ef6ca7" 
electronic_genres = [
    # --- PARENT: HOUSE ---
    'house', 'deep house', 'tech house', 'progressive house', 'future house', 
    'bass house', 'tropical house', 'electro house', 'acid house', 'g-house', 
    'afro house', 'organic house', 'chicago house', 'disco house', 'nu-disco',

    # --- PARENT: TECHNO ---
    'techno', 'minimal techno', 'hard techno', 'acid techno', 'dub techno', 
    'detroit techno', 'peak time techno', 'industrial techno', 'melodic techno', 
    'dark techno', 'hypnotic techno',

    # --- PARENT: TRANCE ---
    'trance', 'uplifting trance', 'psytrance', 'progressive trance', 'goa trance', 
    'vocal trance', 'tech trance', 'dream trance', 'hard trance',

    # --- PARENT: DRUM AND BASS ---
    'drum and bass', 'liquid dnb', 'neurofunk', 'jump-up', 'jungle', 
    'breakcore', 'halftime dnb', 'techstep', 'darkstep', 'atmospheric dnb',

    # --- PARENT: BASS MUSIC & DUBSTEP ---
    'dubstep', 'riddim', 'brostep', 'future bass', 'trap', 'wave', 
    'glitch hop', 'color bass', 'melodic dubstep', 'deathstep', 'uk garage', 
    'speed garage', '2-step',

    # --- PARENT: HARDSTYLE / HARDCORE ---
    'hardstyle', 'euphoric hardstyle', 'rawstyle', 'hardcore', 'gabber', 
    'happy hardcore', 'frenchcore', 'uptempo hardcore', 'hard dance',

    # --- PARENT: DOWNTEMPO / EXPERIMENTAL ---
    'downtempo', 'ambient', 'idm', 'trip-hop', 'chillstep', 'psydub', 
    'vaporwave', 'synthwave', 'illbient', 'ethereal',

    # --- MISC / HYBRID ---
    'hyperpop', 'eurodance', 'complextro', 'big room', 'hardwell style', 'phonk', 'edm', 'electronic', 'dance'
]

# Initialize the network
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

def get_artist_genres(artist_name):
    try:
        # 2. Get the artist object
        artist = network.get_artist(artist_name)
        
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
#my_genres = get_artist_genres("Skrillex")
#print(f"Skrillex Genres: {my_genres}")

def is_artist_electronic(artist_name):
    genres = get_artist_genres(artist_name)
    # Check if ANY of the artist's genres appear in our big electronic list
    return any(genre in electronic_genres for genre in genres)
    





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

'''
saved_tracks = []
results = sp.current_user_saved_tracks(limit=20) # 50 is the max Spotify allows per pull
for i in results['items']:
    print("Song: " + i['track']['name'])
    for artist in i['track']['artists']:
        print("Artist: " + artist['name'])
        print("Is Electronic: " + str(is_artist_electronic(artist['name'])))
        #make it so that if one of the artists is electronic than the other artist is also electronic
        if is_artist_electronic(artist['name']):
            print("Is Electronic: True")
        else:
            print("Is Electronic: False")
    print("\n") 
'''

results = sp.current_user_saved_tracks(limit=30) # 50 is the max Spotify allows per pull

electronic_artists = {}
for item in results['items']:
    track_artists = item['track']['artists']
    
    # Check if ANY artist on the track is electronic
    is_electronic_track = False
    for artist in track_artists:
        artist_id = artist['id']
        if artist_id in electronic_artists or is_artist_electronic(artist['name']):
            is_electronic_track = True
            break
            
    # If the track is electronic, add ALL its artists
    if is_electronic_track:
        for artist in track_artists:
            artist_id = artist['id']
            if artist_id not in electronic_artists:
                electronic_artists[artist_id] = {
                    "spotify_id": artist_id,
                    "name": artist['name'],
                    "count": 1
                }
            else:
                electronic_artists[artist_id]["count"] += 1
def print_entire_dict():
    for artist in electronic_artists.values():
        print(artist)

def print_electronic_artists():
    for artist in electronic_artists.values():
        print(f"{artist['name']} (Count: {artist['count']})")

print_electronic_artists()
#print_entire_dict()
#print(str(is_artist_electronic("swedm®")))

        