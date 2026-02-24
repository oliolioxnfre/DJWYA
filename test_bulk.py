import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

try:
    print("Testing if name_slug has a unique constraint...")
    test_data = [
        {"name": "test_artist_1", "name_slug": "test_artist_1", "genres": [], "vibe_bucket": "unknown", "sonic_dna": {}},
        {"name": "test_artist_1", "name_slug": "test_artist_1", "genres": [], "vibe_bucket": "unknown", "sonic_dna": {}}
    ]
    res = supabase.table("artists").upsert(test_data[0], on_conflict="name_slug").execute()
    print("Upsert with on_conflict succeeded!")
    
    # Cleanup
    if res.data:
        supabase.table("artists").delete().eq("id", res.data[0]['id']).execute()
except Exception as e:
    print(f"Upsert failed: {e}")
