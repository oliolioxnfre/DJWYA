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

def get_user_data(user_id="demo_user"):
    """Fetches the user's aggregate Sonic DNA and Subgenres."""
    response = supabase.table("public.users").select("sonic_dna, subgenres").eq("id", user_id).execute()
    if response.data:
        return response.data[0]
    return None

def get_all_festivals():
    """Fetches all festivals including lineup, sonic_dna, and subgenres."""
    print("Fetching festivals...")
    response = supabase.table("festivals").select("name, lineup, sonic_dna, subgenres").execute()
    return response.data

def cosine_similarity(vec1, vec2):
    """
    Calculates cosine similarity between two sparse subgenre vectors (JSONB dicts).
    """
    if not vec1 or not vec2:
        return 0.0
        
    intersect = set(vec1.keys()) & set(vec2.keys())
    if not intersect:
        return 0.0
        
    dot_product = sum(vec1[k] * vec2[k] for k in intersect)
    mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
    mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
        
    return dot_product / (mag1 * mag2)

def calculate_hybrid_score(user_data, festival_data):
    """
    Final = (0.7 * SubgenreScore) + (0.3 * VibeScore)
    SubgenreScore: Cosine Similarity [0, 1]
    VibeScore: Exponential Decay of Euclidean Distance [0, 1]
    """
    from classifier import VibeClassifier
    
    user_dna = user_data.get('sonic_dna', {})
    fest_dna = festival_data.get('sonic_dna', {})
    user_subs = user_data.get('subgenres', {})
    fest_subs = festival_data.get('subgenres', {})
    
    # 1. Subgenre Cultural Fit (Cosine Similarity)
    s_score = cosine_similarity(user_subs, fest_subs)
    
    # 2. Vibe Fit (Euclidean Distance normalized via decay)
    dist = 0
    if user_dna and fest_dna:
        squared_diffs = []
        for cat in VibeClassifier.CATEGORIES:
            u_val = float(user_dna.get(cat, 0))
            f_val = float(fest_dna.get(cat, 0))
            squared_diffs.append((u_val - f_val) ** 2)
            
        dist = math.sqrt(sum(squared_diffs))
    else:
        dist = 10.0 # High penalty for missing DNA
        
    # Exponential decay: 0 dist = 1.0, 5 dist = ~0.47, 10 dist = ~0.22
    a_score = math.exp(-0.15 * dist)
    
    # Combined Hybrid Result
    hybrid_score = (0.7 * s_score) + (0.3 * a_score)
    return round(hybrid_score * 100, 2)

def run_matching_engine(user_id="demo_user"):
    user_artists_map = get_user_artists(user_id)
    user_data = get_user_data(user_id)
    festivals = get_all_festivals()
    
    if not user_artists_map or not user_data:
        print("Missing user data. Make sure DNA and Subgenres are synced!")
        return []

    match_scores = []

    for fest in festivals:
        fest_name = fest.get('name', 'Unknown Festival')
        raw_lineup = fest.get('lineup') or []
        
        lineup_set = set([artist.lower().strip() for artist in raw_lineup])
        if len(lineup_set) == 0:
            continue
            
        # 1. Hybrid Vibe/Culture Score
        synergy_percentage = calculate_hybrid_score(user_data, fest)
            
        # 2. Artist Overlap Score (Logarithmic)
        overlap = set(user_artists_map.keys()) & lineup_set
        artist_score_sum = 0
        for artist in overlap:
            count = user_artists_map[artist]
            score = math.log(count + 1, 1.75)
            artist_score_sum += score

        # 3. Final Scoring with Saturation
        artist_perc = (len(overlap) / len(lineup_set)) * 100
        
        if len(overlap) <= 2:
            sat_mult = 1.0
        elif len(overlap) <= 9:
            sat_mult = 1.5
        else:
            sat_mult = 2.0
            
        base_artist_score = artist_score_sum * sat_mult
        
        # Scaling: Synergy acts as the final "multiplier" filter
        total_score = base_artist_score * (synergy_percentage / 100)
        
        sorted_overlap = sorted(list(overlap), key=lambda x: user_artists_map.get(x, 0), reverse=True)
        
        match_scores.append({
            'festival': fest_name,
            'total_match': total_score,
            'artist_score': base_artist_score,
            'artist_perc': artist_perc,
            'synergy_match': synergy_percentage,
            'matched_count': len(overlap),
            'total_artists': len(lineup_set),
            'shared_artists': [name.title() for name in sorted_overlap] 
        })
        
    match_scores.sort(key=lambda x: x['total_match'], reverse=True)
    return match_scores

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    print("Starting Hybrid Match Engine...\n")
    # Using a valid UUID for a test user if possible, or demo_user
    test_uid = "af78e583-fb39-4a05-9ec4-7bc4bb2286e6"
    results = run_matching_engine(test_uid) 
    
    if results:
        print("\n--- YOUR SONIC DNA HYBRID MATCHES ---")
        for match in results:
            if match['total_match'] > 0:
                print(f"🔥 {match['festival']}")
                print(f"   Hybrid Match Score: {match['synergy_match']:.1f}%")
                print(f"   Artist Overlap:     {match['matched_count']}/{match['total_artists']} ({match['artist_perc']:.1f}%)")
                print(f"   Shared Artists:     {', '.join(match['shared_artists'][:5])}...")
                print("-" * 40 + "\n")