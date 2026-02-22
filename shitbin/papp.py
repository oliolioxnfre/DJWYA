import spotipy
from spotipy.oauth2 import SpotifyOAuth

# 1. Setup your credentials (GET THESE FROM YOUR DASHBOARD)
CLIENT_ID = "82dac832ac914fbbb09196653244304f"
CLIENT_SECRET = "b31f8dfded994664af02b33fc14c820c"
REDIRECT_URI = "http://127.0.0.1:8000/callback"

# 2. Define "Scopes" (What data do we want?)
# user-top-read: Allows us to see their most listened-to artists
scope = "user-top-read user-library-read"

# 3. Initialize the "Handshake"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope
))

# 4. Pull the data!
print("Pulling your top EDM artists...")
# We are specifically asking for 'artists' here
results = sp.current_user_top_artists(limit=20, time_range='medium_term')

for i, item in enumerate(results['items']):
    # Use .get() instead of ['genres'] to avoid crashing if it's missing
    genres = item.get('genres', [])
    
    artist_name = item.get('name', 'Unknown Artist')
    
    if genres:
        genre_str = ", ".join(genres)
    else:
        genre_str = "No genres listed by Spotify"
        
    print(f"{i+1}. {artist_name} (Genres: {genre_str})")