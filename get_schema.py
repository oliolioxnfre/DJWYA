import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

print("Checking genres...")
res = supabase.table("genres").select("id, slug, name").limit(5).execute()
print(res.data)

print("Checking artist_genres...")
try:
    res = supabase.table("artist_genres").select("*").limit(5).execute()
    print(res.data)
except Exception as e:
    print(f"Error artist_genres: {e}")

