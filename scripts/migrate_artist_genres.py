import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

def main():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print("❌ Supabase credentials not found.")
        sys.exit(1)
        
    supabase: Client = create_client(url, key)

    print("🚀 Starting Artist Genres Migration...")

    # Phase 1: Pre-Flight Memory Maps
    print("📚 Fetching canonical genres and aliases...")
    try:
        genres_res = supabase.table("genres").select("id, slug, aliases").execute()
    except Exception as e:
        print(f"❌ Failed to fetch genres: {e}")
        return

    canonical_map = {}
    alias_dict = {
        # Hardcoded fallbacks
        "dnb": "drum-and-bass",
        "d&b": "drum-and-bass",
        "drumnbass": "drum-and-bass",
        "drum n bass": "drum-and-bass",
        "deep house": "deep-house",
        "tech house": "tech-house",
        "progressive house": "progressive-house",
        "house music": "house",
        "techno music": "techno",
    }
    
    for row in genres_res.data:
        genre_id = row["id"]
        slug = row["slug"]
        if slug:
            canonical_map[slug] = genre_id
            
        # Add database aliases
        aliases = row.get("aliases")
        if aliases and isinstance(aliases, list):
            for alias in aliases:
                # Add if not already explicitly handled in hardcoded fallback
                alias_lower = alias.lower().strip()
                if alias_lower not in alias_dict:
                    alias_dict[alias_lower] = slug

    print(f"✅ Loaded {len(canonical_map)} canonical genres and {len(alias_dict)} aliases.")

    # Fetch Artists
    print("\n🎸 Fetching artists from database...")
    try:
        # Paginating or fetching all depending on data size
        # We'll try to fetch all at once first since PostgREST limit might be 1000
        # Wait, if there are thousands of artists, we need pagination.
        artists_data = []
        limit = 1000
        offset = 0
        while True:
            res = supabase.table("artists").select("id, name, genres").range(offset, offset + limit - 1).execute()
            if not res.data:
                break
            artists_data.extend(res.data)
            offset += limit
            if len(res.data) < limit:
                break
                
        print(f"✅ Loaded {len(artists_data)} artists.")
    except Exception as e:
        print(f"❌ Failed to fetch artists: {e}")
        return

    # Phase 2-4: The Funneler & Bulk Insert Prep
    inserts = []
    skipped = 0
    misc_dropped = 0
    total_artists_processed = 0

    print("\n🌪️ Funneling genres...")
    for artist in artists_data:
        artist_id = artist["id"]
        raw_genres = artist.get("genres")
        
        if not raw_genres or not isinstance(raw_genres, list):
            continue
            
        total_artists_processed += 1
        seen_slugs = set()
        
        for raw in raw_genres:
            # 1. Lowercase & Trim
            cleaned = raw.lower().strip()
            if not cleaned:
                continue
                
            # 2. Translate via Alias Dictionary
            mapped_slug = alias_dict.get(cleaned, cleaned)
            
            # Additional normalization if it slipped through: replace spaces with dashes
            mapped_slug = mapped_slug.replace(" ", "-")
            
            # 3. Translate to canonical if it's already a known alias mapping but 
            # maybe alias_dict routed it to another alias? It shouldn't if mapped correctly.
            final_slug = alias_dict.get(mapped_slug, mapped_slug)
            
            # 4. Map to UUID
            genre_id = canonical_map.get(final_slug)
            if genre_id:
                # 5. Deduplicate slugs for the same artist
                if genre_id not in seen_slugs:
                    seen_slugs.add(genre_id)
                    inserts.append({
                        "artist_id": artist_id,
                        "genre_id": genre_id,
                        "vote_count": 5
                    })
            else:
                misc_dropped += 1

    print(f"✅ Funneled {total_artists_processed} artists.")
    print(f"ℹ️  Dropped {misc_dropped} unmapped strings.")
    print(f"📦 Total `artist_genres` rows to insert: {len(inserts)}")

    if not inserts:
        print("⏭️ No rows to insert. Exiting.")
        return

    # Phase 4: Bulk Insert
    print("\n🚀 Beginning Bulk Insert...")
    batch_size = 500
    success_count = 0
    
    for i in range(0, len(inserts), batch_size):
        batch = inserts[i:i+batch_size]
        try:
            res = supabase.table("artist_genres").insert(batch).execute()
            success_count += len(batch)
            print(f"   -> Inserted batch {i//batch_size + 1} ({len(batch)} rows)")
        except Exception as e:
            msg = str(e)
            print(f"   ❌ Batch failed: {e}")

    print(f"\n🎉 Migration Complete! Successfully processed ~{success_count} payloads.")

if __name__ == "__main__":
    main()
