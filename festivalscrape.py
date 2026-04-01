import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

from artists_categorize import bulk_categorize_artists, sync_artists_to_supabase
from classifier import VibeClassifier

load_dotenv()

# Setup Supabase Client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase URL or Key is missing from .env")
    exit(1)

supabase: Client = create_client(url, key)

EDMTRAIN_API_KEY = os.environ.get("EDMTRAIN_API_KEY")

def fetch_edmtrain_festivals():
    url = "https://edmtrain.com/api/events"
    params = {
        "festivalInd": "true",
        "client": EDMTRAIN_API_KEY
    }
    
    print("📡 Fetching festivals from EDMTrain...")
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("success"):
            events = data.get("data", [])
            print(f"✅ Downloaded {len(events)} events from EDMTrain.")
            return events
        else:
            print(f"❌ API Error: {data.get('message')}")
            return []
            
    except Exception as e:
        print(f"⚠️ Request failed: {e}")
        return []

def aggregate_edmtrain_festivals():
    events = fetch_edmtrain_festivals()
    if not events:
        return
        
    festivals_grouped = {}
    today = datetime.now().date()
    
    # 1. Group multi-day events by name
    for event in events:
        name = event.get('name')
        if not name:
            continue
            
        date_str = event.get('date')
        if not date_str:
            continue
            
        # Parse date to check if it's already in the past
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
            
        # Skip events that have already finished
        if event_date < today:
            continue 
            
        if name not in festivals_grouped:
            festivals_grouped[name] = {
                'start_date': date_str,
                'end_date': date_str,
                'venue': event.get('venue', {}),
                'artistList': []
            }
        else:
            curr_start = festivals_grouped[name]['start_date']
            curr_end = festivals_grouped[name]['end_date']
            
            if date_str < curr_start:
                festivals_grouped[name]['start_date'] = date_str
            if date_str > curr_end:
                festivals_grouped[name]['end_date'] = date_str
                
        # Consolidate Lineups
        for artist in event.get('artistList', []):
            artist_name = artist.get('name')
            if artist_name and artist_name not in festivals_grouped[name]['artistList']:
                festivals_grouped[name]['artistList'].append(artist_name)
                
    print(f"🔄 Grouped into {len(festivals_grouped)} distinct upcoming festival events.")
    
    processed_count = 0
    
    # 2. Process each unique festival
    for festival_name, fest_data in festivals_grouped.items():
        processed_count += 1
        print(f"\n[{processed_count}/{len(festivals_grouped)}] 🎪 Processing '{festival_name}'...")
        
        venue = fest_data['venue']
        location_str = venue.get('location')
        if not location_str:
            parts = [venue.get('city'), venue.get('state'), venue.get('country')]
            location_str = ", ".join([p for p in parts if p])
            
        fest_payload = {
            "name": festival_name,
            "start_date": fest_data['start_date'],
            "end_date": fest_data['end_date'],
            "lat": venue.get('latitude'),
            "lng": venue.get('longitude'),
            "location": location_str,
            "state": venue.get('state'),
            "city": venue.get('city'),
            "country": venue.get('country')
        }
        
        festival_id = None
        
        # 3. DB Sync - Festivals Table
        try:
            res = supabase.table("festivals").select("id, start_date, end_date").eq("name", festival_name).execute()
            if res.data:
                festival_id = res.data[0]['id']
                existing_start = res.data[0].get('start_date')
                existing_end = res.data[0].get('end_date')
                
                # Expand bounding dates if needed
                if existing_start:
                    fest_payload['start_date'] = min(existing_start, fest_payload['start_date'])
                if existing_end:
                    fest_payload['end_date'] = max(existing_end, fest_payload['end_date'])
                    
                supabase.table("festivals").update(fest_payload).eq("id", festival_id).execute()
            else:
                insert_res = supabase.table("festivals").insert(fest_payload).execute()
                if insert_res.data:
                    festival_id = insert_res.data[0]['id']
                    
        except Exception as e:
            print(f"❌ Database error linking festival '{festival_name}': {e}")
            continue
            
        if not festival_id:
            print(f"⚠️ Could not retrieve or create UUID for {festival_name}. Skipping line-up...")
            continue
            
        lineup = fest_data['artistList']
        if not lineup:
            print(f"   ↳ No lineup announced yet.")
            continue
            
        print(f"   ↳ Found {len(lineup)} unique artists in lineup.")
        
        # Rate limit padding
        time.sleep(1)
        
        # 4. Phase 1: Categorize Lineup using standard fallback architecture
        requests_list = [(name, [], False) for name in lineup]
        festival_artists_dict = bulk_categorize_artists(requests_list, supabase, max_workers=5)
        
        if not festival_artists_dict:
            continue
            
        # 5. Phase 2: Sync to Artists Table
        sync_artists_to_supabase(festival_artists_dict, supabase, user_id=None)
        
        # 6. Phase 3: Sync event_artists Junction Table
        slugs = [item['name'].lower().replace(" ", "-") for item in festival_artists_dict.values()]
        artist_ids = []
        batch_size = 100
        
        for i in range(0, len(slugs), batch_size):
            batch_slugs = slugs[i:i+batch_size]
            try:
                res = supabase.table("artists").select("id").in_("name_slug", batch_slugs).execute()
                if res.data:
                    artist_ids.extend([row['id'] for row in res.data])
            except Exception as e:
                print(f"❌ Error fetching bulk artist UUIDs: {e}")
                
        if artist_ids:
            try:
                res = supabase.table("event_artists").select("artist_id").eq("event_id", festival_id).execute()
                existing_event_artists = {row['artist_id'] for row in res.data} if res.data else set()
                
                inserts = [{"event_id": festival_id, "artist_id": aid} for aid in artist_ids if aid not in existing_event_artists]
                
                if inserts:
                    for i in range(0, len(inserts), batch_size):
                        batch = inserts[i:i+batch_size]
                        supabase.table("event_artists").insert(batch).execute()
            except Exception as e:
                print(f"❌ Database error updating event_artists for {festival_name}: {e}")
                
        # 7. Phase 4: Dynamic Re-Calculation of Festival DNA
        artist_dna_list = []
        artist_info_list = []
        
        for name, artist_data in festival_artists_dict.items():
            dna = artist_data.get('sonic_dna')
            genre_votes = artist_data.get('genre_votes', {})
            
            if dna and any(val > 0 for val in dna.values()):
                artist_dna_list.append({
                    'dna': dna,
                    'count': 1 # Lineups are unweighted (flat representation)
                })
                
            artist_info_list.append({
                'name': name,
                'genres_votes': genre_votes, # Replaces list mapping requirement
                'count': 1
            })
            
        festival_dna = VibeClassifier.calculate_dna(artist_dna_list)
        festival_subgenres = VibeClassifier.extract_top_subgenres(artist_info_list)
        
        # Apply Top 25 Constraint
        if festival_subgenres and len(festival_subgenres) > 25:
            festival_subgenres = dict(list(festival_subgenres.items())[:25])
            
        # 8. Phase 5: Upsert final DNA representation
        try:
            update_payload = {
                "lineup": lineup, # Store the raw text lineup array explicitly
                "sonic_dna": festival_dna,
                "subgenres": festival_subgenres
            }
            supabase.table("festivals").update(update_payload).eq("id", festival_id).execute()
            print(f"   ↳ ✅ Successfully generated and synced Vibe Vector.")
        except Exception as e:
            print(f"   ↳ ❌ Failed to upload DNA for {festival_name}: {e}")

if __name__ == "__main__":
    aggregate_edmtrain_festivals()
    print("\n🎉 Monthly Festival Aggregation Complete!")