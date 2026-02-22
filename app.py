import pylast
import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_API_SECRET = os.environ.get("LASTFM_API_SECRET")

SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.environ.get("SPOTIFY_REDIRECT_URI")



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

#returns the top 7 genres for an artist
def get_artist_genres(artist_name):
    try:
        artist = network.get_artist(artist_name)
        top_tags = artist.get_top_tags(limit=7)
        
        #Extract just the names
        genres = [tag.item.get_name().lower() for tag in top_tags]
        
        return genres
    except Exception as e:
        print(f"Couldn't find genres for {artist_name}")
        return []

#returns true if the artist has any electronic genres
def is_artist_electronic(artist_name):
    genres = get_artist_genres(artist_name)
    return any(genre in electronic_genres for genre in genres)

#Returns genres only if they have electronic genres
def get_electronic_genres(artist_name):
    genres = get_artist_genres(artist_name)
    for genre in genres:
        if genre in electronic_genres:
            return genres
    




#--------------------------------Spotify Integration --------------------------------------
scope = "user-library-read "

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
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
                    "count": 1,
                    "genres": get_electronic_genres(artist['name'])
                }
            else:
                electronic_artists[artist_id]["count"] += 1
def print_entire_dict():
    for artist in electronic_artists.values():
        print(artist)

def print_electronic_artists():
    for artist in electronic_artists.values():
        print(f"{artist['name']} (Dectected as Electronic: {is_artist_electronic(artist['name'])}) (Count: {artist['count']})")

#print_electronic_artists()
#print(get_electronic_genres("Nakeesha"))




#--------------------------------Set Conversion + Festival Matching --------------------------------------
# Convert the user's artists into a "Set"
user_artists = set([artist['name'] for artist in electronic_artists.values()])

# 2. Load the Mock Festivals into a dictionary
festivals = {}
with open('mock_festivals.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        fest = row['festival_name']
        artist = row['artist_name']
        
        if fest not in festivals:
            festivals[fest] = set() # Using a set here too
        festivals[fest].add(artist)

# 3. The Comparison Engine

match_scores = []

for fest_name, lineup in festivals.items():
    # Find the overlapping artists using the "&" operator
    overlap = user_artists & lineup
    
    # Calculate what percentage of the festival the user already likes
    match_percentage = (len(overlap) / len(lineup)) * 100
    
    match_scores.append({
        'festival': fest_name,
        'score': match_percentage,
        'shared_artists': list(overlap)
    })

# 4. Sort and Print the results (Highest score first)
match_scores.sort(key=lambda x: x['score'], reverse=True)

def print_match_scores():
    print("\n--- FESTIVAL MATCH RESULTS ---")
    for match in match_scores:
        print(f"{match['festival']}: {match['score']:.1f}% Match")
        print(f"   Artists you know: {', '.join(match['shared_artists'])}\n")

#print_electronic_artists()
#print_entire_dict()
#print(str(is_artist_electronic("swedm®")))

#--------------------------------Supabase Integration --------------------------------------



url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def sync_to_supabase(artist_list, user_id="demo_user"):
    for item in artist_list:
        # --- PART A: Update the Global Artist Dictionary ---
        # We only send info that is "Universal" to this table
        artist_metadata = {
            "spotify_id": item['spotify_id'],
            "name": item['name'],
            "genres": get_electronic_genres(item['name'])
        }
        
        # .upsert() means "Insert if new, do nothing if already exists"
        supabase.table("artists").upsert(artist_metadata).execute()

        # --- PART B: Update your Personal Library ---
        # This links YOU to that artist and saves your specific song count
        library_data = {
            "user_id": user_id,
            "artist_id": item['spotify_id'],
            "count": item['count']
        }
        
        # We use a unique constraint in Supabase so this doesn't create 
        # duplicate rows for the same user/artist combo
        supabase.table("user_lib").upsert(library_data, on_conflict="user_id,artist_id").execute()
        
        print(f"Synced {item['name']} to your cloud library.")

# RUN IT
sync_to_supabase(electronic_artists.values())
        