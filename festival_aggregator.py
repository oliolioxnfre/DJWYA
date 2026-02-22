import os
import csv
import glob
from dotenv import load_dotenv
from supabase import create_client, Client

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
        
        print(f"[{festival_name}] Found {len(artists_list)} unique artists. Uploading to Supabase...")
        
        # Prepare payload
        payload = {
            "name": festival_name,
            "lineup": artists_list
        }
        
        try:
            # Insert since there is no unique constraint on the 'name' column
            response = supabase.table("festivals").insert(payload).execute()
        except Exception as e:
            print(f"Failed to upload {festival_name}: {e}")

if __name__ == "__main__":
    aggregate_csv_festivals()
    print("\nAggregation complete!")

