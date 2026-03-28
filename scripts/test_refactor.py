import os
from dotenv import load_dotenv
from supabase import create_client, Client
from artists_categorize import categorize_artist, bulk_categorize_artists

def test_retrieval():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)

    # Test artist: Hardwell (should be in the DB)
    artist_name = "Hardwell"
    print(f"🔍 Testing retrieval for '{artist_name}'...")
    
    # This should now use the nested select logic I implemented
    result = categorize_artist(artist_name, supabase_client=supabase)
    
    if result:
        print(f"✅ Success! Retrieved: {result['name']}")
        print(f"🧬 Genres (from junction table): {result['genres']}")
        print(f"📊 Vibe Bucket: {result['vibe_bucket']}")
    else:
        print(f"❌ Failed to retrieve artist '{artist_name}' or it was filtered out.")

    # Test bulk retrieval
    print(f"\n🔍 Testing bulk retrieval...")
    requests = [("Hardwell", [], False), ("Tiësto", [], False)]
    bulk_results = bulk_categorize_artists(requests, supabase_client=supabase)
    
    for name, data in bulk_results.items():
        print(f"✅ Bulk Match: {name} -> {data['genres']}")

if __name__ == "__main__":
    test_retrieval()
