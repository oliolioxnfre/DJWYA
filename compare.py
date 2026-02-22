import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Setup Connection
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def get_user_artists(user_id="demo_user"):
    """Fetches the user's liked artists directly from Supabase."""
    print(f"Fetching library for {user_id}...")
    
    # The Magic Join: We ask for the user_lib row, but ALSO tell Supabase 
    # to look up the UUID and hand us back the text 'name' from the artists table.
    response = supabase.table("user_lib").select("artists(name)").eq("user_id", user_id).execute()
    
    user_artists = set()
    for row in response.data:
        # Check if the join succeeded and the artist name exists
        if row.get('artists') and row['artists'].get('name'):
            # Lowercase it to make comparison bulletproof
            clean_name = row['artists']['name'].lower().strip()
            user_artists.add(clean_name)
            
    return user_artists

def get_all_festivals():
    """Fetches all festivals and their JSONB lineups."""
    print("Fetching festivals...")
    response = supabase.table("festivals").select("name, lineup").execute()
    return response.data

def run_matching_engine(user_id="demo_user"):
    user_artists = get_user_artists(user_id)
    festivals = get_all_festivals()
    
    if not user_artists:
        print("No artists found in user_lib. Make sure your app.py synced correctly!")
        return

    match_scores = []

    for fest in festivals:
        fest_name = fest.get('name', 'Unknown Festival')
        raw_lineup = fest.get('lineup') or [] # Handle NULL lineups
        
        # Lowercase the festival lineup so it matches the user library perfectly
        lineup_set = set([artist.lower().strip() for artist in raw_lineup])
        
        # Cybersecurity check: Prevent division by zero if a festival has an empty lineup
        if len(lineup_set) == 0:
            continue
            
        # The Math: Intersect the two sets
        overlap = user_artists & lineup_set
        match_percentage = (len(overlap) / len(lineup_set)) * 100
        
        match_scores.append({
            'festival': fest_name,
            'score': match_percentage,
            'matched_count': len(overlap),
            'total_artists': len(lineup_set),
            # Capitalize the names nicely for the printout
            'shared_artists': [name.title() for name in overlap] 
        })
        
    # Sort highest percentage to lowest
    match_scores.sort(key=lambda x: x['score'], reverse=True)
    return match_scores

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    print("Starting Match Engine...\n")
    results = run_matching_engine("demo_user")
    
    if results:
        print("\n--- YOUR TOP FESTIVAL MATCHES ---")
        for match in results:
            # Only show festivals where there is at least a 1% match
            if match['score'] > 0:
                print(f"🔥 {match['festival']}: {match['score']:.1f}% Match ({match['matched_count']}/{match['total_artists']} Artists)")
                print(f"   Lineup overlaps: {', '.join(match['shared_artists'])}\n")