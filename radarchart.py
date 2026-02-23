import plotly.graph_objects as go
import pandas as pd

# Assuming your VibeClassifier class is in the same file or imported
# from classifier import VibeClassifier

def visualize_vibes(artist_data_list, user_id="demo_user"):
    """
    artist_data_list: List of dicts like [{'name': 'Artist', 'dna': {...}, 'count': 5}]
    """
    if not artist_data_list:
        print("No artist data provided to visualize.")
        return

    fig = go.Figure()

    # The 6 axes we defined
    categories = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing']
    
    # Init average dict
    avg_dna = {cat: 0.0 for cat in categories}
    total_plays = sum(artist.get('count', 1) for artist in artist_data_list)
    
    if total_plays == 0:
        total_plays = 1

    # Sum all the values weighted by play count
    for artist in artist_data_list:
        dna = artist['dna']
        count = artist.get('count', 1)
        for cat in categories:
            avg_dna[cat] += float(dna.get(cat, 0.0)) * count
            
    # Divide to get weighted averages
    for cat in categories:
        avg_dna[cat] /= total_plays

    # Plotly requires the first category to be repeated at the end to close the loop
    values = [avg_dna[cat] for cat in categories]
    values.append(values[0])
    display_cats = categories + [categories[0]]

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=display_cats,
        fill='toself',
        name=f"Average ({len(artist_data_list)} Artists, {total_plays} Plays)",
        opacity=0.7
    ))

    fig.update_layout(
        polar=dict(
            gridshape='linear',
            radialaxis=dict(
                visible=True,
                range=[0, 10]  # Fixed scale 0-10
            )),
        showlegend=True,
        title="Average Sonic DNA Profile"
    )

    fig.show()

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# --- DB CONNECTION ---
load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_all_artist_dna(user_id="demo_user"):
    """Queries the user_lib table joined with artists to get play counts and sonic_dna."""
    print(f"Fetching sonic DNA and play counts for {user_id}...")
    
    # We ask for the user_lib row, but ALSO tell Supabase 
    # to look up the name and sonic_dna from the artists table.
    response = supabase.table("user_lib").select("count, artists(name, sonic_dna)").eq("user_id", user_id).execute()
    
    artist_data_list = []
    for row in response.data:
        play_count = row.get("count", 1)
        artist_info = row.get('artists')
        if not artist_info:
            continue
            
        dna = artist_info.get("sonic_dna")
        name = artist_info.get("name", "Unknown Artist")
        
        if dna and isinstance(dna, dict):
            # Only add if it has all the standard categories
            categories = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing']
            if all(cat in dna for cat in categories):
                artist_data_list.append({
                    'name': name,
                    'dna': dna,
                    'count': play_count
                })
                
    return artist_data_list

if __name__ == "__main__":
    db_artists = fetch_all_artist_dna()
    if not db_artists:
        print("No artists with sonic_dna found in the database. Run app.py to sync your library first!")
    else:
        print(f"Loaded {len(db_artists)} artists. Generating radar chart...")
        visualize_vibes(db_artists)