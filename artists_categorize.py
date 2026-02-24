import pylast
import os
import concurrent.futures
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

def categorize_artist(artist_name, fallback_genres=None, filter_electronic=True, existing_data=None, supabase_client=None):
    """
    Fetches genres, categorizes them, and builds the artist metadata dict.
    If filter_electronic is False, it includes the artist regardless of genre.
    If existing_data or supabase_client is provided, it checks the DB first to skip Last.fm.
    """
    # 1. Check existing_data if provided by bulk process
    # 2. Otherwise, check Supabase directly if client provided
    if not existing_data and supabase_client:
        slug = artist_name.lower().replace(" ", "-")
        try:
            res = supabase_client.table("artists").select("*").eq("name_slug", slug).execute()
            if res.data:
                existing_data = res.data[0]
        except Exception:
            pass # Fall back to Last.fm if DB fails

    if existing_data:
        # Use existing data from DB
        genres = existing_data.get('genres', [])
        
        # We still need to respect the electronic filter even if they are in the DB
        if filter_electronic:
            electronic_matches = get_electronic_genres(genres)
            if not electronic_matches:
                return None
                
        return {
            "name": existing_data.get('name', artist_name),
            "genres": genres,
            "vibe_bucket": existing_data.get('vibe_bucket', []),
            "sonic_dna": existing_data.get('sonic_dna', {})
        }

    # Otherwise, proceed with Last.fm API logic
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

def _categorize_worker(args):
    """Worker function for unpacking args into categorize_artist."""
    artist_name, fallback_genres, filter_electronic, existing_data = args
    return categorize_artist(artist_name, fallback_genres, filter_electronic, existing_data)

def bulk_categorize_artists(artist_requests, supabase_client=None, max_workers=10):
    """
    Multithreaded generation of categorized artist dicts.
    artist_requests is a list of tuples: (artist_name, fallback_genres, filter_electronic)
    If supabase_client is provided, it performs a batch lookup to avoid redundant API calls.
    """
    # 1. First, do a bulk lookup of all artists in the Supabase DB
    existing_map = {}
    if supabase_client:
        all_slugs = [name.lower().replace(" ", "-") for name, _, _ in artist_requests]
        print(f"🔍 Checking Supabase for {len(all_slugs)} existing artists...")
        
        # Batch checks in chunks of 500
        for i in range(0, len(all_slugs), 500):
            batch_slugs = all_slugs[i:i+500]
            try:
                res = supabase_client.table("artists").select("*").in_("name_slug", batch_slugs).execute()
                if res.data:
                    for row in res.data:
                        existing_map[row["name_slug"]] = row
            except Exception as e:
                print(f"⚠️ Warning: Bulk lookup failed: {e}")

    # 2. Prepare requests for the worker (adding the existing data if found)
    worker_requests = []
    for name, fallback, filter_e in artist_requests:
        slug = name.lower().replace(" ", "-")
        existing_info = existing_map.get(slug)
        worker_requests.append((name, fallback, filter_e, existing_info))

    print(f"🧵 Parallel processing {len(worker_requests)} artists...")
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Map the worker over the requests
        future_to_artist = {executor.submit(_categorize_worker, req): req[0] for req in worker_requests}
        for future in concurrent.futures.as_completed(future_to_artist):
            artist_name = future_to_artist[future]
            try:
                categorized = future.result()
                if categorized:
                    results[artist_name] = categorized
            except Exception as e:
                print(f"❌ Error processing {artist_name}: {e}")
                
    return results

def sync_artists_to_supabase(artist_dict, supabase_client, user_id=None):
    """Syncs a dictionary of analyzed artists to the Supabase database using bulk operations."""
    if not artist_dict:
        print("⚠️ No artists found to sync.")
        return

    print(f"🚀 Syncing {len(artist_dict)} artists to Supabase...")
    
    # 1. Prepare slug to artist mapping
    slugs_to_process = []
    artist_metadata_map = {}
    
    for item in artist_dict.values():
        name_slug = item['name'].lower().replace(" ", "-")
        slugs_to_process.append(name_slug)
        artist_metadata_map[name_slug] = {
            "name": item['name'],
            "name_slug": name_slug,
            "genres": item.get('genres', []),
            "vibe_bucket": item.get('vibe_bucket', []),
            "sonic_dna": item.get('sonic_dna', {})
        }

    # 2. Fetch existing artists from Supabase to correctly route inserts vs updates
    # We slice into groups of 100 just in case the query is too large, but typically it is fine.
    existing_slug_to_id = {}
    batch_size = 100
    for i in range(0, len(slugs_to_process), batch_size):
        batch_slugs = slugs_to_process[i:i+batch_size]
        try:
            res = supabase_client.table("artists").select("id, name_slug").in_("name_slug", batch_slugs).execute()
            if res.data:
                for row in res.data:
                    existing_slug_to_id[row["name_slug"]] = row["id"]
        except Exception as e:
            print(f"❌ Error fetching bulk slugs: {e}")

    # 3. Separate into Inserts and Updates
    inserts = []
    updates = []
    
    for slug, payload in artist_metadata_map.items():
        if slug in existing_slug_to_id:
            # We must include the ID to perform an update or upsert
            payload["id"] = existing_slug_to_id[slug]
            updates.append(payload)
        else:
            inserts.append(payload)
            
    # 4. Perform Bulk DB Writes
    try:
        if inserts:
            res = supabase_client.table("artists").insert(inserts).execute()
            # Catch the new IDs so we can use them for the library logic
            if res.data:
                for row in res.data:
                    existing_slug_to_id[row["name_slug"]] = row["id"]
                    
        if updates:
            # Upsert acts as a bulk update if the ID is provided and exists
            supabase_client.table("artists").upsert(updates).execute()
    except Exception as e:
        print(f"❌ Error during bulk artist write: {e}")

    # 5. Process Personal Library
    if user_id:
        # Aggregate counts by artist_id to prevent duplicates in the bulk upsert
        library_data_agg = {}
        for item in artist_dict.values():
            if 'count' not in item: continue
            
            name_slug = item['name'].lower().replace(" ", "-")
            artist_id = existing_slug_to_id.get(name_slug)
            
            if artist_id:
                if artist_id in library_data_agg:
                    library_data_agg[artist_id]['count'] += item['count']
                else:
                    library_data_agg[artist_id] = {
                        "user_id": user_id,
                        "artist_id": artist_id,
                        "count": item.get('count', 1)
                    }
        
        library_inserts = list(library_data_agg.values())
        
        if library_inserts:
            try:
                supabase_client.table("user_lib").upsert(library_inserts, on_conflict="user_id,artist_id").execute()
            except Exception as e:
                print(f"❌ Error inserting user library batch: {e}")
                
        # Update user DNA after sync
        VibeClassifier.update_user_dna(user_id)
        
    print(f"✨ Finished Syncing {len(artist_dict)} artists to Supabase!")

