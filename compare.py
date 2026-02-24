import os
import math
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Setup Connection
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_user_artists(user_id="demo_user"):
    """Fetches identifying artist names and play counts from user_lib."""
    print(f"Fetching library for {user_id}...")
    
    # Fetch count along with Joined artist name
    response = supabase.table("user_lib").select("count, artists(name)").eq("user_id", user_id).execute()
    
    user_artists = {} # name -> count
    for row in response.data:
        if row.get('artists') and row['artists'].get('name'):
            clean_name = row['artists']['name'].lower().strip()
            user_artists[clean_name] = row.get('count', 1)
            
    return user_artists

def get_user_dna(user_id="demo_user"):
    """Fetches the user's aggregate Sonic DNA."""
    response = supabase.table("public.users").select("sonic_dna").eq("id", user_id).execute()
    if response.data and response.data[0].get('sonic_dna'):
        return response.data[0]['sonic_dna']
    return None

def get_all_festivals():
    """Fetches all festivals including lineup and sonic_dna."""
    print("Fetching festivals...")
    response = supabase.table("festivals").select("name, lineup, sonic_dna").execute()
    return response.data

def run_matching_engine(user_id="demo_user"):
    user_artists_map = get_user_artists(user_id)
    user_dna = get_user_dna(user_id)
    festivals = get_all_festivals()
    
    if not user_artists_map:
        print("No artists found in user_lib. Make sure your app.py synced correctly!")
        return

    match_scores = []

    for fest in festivals:
        fest_name = fest.get('name', 'Unknown Festival')
        raw_lineup = fest.get('lineup') or []
        fest_dna = fest.get('sonic_dna')
        
        lineup_set = set([artist.lower().strip() for artist in raw_lineup])
        
        if len(lineup_set) == 0:
            continue
            
        # 1. Calculate Artist Scores (Logarithmic)
        overlap = set(user_artists_map.keys()) & lineup_set
        artist_score_sum = 0
        for artist in overlap:
            count = user_artists_map[artist]
            # log_1.75(count + 1)
            score = math.log(count + 1, 1.75)
            artist_score_sum += score

        # 2. Calculate Genre Synergy (Exponential Decay)
        synergy_percentage = 0
        dist = 0
        if user_dna and fest_dna:
            # Note: Ensure 'bass' matches your exact Supabase JSON key! 
            # (We used 'weight' earlier, but 'bass' is fine if that's what you saved)
            categories = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']
            squared_diffs = []
            for cat in categories:
                u_val = float(user_dna.get(cat, 0))
                f_val = float(fest_dna.get(cat, 0))
                squared_diffs.append((u_val - f_val) ** 2)
            
            dist = math.sqrt(sum(squared_diffs))
            
            # Exponential decay: 0 dist = 100%, 5 dist = ~47%, 10 dist = ~22%
            synergy_percentage = 100 * math.exp(-0.15 * dist)

        # 3. Final Score Calculation (The "God-Tier" Math)
        artist_perc = (len(overlap) / len(lineup_set)) * 100 if len(lineup_set) > 0 else 0
        
        # We apply the Saturation Multiplier we talked about
        # Reward festivals where they know a good "pack" of artists
        if len(overlap) <= 2:
            sat_mult = 1.0
        elif len(overlap) <= 9:
            sat_mult = 1.5
        else:
            sat_mult = 2.0
            
        base_score = artist_score_sum * sat_mult
        
        # The Synergy Multiplier: 
        # Base score is modified by how well the overall festival matches their DNA
        # We divide by 100 because synergy_percentage is a whole number (e.g., 85.5)
        total_score = base_score * (synergy_percentage / 100)
        
        # Sort overlap artists by play count descending
        sorted_overlap = sorted(list(overlap), key=lambda x: user_artists_map.get(x, 0), reverse=True)
        
        match_scores.append({
            'festival': fest_name,
            'total_match': total_score, # Now properly scaled
            'artist_score': base_score,
            'artist_perc': artist_perc,
            'synergy_match': synergy_percentage, # Renamed for clarity
            'matched_count': len(overlap),
            'total_artists': len(lineup_set),
            'shared_artists': [name.title() for name in sorted_overlap] 
        })
        
    # Sort highest score to lowest
    match_scores.sort(key=lambda x: x['total_match'], reverse=True)
    return match_scores

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    print("Starting Match Engine...\n")
    results = run_matching_engine("db65253d-6643-4607-8988-7770f0193a13") 
    
    if results:
        print("\n--- YOUR PROPRIETARY FESTIVAL MATCHES ---")
        for match in results:
            # Only show festivals where there is at least some match
            if match['total_match'] > 0:
                print(f"🔥 {match['festival']}")
                print(f"   Artist % Match: {match['artist_perc']:.1f}%")
                print(f"   Artist Score:   {match['artist_score']:.2f}")
                print(f"   Synergy Match:    {match['synergy_match']:.2f}")
                print(f"   Total Match:    {match['total_match']:.2f}")
                print(f"   Artist Overlap: {', '.join(match['shared_artists'])} ({match['matched_count']}/{match['total_artists']})")
                print("-" * 40 + "\n")