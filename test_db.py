import os
from dotenv import load_dotenv
from supabase import create_client, Client
from classifier import GenreClassifier
from classifier import VibeClassifier

load_dotenv()

LASTFM_API_KEY = os.environ.get("LASTFM_API_KEY")
LASTFM_API_SECRET = os.environ.get("LASTFM_API_SECRET")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Test the VibeClassifier
VibeClassifier.update_user_dna("db65253d-6643-4607-8988-7770f0193a13")

# Query the updated user dna
supabase: Client = create_client(url, key)
res = supabase.table("public.users").select("sonic_dna").eq("id", "db65253d-6643-4607-8988-7770f0193a13").execute()
print(f"\nUser's Sonic DNA: {res.data[0]['sonic_dna'] if res.data else 'Not Found'}")
