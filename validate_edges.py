import os
import re
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv(".env")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_KEY is not set.")
    exit(1)

supabase = create_client(url, key)

def get_valid_slugs():
    print("Fetching valid slugs from database...")
    valid_slugs = set()
    limit = 1000
    offset = 0
    while True:
        response = supabase.table("genres").select("slug").range(offset, offset + limit - 1).execute()
        data = response.data
        if not data:
            break
        for row in data:
            if row.get("slug"):
                valid_slugs.add(row["slug"])
        offset += limit
        if len(data) < limit:
            break
    
    print(f"Fetched {len(valid_slugs)} valid slugs.")
    return valid_slugs

def validate_json_file(file_path, valid_slugs):
    print(f"Validating {file_path}...")
    
    child_slug_pattern = re.compile(r'"child_slug":\s*"([^"]+)"')
    parent_slug_pattern = re.compile(r'"parent_slug":\s*"([^"]+)"')
    
    invalid_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, 1):
                # Check for child_slug
                child_match = child_slug_pattern.search(line)
                if child_match:
                    slug = child_match.group(1)
                    if slug not in valid_slugs:
                        print(f"Line {line_number}: Invalid child_slug -> '{slug}'")
                        invalid_count += 1
                        
                # Check for parent_slug
                parent_match = parent_slug_pattern.search(line)
                if parent_match:
                    slug = parent_match.group(1)
                    if slug not in valid_slugs:
                        print(f"Line {line_number}: Invalid parent_slug -> '{slug}'")
                        invalid_count += 1
                        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
        
    print("-" * 30)
    if invalid_count == 0:
        print("Success! All slugs are valid.")
    else:
        print(f"Validation failed. Found {invalid_count} invalid slugs.")

if __name__ == "__main__":
    valid_slugs = get_valid_slugs()
    json_path = "genre-relationships.json"
    validate_json_file(json_path, valid_slugs)
