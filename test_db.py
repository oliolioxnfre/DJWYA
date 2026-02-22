from app import electronic_artists, sync_to_supabase
import json
print("Loaded electronic artists:", list(electronic_artists.keys())[:5])
if electronic_artists:
    first_key = list(electronic_artists.keys())[0]
    print("Sample:", json.dumps(electronic_artists[first_key], indent=2))
