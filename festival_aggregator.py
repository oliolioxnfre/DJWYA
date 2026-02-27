import os
import csv
import glob
from dotenv import load_dotenv
from supabase import create_client, Client
from artists_categorize import categorize_artist, bulk_categorize_artists, sync_artists_to_supabase

load_dotenv()

# Setup Supabase Client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase URL or Key is missing from .env")
    exit(1)

supabase: Client = create_client(url, key)

def aggregate_csv_festivals():
    # Find all CSV files in the FestivalCSV folder
    csv_files = glob.glob(os.path.join("FestivalCSV", "*.csv"))
    
    if not csv_files:
        print("No CSV files found in 'FestivalCSV/' directory.")
        return
        
    for filepath in csv_files:
        # Clean up the filename to make a readable festival name
        filename = os.path.basename(filepath)
        festival_name = filename.replace('.csv', '').replace('_', ' ')
        
        unique_artists_counts = {} # name -> count
        
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # The column with artist names is usually 'Artist Name(s)'
                artists_str = row.get('Artist Name(s)', '')
                if artists_str:
                    # Split by semicolon to separate collaborations
                    collaborators = [name.strip() for name in artists_str.split(';')]
                    for name in collaborators:
                        unique_artists_counts[name] = unique_artists_counts.get(name, 0) + 1
        
        artists_list = list(unique_artists_counts.keys())
        print(f"\n[{festival_name}] Found {len(artists_list)} unique artists ({sum(unique_artists_counts.values())} total entries).")
        
        # Phase 1: Categorize all artists (Using optimized bulk lookup)
        print(f"[{festival_name}] Categorizing artists...")
        
        # Prepare requests: (name, fallback_genres, filter_electronic)
        # We set filter_electronic=False for festival lineups
        requests = [(name, [], False) for name in artists_list]
        
        festival_artists_dict = bulk_categorize_artists(requests, supabase)
                
        # Phase 2: Sync to artists database
        print(f"[{festival_name}] Syncing {len(festival_artists_dict)} artists to Supabase 'artists' table...")
        sync_artists_to_supabase(festival_artists_dict, supabase, user_id=None)
 
        # Phase 3: Calculate Festival DNA and Subgenre Vector
        print(f"[{festival_name}] Calculating aggregate Sonic DNA & Subgenres...")
        from classifier import VibeClassifier
        
        artist_dna_list = []
        artist_info_list = [] # For subgenre extraction
        
        for name, artist_data in festival_artists_dict.items():
            dna = artist_data.get('sonic_dna')
            genres = artist_data.get('genres', [])
            count = unique_artists_counts.get(name, 1)
            
            if dna and any(val > 0 for val in dna.values()):
                artist_dna_list.append({
                    'dna': dna,
                    'count': count
                })
            
            artist_info_list.append({
                'name': name,
                'genres': genres,
                'count': count
            })
        
        festival_dna = VibeClassifier.calculate_dna(artist_dna_list)
        festival_subgenres = VibeClassifier.extract_top_subgenres(artist_info_list, limit=25)
        
        print(f"[{festival_name}] Calculated DNA: {festival_dna}")
        print(f"[{festival_name}] Calculated Subgenres: {len(festival_subgenres)} keys")
        
        # Phase 4: Prepare and insert payload
        print(f"[{festival_name}] Uploading festival to Supabase...")
        payload = {
            "name": festival_name,
            "lineup": artists_list,
            "sonic_dna": festival_dna,
            "subgenres": festival_subgenres
        }
        
        try:
            # Insert since there is no unique constraint on the 'name' column
            response = supabase.table("festivals").insert(payload).execute()
        except Exception as e:
            print(f"Failed to upload {festival_name}: {e}")

if __name__ == "__main__":
    aggregate_csv_festivals()
    print("\nAggregation complete!")

