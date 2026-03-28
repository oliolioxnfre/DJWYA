import os
import sys
from collections import Counter
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

    print("🔍 Fetching genres and aliases for comparison...")
    try:
        genres_res = supabase.table("genres").select("id, slug, aliases").execute()
    except Exception as e:
        print(f"❌ Failed to fetch genres: {e}")
        return

    canonical_slugs = set()
    alias_dict = {
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
        slug = row["slug"]
        if slug:
            canonical_slugs.add(slug)
        aliases = row.get("aliases")
        if aliases and isinstance(aliases, list):
            for alias in aliases:
                alias_lower = alias.lower().strip()
                if alias_lower not in alias_dict:
                    alias_dict[alias_lower] = slug

    print(f"✅ Loaded {len(canonical_slugs)} canonical slugs and {len(alias_dict)} aliases.")

    print("\n🎸 Fetching artists from database...")
    artists_data = []
    limit = 1000
    offset = 0
    while True:
        res = supabase.table("artists").select("genres").range(offset, offset + limit - 1).execute()
        if not res.data:
            break
        artists_data.extend(res.data)
        offset += limit
        if len(res.data) < limit:
            break
            
    print(f"✅ Loaded {len(artists_data)} artists.")

    failed_counter = Counter()

    print("\n🌪️ Analyzing failed mappings...")
    for artist in artists_data:
        raw_genres = artist.get("genres")
        if not raw_genres or not isinstance(raw_genres, list):
            continue
            
        for raw in raw_genres:
            cleaned = raw.lower().strip()
            if not cleaned: continue
            
            # Follow migration logic: translate then check
            mapped_slug = alias_dict.get(cleaned, cleaned)
            mapped_slug = mapped_slug.replace(" ", "-")
            final_slug = alias_dict.get(mapped_slug, mapped_slug)
            
            if final_slug not in canonical_slugs:
                failed_counter[raw] += 1

    print("\n📊 UNMAPPED GENRE ANALYSIS (Sorted by Count Descending):")
    print("-" * 50)
    for genre, count in failed_counter.most_common():
        print(f"{genre}: {count}")
    print("-" * 50)
    print(f"Done! {len(failed_counter)} unique unmapped strings found.")

if __name__ == "__main__":
    main()
