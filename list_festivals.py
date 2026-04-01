import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

response = supabase.table("festivals").select("*").execute()
for f in response.data:
    print(f"Festival: {f['name']}, Lat: {f['lat']}, Lng: {f['lng']}")
