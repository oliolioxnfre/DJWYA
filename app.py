import pylast
import csv
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_API_SECRET = os.environ.get("LASTFM_API_SECRET")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")



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

    # --- PARENT: HARD DANCE / HARDCORE ---
    'hardstyle', 'euphoric hardstyle', 'rawstyle', 'gabber', 
    'happy hardcore', 'frenchcore', 'uptempo hardcore', 'hard dance',

    # --- PARENT: DOWNTEMPO / EXPERIMENTAL ---
    'downtempo', 'ambient', 'idm', 'trip-hop', 'chillstep', 'psydub', 
    'vaporwave', 'synthwave', 'illbient', 'ethereal',

    # --- MISC / HYBRID ---
    'hyperpop', 'eurodance', 'complextro', 'big room', 'hardwell style', 
    'phonk', 'edm', 'electronic'
]

no_exception_genres = [
    'rap', 'hip hop', 'r&b', 'soul', 'blues', 'rock', 
    'metal', 'punk', 'country', 'folk', 'reggae', 'latin', 'world', 'classical', 
    'soundtrack', 'gospel', 'pop', 'indie', 'pop rock', 'pop punk', 'pop metal',
    'emo', 'post-punk', 'post-rock', 'shoegaze', 'slowcore', '90s emo', 'hardcore'
]

# Initialize the network
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

# Cache to prevent doing redundant Last.FM API calls
artist_genre_cache = {}

# returns the top 7 genres for an artist
def get_artist_genres(artist_name):
    if artist_name in artist_genre_cache:
        return artist_genre_cache[artist_name]
    try:
        artist = network.get_artist(artist_name)
        top_tags = artist.get_top_tags(limit=7)
        genres = [tag.item.get_name().lower() for tag in top_tags]
        artist_genre_cache[artist_name] = genres
        return genres
    except Exception as e:
        artist_genre_cache[artist_name] = [] # Cache empty to prevent retrying failures
        return []

# returns true if the artist has any electronic genres
def is_artist_electronic(artist_name):
    genres = get_artist_genres(artist_name)
    return any(genre in electronic_genres for genre in genres)

def has_denied_genres(artist_name):
    genres = get_artist_genres(artist_name)
    return any(genre in no_exception_genres for genre in genres)
    




#--------------------------------Local CSV Integration --------------------------------------

electronic_artists = {}

try:
    with open("liked_songs/liked_songs.csv", mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        print("Parsing Local Liked Songs CSV...")
        
        # We iterate over every row in the liked songs csv
        for row in reader:
            raw_artists = row.get("Artist Name(s)", "")
            
            # 1. Properly split the artists since some tracks have multiple artists separated by ';'
            track_artists = [a.strip() for a in raw_artists.split(';') if a.strip()]
            
            # Check if ANY artist on the track is electronic
            is_electronic_track = False
            for artist_name in track_artists:
                # Cache lookup or Last.fm call
                if artist_name in electronic_artists or is_artist_electronic(artist_name):
                    is_electronic_track = True
                    break
                    
            # If the track is electronic, add ALL its artists unless they are denied
            if is_electronic_track:
                for artist_name in track_artists:
                    if artist_name in electronic_artists:
                        electronic_artists[artist_name]["count"] += 1
                    else:
                        _is_electronic = is_artist_electronic(artist_name)
                        _has_denied = has_denied_genres(artist_name)
                        
                        # They get in if they have electronic tags OR if they don't have denied tags
                        if _is_electronic or not _has_denied:
                            electronic_artists[artist_name] = {
                                "name": artist_name,
                                "count": 1,
                                "genres": get_artist_genres(artist_name)
                            }
                        
            
except FileNotFoundError:
    print("Could not find liked_songs/liked_songs.csv")

def print_entire_dict():
    for artist in electronic_artists.values():
        print(artist)

def print_electronic_artists():
    for artist_name, artist_data in electronic_artists.items():
        print(f"{artist_name} (Detected as Electronic: True) (Count: {artist_data['count']})")

print_electronic_artists()
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
 



supabase: Client = create_client(url, key)

def sync_to_supabase(artist_list, user_id="demo_user"):
    for item in artist_list:
        name_slug = item['name'].lower().replace(" ", "-")
        # --- PART A: Update the Global Artist Dictionary ---
        artist_metadata = {
            "name": item['name'],
            "name_slug": name_slug,
            "genres": item.get('genres', [])
        }
        
        # Check if artist already exists to get their UUID
        existing_artist = supabase.table("artists").select("id").eq("name_slug", name_slug).execute()
        
        if existing_artist.data and len(existing_artist.data) > 0:
            artist_id = existing_artist.data[0]['id']
        else:
            # Insert new artist and get the generated UUID
            inserted_artist = supabase.table("artists").insert(artist_metadata).execute()
            if inserted_artist.data:
                artist_id = inserted_artist.data[0]['id']
            else:
                print(f"Failed to insert artist {item['name']}")
                continue

        # --- PART B: Update your Personal Library ---
        # This links YOU to that artist and saves your specific song count
        library_data = {
            "user_id": user_id,
            "artist_id": artist_id,
            "count": item['count']
        }
        
        # We use a unique constraint in Supabase so this doesn't create 
        # duplicate rows for the same user/artist combo
        supabase.table("user_lib").upsert(library_data, on_conflict="user_id,artist_id").execute()
        
        print(f"Synced {item['name']} to your cloud library.")

# RUN IT
sync_to_supabase(electronic_artists.values())
        