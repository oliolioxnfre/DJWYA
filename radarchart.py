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

    # --- RELATIVE NORMALIZATION ---
    # Because averages flatten the shape, we scale the entire graph so the highest peak hits 10.
    current_max = max(avg_dna.values())
    if current_max > 0:
        scaler = 10.0 / current_max
        for cat in categories:
            avg_dna[cat] *= scaler

    # Plotly requires the first category to be repeated at the end to close the loop
    values = [avg_dna[cat] for cat in categories]
    values.append(values[0])
    display_cats = categories + [categories[0]]

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=display_cats,
        fill='toself',
        name=f"Scaled Average ({len(artist_data_list)} Artists, {total_plays} Plays)",
        fillcolor='rgba(255, 75, 75, 0.5)', # Vibrant red fill
        line=dict(color='rgba(255, 75, 75, 1.0)'),
        opacity=0.7
    ))

    # --- OUTER BOUNDARY ---
    # Draw a line connecting all the outer points for visual reference
    fig.add_trace(go.Scatterpolar(
        r=[10, 10, 10, 10, 10, 10, 10], 
        theta=display_cats,
        mode='lines',
        name="Max Potential",
        line=dict(color='rgba(200, 200, 200, 0.8)', width=2, dash='dash'),
    ))

    # --- OUTER COMPLETE GRAPH (K6) ---
    # Connect every vertex to every other vertex for a "complete graph" aesthetic at the max level
    for i in range(len(categories)):
        for j in range(i + 1, len(categories)):
            fig.add_trace(go.Scatterpolar(
                r=[10, 10],
                theta=[categories[i], categories[j]],
                mode='lines',
                line=dict(color='rgba(200, 200, 200, 0.3)', width=1),
                showlegend=False,
                hoverinfo='skip'
            ))

    fig.update_layout(
        polar=dict(
            gridshape='linear',
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                gridcolor='rgba(255, 255, 255, 0.1)',
            ),
            angularaxis=dict(
                gridcolor='rgba(255, 255, 255, 0.1)',
                linecolor='rgba(255, 255, 255, 0.2)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        title="Average Sonic DNA Profile (Normalized & Scaled)",
        template="plotly_dark",
        paper_bgcolor='rgba(15, 15, 15, 1)',
        plot_bgcolor='rgba(0,0,0,0)'
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