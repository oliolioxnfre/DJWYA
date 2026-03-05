import os
import time
import json
from dotenv import load_dotenv
from supabase import create_client, Client
from google import genai
from google.genai import types
from pydantic import BaseModel

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Supabase Auth
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_SERVICE_KEY") # Use service key to bypass RLS for writes if needed
supabase: Client = create_client(url, key)

# Gemini Auth
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

class Edge(BaseModel):
    name: str # Name must be exact match from valid_genres
    weight: float

class GenreEdges(BaseModel):
    parents: list[Edge]
    influences: list[Edge]

def fetch_all_genres():
    print("Fetching vocabulary of valid genres from database...")
    response = supabase.table("genres").select("id, name, description").execute()
    genres = response.data
    
    vocabulary = {g['name'].lower(): g['id'] for g in genres}
    names_list = [g['name'] for g in genres]
    print(f"Loaded {len(vocabulary)} valid genres.")
    return genres, vocabulary, names_list

def get_existing_processed_ids():
    response = supabase.table("genre_edges").select("child_id").execute()
    return set([row['child_id'] for row in response.data])

def extract_edges_from_llm(genre_name, description, valid_names_str):
    prompt = f"""
    You are an expert musicologist.
    Analyze this electronic music genre and its description to identify its parenthood and influences.
    
    Target Genre: {genre_name}
    Description: {description if description else 'No description available.'}
    
    Instructions:
    1. Identify AT MOST 2 direct parent genres and AT MOST 2 influencing genres. 
    2. IF you beleive the selected genre is a root edm genre such as house, jungle, techno etc. then it will have 0 parents and 0 influences.
    3. You MUST ONLY CHOOSE genres from the strict Approved Vocabulary List below.
    4. If the true parent or influence is not on the list, you must omit it. Do not invent genres.
    5. For each relationship, assign a weight between 0.0 and 1.0 representing the strength (e.g., 0.9 for direct parent, 0.4 for minor influence).
    6. The target genre cannot be its own parent or influence.

    Approved Vocabulary List:
    {valid_names_str}
    """
    
    max_retries = 3
    retry_delay = 10 # seconds to wait on 429
    
    for attempt in range(max_retries):
        try:
            # Using 'gemini-flash-latest' which is 1.5 Flash and worked in testing
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GenreEdges,
                    temperature=0.1 
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "resource_exhausted" in error_str:
                if attempt < max_retries - 1:
                    print(f"  -> Quota limit reached for {genre_name}. Waiting {retry_delay}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
            print(f"LLM Error for {genre_name}: {e}")
            return None

def process_and_insert_genre(genre, vocabulary, valid_names_str):
    genre_name = genre['name']
    genre_id = genre['id']
    description = genre['description']
    
    print(f"Processing: {genre_name}...")
    
    llm_result = extract_edges_from_llm(genre_name, description, valid_names_str)
    if not llm_result:
        return
        
    edges_to_insert = []
    
    # Process Parents
    for edge in llm_result.get('parents', []):
        parent_name = edge['name'].lower()
        if parent_name in vocabulary and parent_name != genre_name.lower():
            edges_to_insert.append({
                "child_id": genre_id,
                "parent_id": vocabulary[parent_name],
                "edge_type": "parent",
                "weight": edge['weight']
            })
            
    # Process Influences
    for edge in llm_result.get('influences', []):
        influence_name = edge['name'].lower()
        if influence_name in vocabulary and influence_name != genre_name.lower():
            edges_to_insert.append({
                "child_id": genre_id,
                "parent_id": vocabulary[influence_name],
                "edge_type": "influence",
                "weight": edge['weight']
            })
            
    if edges_to_insert:
        # Create a reverse vocabulary to get names back from IDs
        reverse_vocab = {v: k for k, v in vocabulary.items()}
        
        try:
            supabase.table("genre_edges").insert(edges_to_insert).execute()
            
            # Print specifically what was inserted
            for edge in edges_to_insert:
                rel_name = reverse_vocab.get(edge['parent_id'], "Unknown")
                print(f"  -> Added {edge['edge_type']}: {rel_name} (weight: {edge['weight']})")
                
            print(f"  Success: {len(edges_to_insert)} total edges for {genre_name}")
        except Exception as e:
            print(f"  -> DB Insert Error for {genre_name}: {e}")
    else:
        print(f"  -> No valid edges found for {genre_name}")

def main():
    genres, vocabulary, names_list = fetch_all_genres()
    valid_names_str = ", ".join(names_list)
    
    processed_ids = get_existing_processed_ids()
    print(f"Found {len(processed_ids)} already processed genres to skip.")
    
    count = 0
    for genre in genres:
        if genre['id'] in processed_ids:
            continue
            
        process_and_insert_genre(genre, vocabulary, valid_names_str)
        
        # Rate Limiting
        # Rate Limiting for Free Tier
        time.sleep(10) # 6 requests per minute (Limit is 15 but let's be safe)
        
        count += 1
        if count >= 20: # Limit to 20 for testing
            print("Reached limit of 20 genres. Stopping.")
            break
            
    print("Finished processing all genres.")

if __name__ == "__main__":
    main()
