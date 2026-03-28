import os
from dotenv import load_dotenv
from supabase import create_client

# Import the classifier to access the dictionary
from classifier import VibeClassifier

def main():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    supabase = create_client(url, key)

    sonic_dna_dict = VibeClassifier.SONIC_DNA

    print(f"🚀 Found {len(sonic_dna_dict)} hardcoded sonic DNA profiles.")
    
    updates = []
    
    # We will fetch all genres to get their IDs and current slugs
    print("📚 Fetching genres from the database...")
    res = supabase.table("genres").select("id, slug").execute()
    genres_db = {row['slug']: row['id'] for row in res.data if row.get('slug')}
    
    print(f"✅ Found {len(genres_db)} genres in the database.")
    
    for slug, dna in sonic_dna_dict.items():
        if slug in genres_db:
            genre_id = genres_db[slug]
            updates.append({
                "id": genre_id,
                "sonic_dna": dna
            })
        else:
            print(f"⚠️ Warning: Slug '{slug}' not found in the database. Skipping.")

    success_count = 0
    for update_payload in updates:
        try:
            supabase.table("genres").update({"sonic_dna": update_payload["sonic_dna"]}).eq("id", update_payload["id"]).execute()
            success_count += 1
        except Exception as e:
            print(f"   ❌ Update failed for id {update_payload['id']}: {e}")

    print(f"🎉 Successfully updated {success_count} genres with Sonic DNA data!")

if __name__ == "__main__":
    main()
