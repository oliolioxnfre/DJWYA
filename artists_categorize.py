import pylast
import os
from dotenv import load_dotenv
from classifier import GenreClassifier, VibeClassifier

load_dotenv()

LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_API_SECRET = os.environ.get("LASTFM_API_SECRET")

# Initialize the network
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

# Cache to prevent doing redundant Last.FM API calls
artist_genre_cache = {}

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

def get_electronic_genres(genres):
    if not genres: return []
    return [genre for genre in genres if genre in electronic_genres]

def get_artist_genres(artist_name):
    """Returns the top 7 genres for an artist from Last.fm"""
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

def categorize_artist(artist_name, fallback_genres=None, filter_electronic=True):
    """
    Fetches genres, categorizes them, and builds the artist metadata dict.
    If filter_electronic is False, it includes the artist regardless of genre.
    """
    lastfm_genres = get_artist_genres(artist_name)
    
    if not filter_electronic:
        # Include all artists (like for festivals). Use lastfm if available, else fallback
        genres_to_use = lastfm_genres if lastfm_genres else (fallback_genres or [])
        return {
            "name": artist_name,
            "genres": genres_to_use,
            "vibe_bucket": GenreClassifier.classify(genres_to_use),
            "sonic_dna": VibeClassifier.get_artist_vibe(genres_to_use)
        }
    else:
        # Strict electronic filtering for personal playlists
        electronic_matches = get_electronic_genres(lastfm_genres)
        if electronic_matches:
            return {
                "name": artist_name,
                "genres": lastfm_genres,
                "vibe_bucket": GenreClassifier.classify(lastfm_genres),
                "sonic_dna": VibeClassifier.get_artist_vibe(lastfm_genres)
            }
        else:
            csv_electronic_matches = get_electronic_genres(fallback_genres) if fallback_genres else []
            if csv_electronic_matches:
                return {
                    "name": artist_name,
                    "genres": fallback_genres,
                    "vibe_bucket": GenreClassifier.classify(fallback_genres),
                    "sonic_dna": VibeClassifier.get_artist_vibe(fallback_genres)
                }
            return None

def sync_artists_to_supabase(artist_dict, supabase_client, user_id=None):
    """Syncs a dictionary of analyzed artists to the Supabase database."""
    if not artist_dict:
        print("⚠️ No artists found to sync.")
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
        existing_artist = supabase_client.table("artists").select("id").eq("name_slug", name_slug).execute()
        
        if existing_artist.data and len(existing_artist.data) > 0:
            artist_id = existing_artist.data[0]['id']
            # Update the existing artist
            supabase_client.table("artists").update(artist_metadata).eq("id", artist_id).execute()
        else:
            # Insert new artist
            inserted_artist = supabase_client.table("artists").insert(artist_metadata).execute()
            if inserted_artist.data:
                artist_id = inserted_artist.data[0]['id']
            else:
                print(f"❌ Failed to insert artist {item['name']}")
                continue

        # --- PART B: Update Personal Library (If user_id provided) ---
        if user_id and 'count' in item:
            library_data = {
                "user_id": user_id,
                "artist_id": artist_id,
                "count": item['count']
            }
            supabase_client.table("user_lib").upsert(library_data, on_conflict="user_id,artist_id").execute()
            
    # Finally, update the aggregate User DNA in the users table if a user_id was provided
    if user_id:
        VibeClassifier.update_user_dna(user_id)
        
    print(f"✨ Finished Syncing {len(artist_dict)} artists to Supabase!")
