import os
import csv
import glob
from dotenv import load_dotenv
from supabase import create_client, Client
from artists_categorize import categorize_artist, sync_artists_to_supabase

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
        
        unique_artists = set()
        
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # The column with artist names is usually 'Artist Name(s)'
                artists_str = row.get('Artist Name(s)', '')
                if artists_str:
                    # Split by semicolon to separate collaborations
                    collaborators = [name.strip() for name in artists_str.split(';')]
                    unique_artists.update(collaborators)
        
        artists_list = list(unique_artists)
        print(f"\n[{festival_name}] Found {len(artists_list)} unique artists.")
        
        # Phase 1: Categorize all artists
        print(f"[{festival_name}] Categorizing artists from Last.fm...")
        festival_artists_dict = {}
        for artist_name in artists_list:
            # We don't filter out non-electronic genres because these are electronic festivals
            categorized = categorize_artist(artist_name, fallback_genres=[], filter_electronic=False)
            if categorized:
                festival_artists_dict[artist_name] = categorized
                
        # Phase 2: Sync to artists database
        print(f"[{festival_name}] Syncing {len(festival_artists_dict)} artists to Supabase 'artists' table...")
        sync_artists_to_supabase(festival_artists_dict, supabase, user_id=None)

        # Phase 3: Calculate Festival DNA
        print(f"[{festival_name}] Calculating aggregate Sonic DNA...")
        festival_dna = {'intensity': 0.0, 'euphoria': 0.0, 'space': 0.0, 'pulse': 0.0, 'chaos': 0.0, 'swing': 0.0}
        total_artists_with_dna = 0

        for artist_data in festival_artists_dict.values():
            dna = artist_data.get('sonic_dna')
            if dna and sum(dna.values()) > 0:
                total_artists_with_dna += 1
                for cat in festival_dna.keys():
                    festival_dna[cat] += dna.get(cat, 0)
        
        if total_artists_with_dna > 0:
            festival_dna = {k: round(v / total_artists_with_dna, 1) for k, v in festival_dna.items()}
        
        print(f"[{festival_name}] Calculated DNA: {festival_dna}")
        
        # Phase 4: Prepare and insert payload
        print(f"[{festival_name}] Uploading festival to Supabase...")
        payload = {
            "name": festival_name,
            "lineup": artists_list,
            "sonic_dna": festival_dna
        }
        
        try:
            # Insert since there is no unique constraint on the 'name' column
            response = supabase.table("festivals").insert(payload).execute()
        except Exception as e:
            print(f"Failed to upload {festival_name}: {e}")

if __name__ == "__main__":
    aggregate_csv_festivals()
    print("\nAggregation complete!")

