import plotly.graph_objects as go
import pandas as pd

# Assuming your VibeClassifier class is in the same file or imported
# from classifier import VibeClassifier

def visualize_vibes(artist_data_list):
    """
    artist_data_list: List of dicts like [{'name': 'Artist', 'dna': {...}}]
    """
    if not artist_data_list:
        print("No artist data provided to visualize.")
        return

    fig = go.Figure()

    # The 6 axes we defined
    categories = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing']
    
    # Init average dict
    avg_dna = {cat: 0.0 for cat in categories}
    num_artists = len(artist_data_list)

    # Sum all the values
    for artist in artist_data_list:
        dna = artist['dna']
        for cat in categories:
            avg_dna[cat] += float(dna.get(cat, 0.0))
            
    # Divide to get averages
    for cat in categories:
        avg_dna[cat] /= num_artists

    # Plotly requires the first category to be repeated at the end to close the loop
    values = [avg_dna[cat] for cat in categories]
    values.append(values[0])
    display_cats = categories + [categories[0]]

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=display_cats,
        fill='toself',
        name=f"Average ({num_artists} Artists)",
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

def fetch_all_artist_dna():
    """Queries the artists table for all artists that have sonic_dna attached."""
    print("Fetching sonic DNA from library...")
    response = supabase.table("artists").select("name, sonic_dna").not_.is_("sonic_dna", "null").execute()
    
    artist_data_list = []
    for row in response.data:
        # Validate that the dna is a dictionary with all required keys
        dna = row.get("sonic_dna")
        name = row.get("name", "Unknown Artist")
        
        if dna and isinstance(dna, dict):
            # Only add if it has all the standard categories
            categories = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing']
            if all(cat in dna for cat in categories):
                artist_data_list.append({
                    'name': name,
                    'dna': dna
                })
                
    return artist_data_list

if __name__ == "__main__":
    db_artists = fetch_all_artist_dna()
    if not db_artists:
        print("No artists with sonic_dna found in the database. Run app.py to sync your library first!")
    else:
        print(f"Loaded {len(db_artists)} artists. Generating radar chart...")
        visualize_vibes(db_artists)