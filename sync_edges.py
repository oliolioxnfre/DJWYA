import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Supabase Auth
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY") # Use service key to bypass RLS for writes
if not key:
    key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found. Make sure SUPABASE_URL and SUPABASE_SERVICE_KEY are set.")
    exit(1)

supabase = create_client(url, key)

def fetch_slug_to_id_map():
    print("Fetching genres to build slug -> id mapping...")
    slug_to_id = {}
    limit = 1000
    offset = 0
    while True:
        response = supabase.table("genres").select("id, slug").range(offset, offset + limit - 1).execute()
        data = response.data
        if not data:
            break
        for row in data:
            if row.get("slug"):
                slug_to_id[row["slug"]] = row["id"]
        offset += limit
        if len(data) < limit:
            break
    print(f"Loaded {len(slug_to_id)} genres.")
    return slug_to_id

def sync_edges(json_file):
    slug_to_id = fetch_slug_to_id_map()
    
    print(f"Loading {json_file}...")
    with open(json_file, "r") as f:
        data = json.load(f)
        
    edges_to_insert = []
    
    missing_slugs = set()
    
    for item in data:
        child_slug = item.get("child_slug")
        edges = item.get("edges", [])
        
        if not edges:
            continue
            
        if child_slug not in slug_to_id:
            missing_slugs.add(child_slug)
            continue
            
        child_id = slug_to_id[child_slug]
        
        for edge in edges:
            parent_slug = edge.get("parent_slug")
            
            if parent_slug not in slug_to_id:
                missing_slugs.add(parent_slug)
                continue
                
            parent_id = slug_to_id[parent_slug]
            
            edges_to_insert.append({
                "child_id": child_id,
                "parent_id": parent_id,
                "edge_type": edge.get("edge_type"),
                "weight": edge.get("weight")
            })

    if missing_slugs:
        print(f"Warning: Found {len(missing_slugs)} missing slugs in the database that were in the JSON.")
        for slug in missing_slugs:
            print(f"  - {slug}")
        
    print(f"Prepared {len(edges_to_insert)} edges for insertion.")
    
    if not edges_to_insert:
        print("No edges to insert. Exiting.")
        return

    print("Clearing existing genre_edges...")
    # Using 'neq' on edge_type to delete all rows. 'parent' and 'influence' are the types.
    # Choosing an impossible edge_type to be un-equal to, so it matches all rows.
    try:
        supabase.table("genre_edges").delete().neq("edge_type", "DELETE_ME").execute()
    except Exception as e:
        print(f"Warning on delete operation: {e}")
        pass
        
    print("Inserting new edges...")
    # Insert in batches to avoid payload limits
    batch_size = 500
    for i in range(0, len(edges_to_insert), batch_size):
        batch = edges_to_insert[i:i+batch_size]
        try:
            supabase.table("genre_edges").insert(batch).execute()
            print(f"Inserted batch {i//batch_size + 1} ({len(batch)} edges)")
        except Exception as e:
            print(f"Error inserting batch {i//batch_size + 1}: {e}")
        
    print("Sync complete!")

if __name__ == "__main__":
    sync_edges("genre-relationships.json")
