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

def print_entire_dict():
    for artist in electronic_artists.values():
        print(artist)

def print_electronic_artists():
    for artist_name, artist_data in electronic_artists.items():
        print(f"{artist_name} (Detected as Electronic: True) (Count: {artist_data['count']})")

def get_electronic_genres(genres):
    return [genre for genre in genres if genre in electronic_genres]

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


# Global Supabase Client
supabase: Client = create_client(url, key)
resolved_user_id = None

def sync_to_supabase(artist_dict, user_id):
    """Syncs the analyzed electronic artists to the Supabase database."""
    if not artist_dict:
        print("⚠️ No electronic artists found to sync.")
        return

    print(f"🚀 Syncing {len(artist_dict)} artists to Supabase...")
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
            # Update the existing artist
            supabase.table("artists").update(artist_metadata).eq("id", artist_id).execute()
        else:
            # Insert new artist
            inserted_artist = supabase.table("artists").insert(artist_metadata).execute()
            if inserted_artist.data:
                artist_id = inserted_artist.data[0]['id']
            else:
                print(f"❌ Failed to insert artist {item['name']}")
                continue

        # --- PART B: Update Personal Library ---
        library_data = {
            "user_id": user_id,
            "artist_id": artist_id,
            "count": item['count']
        }
        
        supabase.table("user_lib").upsert(library_data, on_conflict="user_id,artist_id").execute()
        print(f"  ✅ Synced: {item['name']}")
    
    # Finally, update the aggregate User DNA in the users table
    VibeClassifier.update_user_dna(user_id)
    print("\n✨ Finished Syncing to Supabase!")

def add_playlist(user_id):
    """Prompts for a CSV and processes it."""
    while True:
        file_input = input("\nEnter CSV filename from 'liked_songs' (e.g. Max_Songs) or 'b' to go back: ").strip()
        if file_input.lower() == 'b': return
        if not file_input: continue
        
        if not file_input.lower().endswith('.csv'):
            file_input += '.csv'
            
        target_csv_file = f"liked_songs/{file_input}"
        if not os.path.exists(target_csv_file):
            print(f"❌ Error: File '{target_csv_file}' not found.")
            continue
            
        print(f"📂 Analyzing {target_csv_file}...")
        break

    electronic_artists = {}
    try:
        with open(target_csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                raw_artists = row.get("Artist Name(s)", "")
                csv_genres_raw = row.get("Genres", "")
                track_artists = [a.strip() for a in raw_artists.split(';') if a.strip()]
                
                csv_genres_list = []
                if csv_genres_raw:
                    csv_genres_list = [g.strip().lower().replace(" ", "-") for g in csv_genres_raw.split(',') if g.strip()]
                
                for artist_name in track_artists:
                    if artist_name in electronic_artists:
                        electronic_artists[artist_name]["count"] += 1
                        continue
                    
                    lastfm_genres = get_artist_genres(artist_name)
                    electronic_matches = get_electronic_genres(lastfm_genres)
                    
                    if electronic_matches:
                        electronic_artists[artist_name] = {
                            "name": artist_name,
                            "count": 1,
                            "genres": lastfm_genres,
                            "vibe_bucket": GenreClassifier.classify(lastfm_genres),
                            "sonic_dna": VibeClassifier.get_artist_vibe(lastfm_genres)
                        }
                    else:
                        csv_electronic_matches = get_electronic_genres(csv_genres_list)
                        if csv_electronic_matches:
                            electronic_artists[artist_name] = {
                                "name": artist_name,
                                "count": 1,
                                "genres": csv_genres_list,
                                "vibe_bucket": GenreClassifier.classify(csv_genres_list),
                                "sonic_dna": VibeClassifier.get_artist_vibe(csv_genres_list)
                            }
        sync_to_supabase(electronic_artists, user_id)
    except Exception as e:
        print(f"❌ Critical Error during sync: {e}")

def check_sonic_dna(user_id):
    """Fetches user DNA and triggers the radar chart."""
    from radarchart import fetch_user_dna, visualize_vibes
    dna = fetch_user_dna(user_id)
    if dna:
        visualize_vibes([{'name': 'My Profile', 'dna': dna, 'count': 1}], user_id)
    else:
        print("❌ No Sonic DNA found. Try adding a playlist first!")

def show_menu():
    """Prints a premium styled menu."""
    print("\n" + "="*40)
    print("      🎧 DJWYA CONTROL CENTER 🎧")
    print("="*40)
    print(" 1. ➕ Add New Playlist (CSV Sync)")
    print(" 2. ➖ Remove Playlist (Coming Soon)")
    print(" 3. 🎪 Find Festival Matches (Coming Soon)")
    print(" 4. 🧬 Check My Sonic DNA")
    print(" 5. 📊 View Favorite Genres (Coming Soon)")
    print(" 6. 🎙️ View Favorite Artists (Coming Soon)")
    print("-" * 40)
    print(" 9. 🚪 Logout")
    print(" 0. 🏁 Exit")
    print("="*40)

def main_loop():
    """Main program execution loop."""
    print("\nWelcome to DJWYA - Don't Just Wear Your Artists.")
    
    while True:
        # Step 1: Login / Auth
        global resolved_user_id
        username = input("\n👤 Enter your DJWYA username or 'exit': ").strip()
        
        if username.lower() == 'exit':
            print("Goodbye! 👋")
            break
            
        if not username: continue
        
        response = supabase.table("public.users").select("id").eq("username", username).execute()
        if not response.data:
            print(f"❌ User '{username}' not found. Use user.py to create one.")
            continue
            
        resolved_user_id = response.data[0]['id']
        print(f"✅ Authenticated as: {username}")
        
        # Step 2: Command Loop
        while True:
            show_menu()
            choice = input("\n👉 Select an option: ").strip()
            
            match choice:
                case "1":
                    add_playlist(resolved_user_id)
                case "2":
                    print("🚧 Playlist removal is under development.")
                case "3":
                    print("🚧 Festival matching is coming soon.")
                case "4":
                    check_sonic_dna(resolved_user_id)
                case "5" | "6":
                    print("🚧 Visual analytics are coming in the next update!")
                case "9":
                    print(f"Logging out {username}...")
                    break # Back to the username prompt
                case "0":
                    print("Exiting application...")
                    return # Exit everything
                case _:
                    print("❌ Invalid command. Please choose 0-9.")

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nForce exiting... Goodbye!")
