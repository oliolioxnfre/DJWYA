import os
import time
import requests
import re
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

from artists_categorize import bulk_categorize_artists, sync_artists_to_supabase
from classifier import VibeClassifier

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase URL or Key is missing from .env")
    exit(1)

supabase: Client = create_client(url, key)
EDMTRAIN_API_KEY = os.environ.get("EDMTRAIN_API_KEY")

def fetch_edmtrain_festivals():
    url = "https://edmtrain.com/api/events"
    params = {"festivalInd": "true", "client": EDMTRAIN_API_KEY}
    
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

def parse_lineup_and_tba(artists_list):
    cleaned_artists = set()
    tba_flag = False
    
    for artist_name in artists_list:
        upper_name = artist_name.upper()
        
        if "TBA" in upper_name or "TBD" in upper_name:
            tba_flag = True
            continue
            
        if artist_name.count("?") >= 3:
            tba_flag = True
            continue
            
        match = re.search(r'\((.*?)\)', artist_name)
        if match:
            inner_content = match.group(1)
            # If inner contains split chars, extract and split
            if re.search(r'\s+&\s+|\s+x\s+|\s+b2b\s+', inner_content, flags=re.IGNORECASE):
                sub_artists = re.split(r'\s+&\s+|\s+x\s+|\s+b2b\s+', inner_content, flags=re.IGNORECASE)
                for sa in sub_artists:
                    if sa.strip():
                        cleaned_artists.add(sa.strip())
            else:
                base_name = re.sub(r'\s*\(.*?\)\s*', '', artist_name).strip()
                if base_name:
                    if re.search(r'\s+&\s+|\s+x\s+|\s+b2b\s+', base_name, flags=re.IGNORECASE):
                        sub_artists = re.split(r'\s+&\s+|\s+x\s+|\s+b2b\s+', base_name, flags=re.IGNORECASE)
                        for sa in sub_artists:
                            if sa.strip():
                                cleaned_artists.add(sa.strip())
                    else:
                        cleaned_artists.add(base_name)
        else:
            if re.search(r'\s+&\s+|\s+x\s+|\s+b2b\s+', artist_name, flags=re.IGNORECASE):
                sub_artists = re.split(r'\s+&\s+|\s+x\s+|\s+b2b\s+', artist_name, flags=re.IGNORECASE)
                for sa in sub_artists:
                    if sa.strip():
                        cleaned_artists.add(sa.strip())
            else:
                cleaned_artists.add(artist_name.strip())
                
    return list(cleaned_artists), tba_flag

def aggregate_edmtrain_festivals():
    events = fetch_edmtrain_festivals()
    if not events:
        return
        
    festivals_grouped = {}
    today = datetime.now().date()
    
    # 1. Group multi-day events
    for event in events:
        name = event.get('name')
        if not name:
            continue
            
        date_str = event.get('date')
        if not date_str:
            continue
            
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
            
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
            if date_str < curr_start: festivals_grouped[name]['start_date'] = date_str
            if date_str > curr_end: festivals_grouped[name]['end_date'] = date_str
                
        for artist in event.get('artistList', []):
            aname = artist.get('name')
            if aname and aname not in festivals_grouped[name]['artistList']:
                festivals_grouped[name]['artistList'].append(aname)
                
    print(f"🔄 Grouped into {len(festivals_grouped)} distinct upcoming events.")
    
    processed_count = 0
    for festival_name, fest_data in festivals_grouped.items():
        processed_count += 1
        print(f"\n[{processed_count}/{len(festivals_grouped)}] 🎪 Processing '{festival_name}'...")
        
        venue = fest_data['venue']
        location_str = venue.get('location')
        if not location_str:
            parts = [venue.get('city'), venue.get('state'), venue.get('country')]
            location_str = ", ".join([p for p in parts if p])
            
        # Analyze lineup & compute explicit TBA requirements
        cleaned_lineup, name_triggered_tba = parse_lineup_and_tba(fest_data['artistList'])
        
        start_date_obj = datetime.strptime(fest_data['start_date'], "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(fest_data['end_date'], "%Y-%m-%d").date()
        days_length = (end_date_obj - start_date_obj).days + 1
        artist_count = len(cleaned_lineup)
        
        is_tba = name_triggered_tba
        if days_length == 1 and artist_count < 8:
            is_tba = True
        elif days_length == 2 and artist_count < 20:
            is_tba = True
        elif days_length >= 3 and artist_count < 33:
            is_tba = True
            
        fest_payload = {
            "name": festival_name,
            "start_date": fest_data['start_date'],
            "end_date": fest_data['end_date'],
            "lat": venue.get('latitude'),
            "lng": venue.get('longitude'),
            "location": location_str,
            "state": venue.get('state'),
            "city": venue.get('city'),
            "country": venue.get('country'),
            "tba": is_tba
        }
        
        festival_id = None
        try:
            res = supabase.table("festivals").select("id, start_date, end_date").eq("name", festival_name).execute()
            if res.data:
                festival_id = res.data[0]['id']
                existing_start = res.data[0].get('start_date')
                existing_end = res.data[0].get('end_date')
                if existing_start: fest_payload['start_date'] = min(existing_start, fest_payload['start_date'])
                if existing_end: fest_payload['end_date'] = max(existing_end, fest_payload['end_date'])
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
            
        if not cleaned_lineup:
            print(f"   ↳ No lineup announced yet.")
            continue
            
        print(f"   ↳ Found {artist_count} unique artists in lineup. (TBA Status: {is_tba})")
        time.sleep(1)
        
        requests_list = [(name, [], False) for name in cleaned_lineup]
        festival_artists_dict = bulk_categorize_artists(requests_list, supabase, max_workers=5)
        
        if not festival_artists_dict:
            continue
            
        # Filter out unresolved Last.fm artists (artists yielding NO genres)
        filtered_artists = {}
        for name, data in festival_artists_dict.items():
            if data.get('genres') or data.get('genre_votes'):
                filtered_artists[name] = data
            else:
                print(f"   ↳ 🚫 Dropping '{name}': Not resolved on Last.fm & no prior DB mapping.")
                
        if not filtered_artists:
            print(f"   ↳ No valid electronic/mapped artists found in lineup. Continuing.")
            continue
            
        sync_artists_to_supabase(filtered_artists, supabase, user_id=None)
        
        slugs = [item['name'].lower().replace(" ", "-") for item in filtered_artists.values()]
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
                existing_ev = {row['artist_id'] for row in res.data} if res.data else set()
                inserts = [{"event_id": festival_id, "artist_id": aid} for aid in artist_ids if aid not in existing_ev]
                if inserts:
                    for i in range(0, len(inserts), batch_size):
                        supabase.table("event_artists").insert(inserts[i:i+batch_size]).execute()
            except Exception as e:
                print(f"❌ Database error updating event_artists for {festival_name}: {e}")
                
        artist_dna_list = []
        artist_info_list = []
        for name, data in filtered_artists.items():
            dna = data.get('sonic_dna')
            if dna and any(val > 0 for val in dna.values()):
                artist_dna_list.append({'dna': dna, 'count': 1})
            artist_info_list.append({'name': name, 'genres_votes': data.get('genre_votes', {}), 'count': 1})
            
        festival_dna = VibeClassifier.calculate_dna(artist_dna_list)
        festival_subgenres = VibeClassifier.extract_top_subgenres(artist_info_list)
        
        if festival_subgenres and len(festival_subgenres) > 25:
            festival_subgenres = dict(list(festival_subgenres.items())[:25])
            
        try:
            update_payload = {
                "lineup": list(filtered_artists.keys()), 
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