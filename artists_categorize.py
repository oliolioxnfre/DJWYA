import pylast
import os
import concurrent.futures
from dotenv import load_dotenv
from classifier import VibeClassifier, GenreManager

load_dotenv()

LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_API_SECRET = os.environ.get("LASTFM_API_SECRET")

# Initialize the network
network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

# Pre-initialize GenreManager to avoid thread-safety issues during bulk process
GenreManager.get_instance()

# Cache to prevent doing redundant Last.fm API calls
artist_genre_cache = {}

def get_electronic_genres(genres):
    if not genres: return []
    manager = GenreManager.get_instance()
    return [genre for genre in genres if manager.is_electronic(genre)]

import time

def get_artist_genres(artist_name):
    """Returns all genres for an artist from Last.fm, with heavy persistence for accuracy."""
    if artist_name in artist_genre_cache:
        return artist_genre_cache[artist_name]
        
    def fetch_genres(name_to_fetch):
        artist = network.get_artist(name_to_fetch)
        top_tags = artist.get_top_tags(limit=50)
        return [tag.item.get_name().lower().replace(" ", "-") for tag in top_tags]

    names_to_try = [artist_name]
    # Try an ascii-normalized name if different
    normalized = artist_name.encode('ascii', 'ignore').decode('utf-8').strip()
    # Also sometimes EDM names have extra text in parentheses. We can keep it simple for now as requested.
    if normalized and normalized != artist_name:
        names_to_try.append(normalized)

    retries = 5 # Reduced from 10 to not hang the scraper on actual connection errors
    for name_variant in names_to_try:
        for attempt in range(retries):
            try:
                genres = fetch_genres(name_variant)
                # Successful fetch
                artist_genre_cache[artist_name] = genres
                return genres
                
            except pylast.WSError as ws:
                err_str = str(ws).lower()
                # "could not be found" wasn't caught by "not found" in a strict contiguous check
                if "not found" in err_str or "no such artist" in err_str or "could not be found" in err_str:
                    print(f"ℹ️ Last.fm: Artist '{name_variant}' not found.")
                    break # Break retry loop, move to next normalization variant if exists
                
                # Rate limits or internal Last.fm errors: Wait and retry
                wait_time = (attempt + 1) * 2
                print(f"⚠️ Last.fm API Error ({ws}). Waiting {wait_time}s to retry '{name_variant}'...")
                time.sleep(wait_time)
                
            except Exception as e:
                # Network timeouts, SSL issues, etc.
                wait_time = (attempt + 1) * 2
                print(f"⚠️ Network issue for '{name_variant}' (Attempt {attempt+1}/{retries}): {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)

    # If we fall through (all variants failed or were not found)
    print(f"❌ '{artist_name}' could not be resolved on Last.fm. Storing empty genres to pass to database anyways.")
    artist_genre_cache[artist_name] = []
    # Cache it as empty so we don't spam Last.fm on future passes
    return []

def categorize_artist(artist_name, fallback_genres=None, filter_electronic=True, existing_data=None, supabase_client=None):
    """
    Fetches genres, categorizes them, and builds the artist metadata dict.
    Calculates unified vote scoring across both CSV and Last.fm inputs.
    """ 
    manager = GenreManager.get_instance()
    
    if not existing_data and supabase_client:
        slug = artist_name.lower().replace(" ", "-")
        try:
            res = supabase_client.table("artists").select("*, artist_genres(genres(slug))").eq("name_slug", slug).execute()
            if res.data:
                existing_data = res.data[0]
                ag_list = existing_data.get("artist_genres") or []
                existing_data['genres'] = [ag['genres']['slug'] for ag in ag_list if ag.get('genres') and ag['genres'].get('slug')]
        except Exception:
            pass

    if existing_data:
        genres = existing_data.get('genres', [])
        
        if filter_electronic:
            electronic_matches = get_electronic_genres(genres)
            if not electronic_matches:
                genres = []
                
        return {
            "name": existing_data.get('name', artist_name),
            "genres": genres,
            "sonic_dna": existing_data.get('sonic_dna', {})
        }

    # New Dual-Source Vote System Logic
    csv_genres = []
    if fallback_genres:
        for item in fallback_genres:
            csv_genres.extend([g.strip() for g in item.split(",") if g.strip()])
            
    # 1. Fetch both Last.fm and CSV data unconditionally
    lastfm_genres = get_artist_genres(artist_name)
    
    # 2. Get electronic canonical subsets
    csv_electronic = get_electronic_genres(csv_genres)
    lastfm_electronic = get_electronic_genres(lastfm_genres)
    
    generic_slugs = {"electronic", "edm", "rave"}
    genre_votes_map = {}
    
    # helper to process a list of genres into the vote map
    def process_genres(genre_list, source):
        for raw in genre_list:
            slug = manager.get_canonical_slug(raw)
            if not manager.is_electronic(slug):
                continue
            if slug in genre_votes_map:
                # If it's already in from another source, it's an intersection!
                if genre_votes_map[slug]["source"] != source:
                    genre_votes_map[slug]["votes"] = 20
            else:
                genre_votes_map[slug] = {"votes": 5, "source": source}
                
    process_genres(csv_genres, source="csv")
    process_genres(lastfm_genres, source="lastfm")
    
    # --- HARD LIMITERS ---
    # ROOT genres that are definitively non-electronic.
    # We use exact slug matching to avoid catching crossover genres like 
    # "Indie Dance" or "Synth Funk".
    RAW_BLACKLIST = [
        "rock", "rap", "metal", "heavy-metal", "ska", "acoustic", "hardcore-punk",
        "country", "shoegaze", "pop-punk", "alternative-rock", "death-metal", "black-metal",
        "classical", "folk-rock", "punk", "punk-rock", "ska", "blues"
    ]
    
    HARD_BLACKLIST = {manager.get_canonical_slug(b) for b in RAW_BLACKLIST}
    
    all_raw_tags = csv_genres + lastfm_genres

    all_slugs = {manager.get_canonical_slug(tag) for tag in all_raw_tags}
    
    # 1. Absolute Blacklist: 
    # If any of the hard non-electronic genres exist exactly, wipe out their electronic features
    if any(slug in HARD_BLACKLIST for slug in all_slugs):
        genre_votes_map.clear()
        
    # 2. Generic Isolation Rule:
    # If the *only* electronic tags they possess are generic (electronic, edm, rave)...
    has_specific_electronic = any(slug not in generic_slugs for slug in genre_votes_map.keys())
    if not has_specific_electronic and bool(genre_votes_map):
        # ...they MUST not have any other catalog mapped sub-genres.
        all_slugs_loop = {manager.get_canonical_slug(tag) for tag in all_raw_tags}
        # Simple Generic Isolation: If they have less than 20% electronic genres,
        # and only generic electronic genres, wipe out their electronic features.
        if len(genre_votes_map) < len(all_raw_tags) * 0.2:
            genre_votes_map.clear()
    
    # --- END HARD LIMITERS ---
    
    # 3. Handle generics
    # If there are ANY specific electronic tags across both sources, purge generics entirely.
    has_specific = any(slug not in generic_slugs for slug in genre_votes_map.keys())
    if has_specific:
        # scrub generics
        for slug in generic_slugs:
            if slug in genre_votes_map:
                del genre_votes_map[slug]
                
    # 4. Strict Electronic Filtering logic
    # If filter_electronic=True, and we have NO valid electronic tags (either naturally, 
    # or because they hit the blacklist and got cleared), we explicitly ensure their 
    # return dict has absolutely ZERO electronic footprint, but we ALLOW them to return 
    # so they get inserted into the database as a blank-slate!
    if filter_electronic and not genre_votes_map:
        genre_votes_map.clear()
    
    # In order to maintain compatibility with existing payload shapes,
    # "genres" will still return a flat list ordered by votes desc,
    # and we add "genre_votes" to pass explicit counts.
    sorted_genres = sorted(genre_votes_map.items(), key=lambda x: x[1]["votes"], reverse=True)
    flat_genres_to_use = [item[0] for item in sorted_genres]
    vote_counts_only = {item[0]: item[1]["votes"] for item in sorted_genres}
    
    return {
        "name": artist_name,
        "genres": flat_genres_to_use,
        "genre_votes": vote_counts_only,
        "sonic_dna": VibeClassifier.get_artist_vibe_from_votes(vote_counts_only)
    }

def _categorize_worker(args):
    artist_name, fallback_genres, filter_electronic, existing_data = args
    return categorize_artist(artist_name, fallback_genres, filter_electronic, existing_data)

def bulk_categorize_artists(artist_requests, supabase_client=None, max_workers=10):
    existing_map = {}
    if supabase_client:
        all_slugs = [name.lower().replace(" ", "-") for name, _, _ in artist_requests]
        print(f"🔍 Checking Supabase for {len(all_slugs)} existing artists...")
        
        for i in range(0, len(all_slugs), 500):
            batch_slugs = all_slugs[i:i+500]
            try:
                res = supabase_client.table("artists").select("*, artist_genres(genres(slug))").in_("name_slug", batch_slugs).execute()
                if res.data:
                    for row in res.data:
                        ag_list = row.get("artist_genres") or []
                        row['genres'] = [ag['genres']['slug'] for ag in ag_list if ag.get('genres') and ag['genres'].get('slug')]
                        existing_map[row["name_slug"]] = row
            except Exception as e:
                print(f"⚠️ Warning: Bulk lookup failed: {e}")

    worker_requests = []
    for name, fallback, filter_e in artist_requests:
        slug = name.lower().replace(" ", "-")
        existing_info = existing_map.get(slug)
        worker_requests.append((name, fallback, filter_e, existing_info))

    print(f"🧵 Parallel processing {len(worker_requests)} artists...")
    
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
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
    if not artist_dict:
        print("⚠️ No artists found to sync.")
        return

    print(f"🚀 Syncing {len(artist_dict)} artists to Supabase...")
    manager = GenreManager.get_instance()
    
    slugs_to_process = []
    artist_metadata_map = {}
    
    for item in artist_dict.values():
        name_slug = item['name'].lower().replace(" ", "-")
        slugs_to_process.append(name_slug)
        artist_metadata_map[name_slug] = {
            "name": item['name'],
            "name_slug": name_slug,
            "sonic_dna": item.get('sonic_dna', {})
        }

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

    inserts = []
    updates = []
    
    for slug, payload in artist_metadata_map.items():
        if slug in existing_slug_to_id:
            payload["id"] = existing_slug_to_id[slug]
            updates.append(payload)
        else:
            inserts.append(payload)
            
    try:
        if inserts:
            res = supabase_client.table("artists").insert(inserts).execute()
            if res.data:
                for row in res.data:
                    existing_slug_to_id[row["name_slug"]] = row["id"]
        
        if updates:
            supabase_client.table("artists").upsert(updates).execute()

        artist_genres_payloads = []
        for name_slug, item in artist_metadata_map.items():
            artist_id = existing_slug_to_id.get(name_slug)
            if not artist_id: continue
            
            orig_item = next((v for v in artist_dict.values() if v['name'].lower().replace(" ", "-") == name_slug), {})
            # Read the vote map from the origin item. If empty or legacy, just fall back to standard genre list.
            genre_votes_map = orig_item.get("genre_votes", {})
            raw_genres = orig_item.get("genres", [])

            seen_slugs = set()
            
            # If we dynamically computed genre_votes (the new way)
            if genre_votes_map and isinstance(genre_votes_map, dict):
                for raw, votes in genre_votes_map.items():
                    genre_id = manager.get_canonical_id(raw)
                    if genre_id and genre_id not in seen_slugs:
                        seen_slugs.add(genre_id)
                        artist_genres_payloads.append({
                            "artist_id": artist_id,
                            "genre_id": genre_id,
                            "vote_count": votes
                        })
            # Legacy fallback: if we only have the flat list
            elif raw_genres and isinstance(raw_genres, list):
                for raw in raw_genres:
                    genre_id = manager.get_canonical_id(raw)
                    if genre_id and genre_id not in seen_slugs:
                        seen_slugs.add(genre_id)
                        artist_genres_payloads.append({
                            "artist_id": artist_id,
                            "genre_id": genre_id,
                            "vote_count": 5
                        })

        if artist_genres_payloads:
            try:
                processed_artist_ids = list(set(p['artist_id'] for p in artist_genres_payloads))
                existing_mappings = []
                for i in range(0, len(processed_artist_ids), 500):
                    batch_ids = processed_artist_ids[i:i+500]
                    res = supabase_client.table("artist_genres").select("artist_id, genre_id").in_("artist_id", batch_ids).execute()
                    if res.data:
                        existing_mappings.extend(res.data)
                
                existing_set = set((m['artist_id'], m['genre_id']) for m in existing_mappings)
                to_insert = [p for p in artist_genres_payloads if (p['artist_id'], p['genre_id']) not in existing_set]
                
                if to_insert:
                    ag_batch_size = 500
                    for i in range(0, len(to_insert), ag_batch_size):
                        batch = to_insert[i:i+ag_batch_size]
                        supabase_client.table("artist_genres").insert(batch).execute()
                        
            except Exception as e:
                print(f"❌ Error syncing artist_genres: {e}")

    except Exception as e:
        print(f"❌ Error during bulk artist write: {e}")

    if user_id:
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
                
        VibeClassifier.update_user_dna(user_id)
        
    print(f"✨ Finished Syncing {len(artist_dict)} artists to Supabase!")
