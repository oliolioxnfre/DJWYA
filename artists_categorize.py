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

def get_artist_genres(artist_name):
    """Returns all genres for an artist from Last.fm"""
    if artist_name in artist_genre_cache:
        return artist_genre_cache[artist_name]
    try:
        artist = network.get_artist(artist_name)
        # Get a generous amount of tags (limit 50 to avoid extreme cases)
        top_tags = artist.get_top_tags(limit=50)
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
    Prioritizes fallback_genres (CSV) and only falls back to Last.fm if data is sparse.
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
                return None
                
        return {
            "name": existing_data.get('name', artist_name),
            "genres": genres,
            "sonic_dna": existing_data.get('sonic_dna', {})
        }

    # New Genre Priority Logic
    csv_genres = fallback_genres if fallback_genres else []
    genres_to_use = csv_genres
    
    csv_electronic = get_electronic_genres(csv_genres)
    generic_slugs = {"electronic", "edm", "rave"}
    has_only_generic_electronic = False
    
    if csv_electronic:
        has_only_generic_electronic = all(manager.get_canonical_slug(g) in generic_slugs for g in csv_electronic)
    
    # Determine if we should fallback to Last.fm
    # Fallback if:
    # 1. CSV has less than 2 genres (0 or 1)
    # 2. CSV has exactly 1 electronic genre (and no other genres)
    # 3. All electronic genres present in the CSV are generic ("electronic", "edm", "rave")
    should_fallback = False
    if len(csv_genres) < 2:
        should_fallback = True
    elif len(csv_genres) == 1 and bool(csv_electronic):
        should_fallback = True
    elif has_only_generic_electronic:
        should_fallback = True
        
    if should_fallback:
        lastfm_genres = get_artist_genres(artist_name)
        if lastfm_genres:
            lastfm_electronic = get_electronic_genres(lastfm_genres)
            lastfm_has_specific = any(manager.get_canonical_slug(g) not in generic_slugs for g in lastfm_electronic)
            
            # Use lastfm genres only if they provide a specific electronic genre,
            # or if the CSV didn't even have generic electronic genre.
            if lastfm_has_specific or not csv_electronic:
                genres_to_use = lastfm_genres
        # If lastfm fails, we naturally keep using csv_genres as per logic
        
    if filter_electronic:
        electronic_matches = get_electronic_genres(genres_to_use)
        if not electronic_matches:
            # If we were using lastfm and it failed to find electronic genres, 
            # maybe the singular CSV genre was electronic and we should use that?
            # "If the lastfm lookup fails we default to the singular electronic genre we found in the csv."
            if genres_to_use != csv_genres:
                secondary_electronic = get_electronic_genres(csv_genres)
                if secondary_electronic:
                    genres_to_use = csv_genres
                else:
                    return None
            else:
                return None
            
    return {
        "name": artist_name,
        "genres": genres_to_use,
        "sonic_dna": VibeClassifier.get_artist_vibe(genres_to_use)
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
            raw_genres = orig_item.get("genres", [])

            seen_slugs = set()
            if raw_genres and isinstance(raw_genres, list):
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
