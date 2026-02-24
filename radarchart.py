import plotly.graph_objects as go
import pandas as pd
from classifier import VibeClassifier
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")


# Assuming your VibeClassifier class is in the same file or imported
# from classifier import VibeClassifier

def visualize_vibes(artist_data_list, user_id):
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

def fetch_user_dna(user_id):
    supabase: Client = create_client(url, key)
    res = supabase.table("public.users").select("sonic_dna").eq("id", user_id).execute()
    if res.data and res.data[0].get('sonic_dna'):
        return res.data[0]['sonic_dna']
    return None

if __name__ == "__main__":
    u_id = "db65253d-6643-4607-8988-7770f0193a13"
    user_dna = fetch_user_dna(u_id)
    if not user_dna:
        print("No DNA profile found in the database. Run app.py or test_db.py first!")
    else:
        print(f"Generating radar chart for user: {u_id}")
        # visualize_vibes expects a list of artist objects
        visualize_vibes([{'name': 'My Profile', 'dna': user_dna, 'count': 1}], u_id)