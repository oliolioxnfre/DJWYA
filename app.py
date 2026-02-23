import pylast
import csv
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from classifier import GenreClassifier
from classifier import VibeClassifier

load_dotenv()

LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_API_SECRET = os.environ.get("LASTFM_API_SECRET")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")



electronic_genres = [
    # --- PARENT: HOUSE ---
    'house', 'deep-house', 'tech-house', 'progressive-house', 'future-house', 
    'bass-house', 'tropical-house', 'electro-house', 'acid-house', 'g-house', 
    'afro-house', 'organic-house', 'chicago-house', 'disco-house', 'nu-disco', 
    'lo-fi-house', 'funky-house', 'hard-house', 'jazz-house', 'rally-house', 
    'melodic-house', 'speed-house', 'ghetto-house', 'witch-house',
    'future-funk', 'liquid-funk', 'digicore', 'french-house', 'chiptune', 'breakbeat',
    'uk-garage', 'melodic-dubstep', 'garage',

    # --- PARENT: TECHNO ---
    'techno', 'minimal-techno', 'hard-techno', 'acid-techno', 'dub-techno', 
    'detroit-techno', 'peak-time-techno', 'industrial-techno', 'melodic-techno', 
    'dark-techno', 'hypnotic-techno', 'cyber-house',

    # --- PARENT: TRANCE ---
    'trance', 'uplifting-trance', 'psytrance', 'progressive-trance', 'goa-trance', 
    'vocal-trance', 'tech-trance', 'dream-trance', 'hard-trance', 'hypertrance', 
    'neotrance', 'acid-trance',

    # --- PARENT: DRUM AND BASS ---
    'drum-and-bass', 'drum-n-bass', 'liquid-dnb', 'neurofunk', 'jump-up', 'jungle', 
    'breakcore', 'halftime-dnb', 'techstep', 'darkstep', 'atmospheric-dnb', 'dnb',
    'atmospheric-jungle',

    # --- PARENT: BASS MUSIC & DUBSTEP ---
    'dubstep', 'riddim', 'brostep', 'future-bass', 'j-core', 'trap', 'wave', 
    'glitch-hop', 'color-bass', 'melodic-dubstep', 'deathstep', 'uk-garage', 
    'speed-garage', '2-step', 'melodic-bass', 'glitchcore', 'bass', 'glitch',
    'moombahton', 'midtempo-bass', 'hardwave', 'drift-phonk', 'juke', 'footwork',
    'grime', 'dub',

    # --- PARENT: HARD DANCE / HARDCORE ---
    'hardstyle', 'euphoric-hardstyle', 'rawstyle', 'gabber', 
    'happy-hardcore', 'frenchcore', 'uptempo-hardcore', 'hard-dance',
    'hard-bass', 'donk', 'bounce', 'scouse-house', 'nightcore',

    # --- PARENT: DOWNTEMPO / EXPERIMENTAL ---
    'downtempo', 'idm', 'trip-hop', 'chillstep', 'psydub', 
    'vaporwave', 'synthwave', 'illbient', 'ethereal', 'electronica', 'chillout', 
    'ambient', 'dream-pop', 'outrun', 'retrowave', 'chillsynth', 'musique-concrete',
    'deconstructed-club',

    # --- MISC / HYBRID ---
    'hyperpop', 'eurodance', 'complextro', 'big-room', 'hardwell-style', 
    'phonk', 'edm', 'electronic', 'synthpop', 'electropop',
    'rave', 'rave-techno',
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
        # Lowercase and replace spaces with dashes for normalization
        genres = [tag.item.get_name().lower().replace(" ", "-") for tag in top_tags]
        artist_genre_cache[artist_name] = genres
        return genres
    except Exception as e:
        artist_genre_cache[artist_name] = [] # Cache empty to prevent retrying failures
        return []

def get_electronic_genres(genres):
    return [genre for genre in genres if genre in electronic_genres]


#-------------------------------- CLI AUTH & SETUP --------------------------------------
# Initialize Supabase first so we can verify the user before processing
supabase: Client = create_client(url, key)
resolved_user_id = None
target_csv_file = None

print(f"--- DJWYA App Sync ---")
while True:
    username = input("Enter your DJWYA username: ").strip()
    if not username: continue
    
    response = supabase.table("public.users").select("id").eq("username", username).execute()
    if not response.data:
        print(f"❌ User '{username}' not found in Supabase. Please try again or create them in user.py")
        continue
        
    resolved_user_id = response.data[0]['id']
    print(f"✅ Welcome back, {username}!\n")
    break
    
while True:
    file_input = input("Enter the name of your liked songs CSV file (e.g. Max_Songs): ").strip()
    if not file_input: continue
    
    # Append .csv if the user didn't type it
    if not file_input.lower().endswith('.csv'):
        file_input += '.csv'
        
    target_csv_file = f"liked_songs/{file_input}"
    if not os.path.exists(target_csv_file):
        print(f"❌ Could not find file at '{target_csv_file}'. Please check the name and try again.")
        continue
        
    print(f"✅ Found {target_csv_file}. Starting analysis...\n")
    break


#--------------------------------Local CSV Integration --------------------------------------

electronic_artists = {}

try:
    with open(target_csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        print("Parsing Local Liked Songs CSV...")
        
        # We iterate over every row in the liked songs csv
        for row in reader:
            raw_artists = row.get("Artist Name(s)", "")
            csv_genres_raw = row.get("Genres", "")
            
            # 1. Properly split the artists since some tracks have multiple artists separated by ';'
            track_artists = [a.strip() for a in raw_artists.split(';') if a.strip()]
            
            csv_genres_list = []
            if csv_genres_raw:
                # Replace spaces with dashes for normalization
                csv_genres_list = [g.strip().lower().replace(" ", "-") for g in csv_genres_raw.split(',') if g.strip()]
            
            # We iterate over every artist on the track independently
            for artist_name in track_artists:
                # 1. If we already validated them previously, just increment
                if artist_name in electronic_artists:
                    electronic_artists[artist_name]["count"] += 1
                    continue
                
                # 2. They are new. Fetch their raw Last.fm genres.
                lastfm_genres = get_artist_genres(artist_name)
                
                # 3. Check if Last.fm yielded any electronic genres
                electronic_matches = get_electronic_genres(lastfm_genres)
                
                if electronic_matches:
                    # They have electronic Last.fm tags, add them!
                    electronic_artists[artist_name] = {
                        "name": artist_name,
                        "count": 1,
                        "genres": lastfm_genres,
                        "vibe_bucket": GenreClassifier.classify(lastfm_genres),
                        "sonic_dna": VibeClassifier.get_artist_vibe(lastfm_genres)
                    }
                else:
                    # 4. No electronic Last.fm tags found. Do the CSV track tags contain any?
                    csv_electronic_matches = get_electronic_genres(csv_genres_list)
                    
                    if csv_electronic_matches:
                        # The track ITSELF is electronic. Assign the track's CSV tags to the artist.
                        electronic_artists[artist_name] = {
                            "name": artist_name,
                            "count": 1,
                            "genres": csv_genres_list, # They inherit the track's full tags
                            "vibe_bucket": GenreClassifier.classify(csv_genres_list),
                            "sonic_dna": VibeClassifier.get_artist_vibe(csv_genres_list)
                        }
                    # 5. If STILL no (meaning Last.fm isn't electronic AND track isn't electronic),
                    # they are completely skipped! (e.g. an unrelated rap track)
            
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
"""
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
"""
#--------------------------------Supabase Integration --------------------------------------

def sync_to_supabase(artist_dict, user_id):
    for item in artist_dict.values():
        name_slug = item['name'].lower().replace(" ", "-")
        # --- PART A: Update the Global Artist Dictionary ---
        artist_metadata = {
            "name": item['name'],
            "name_slug": name_slug,
            "genres": item.get('genres', []),
            "vibe_bucket": item.get('vibe_bucket', []),
            "sonic_dna": item.get('sonic_dna', {})
        }
        
        # Check if artist already exists to get their UUID
        existing_artist = supabase.table("artists").select("id").eq("name_slug", name_slug).execute()
        
        if existing_artist.data and len(existing_artist.data) > 0:
            artist_id = existing_artist.data[0]['id']
            # Update the existing artist with the new classification metrics
            supabase.table("artists").update(artist_metadata).eq("id", artist_id).execute()
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
    VibeClassifier.update_user_dna(resolved_user_id)
# RUN IT
sync_to_supabase(electronic_artists, resolved_user_id)

