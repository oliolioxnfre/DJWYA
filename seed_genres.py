import os
import re
from supabase import create_client, Client
from dotenv import load_dotenv

def slugify(text):
    # Standard slugify: lowercase, replace spaces/special chars with hyphens
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text

def parse_rym_pull(filepath):
    genres = []
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return genres

    with open(filepath, 'r') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        name = lines[i].strip()
        if not name:
            i += 1
            continue
            
        # The description should be on the next line
        if i + 1 < len(lines):
            description = lines[i+1].strip()
            
            # If the next line is also blank, we treat it as a name without description
            if not description:
                genres.append({
                    "name": name,
                    "slug": slugify(name),
                    "description": ""
                })
                i += 1
                continue
            
            # Valid Name + Description block
            genres.append({
                "name": name,
                "slug": slugify(name),
                "description": description
            })
            # Skip the name, description, and the following blank line
            i += 3
        else:
            # Last line of the file
            genres.append({
                "name": name,
                "slug": slugify(name),
                "description": ""
            })
            i += 1
            
    return genres

def seed_genres():
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment.")
        return

    supabase: Client = create_client(url, key)
    
    filepath = "RYMPULL.md"
    genres_to_add = parse_rym_pull(filepath)
    
    if not genres_to_add:
        print("No genres found to add.")
        return

    print(f"Found {len(genres_to_add)} genres in {filepath}.")
    
    try:
        # Verify 'description' column exists by attempting to select it
        supabase.table("genres").select("id, description").limit(1).execute()
    except Exception as e:
        print(f"Error: Could not access 'genres' table or 'description' column. {e}")
        return

    print(f"Upserting {len(genres_to_add)} genres...")
    
    # Upsert in batches of 100
    for i in range(0, len(genres_to_add), 100):
        batch = genres_to_add[i:i+100]
        try:
            res = supabase.table("genres").upsert(batch, on_conflict="slug").execute()
            print(f"  Batch {i//100 + 1} complete.")
        except Exception as e:
            print(f"  Error in batch {i//100 + 1}: {e}")

    print("Success: Genres seeded from RYMPULL.md.")

if __name__ == "__main__":
    seed_genres()
