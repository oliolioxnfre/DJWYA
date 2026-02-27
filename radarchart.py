import plotly.graph_objects as go
import pandas as pd
from classifier import VibeClassifier
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")


def radarchart(artist_data_list, user_id, scale=True, round_even=True):
    """
    artist_data_list: List of dicts like [{'name': 'Artist', 'dna': {...}, 'count': 5}]
    Renders a 7-axis heptagonal radar chart with a complete K7 graph overlay.
    """
    if not artist_data_list:
        print("No artist data provided to visualize.")
        return

    fig = go.Figure()

    # The 7 axes of the Sonic DNA heptagon
    categories = ['intensity', 'euphoria', 'space', 'pulse', 'chaos', 'swing', 'bass']
    
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
    if scale:
        current_max = max(avg_dna.values())
        if current_max > 0:
            scaler = 10.0 / current_max
            for cat in categories:
                avg_dna[cat] *= scaler
                
                if round_even:
                    # Round to nearest even number (0, 2, 4, 6, 8, 10)
                    avg_dna[cat] = round(avg_dna[cat] / 2.0) * 2
    elif round_even:
        for cat in categories:
            avg_dna[cat] = round(avg_dna[cat] / 2.0) * 2

    # Color Theme (using highest category for hue)
    max_cat_key = max(avg_dna, key=avg_dna.get)
    max_idx = categories.index(max_cat_key)
    max_hue = max_idx * (360 / 7)
    color_theme = 'rgba(155,155,155,0.4)' # Defaulting to grey as per user's starchart override

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
        opacity=0
    ))

    # --- OUTER BOUNDARY (Heptagon) ---
    # Draw a line connecting all 7 outer points for visual reference
    fig.add_trace(go.Scatterpolar(
        r=[10, 10, 10, 10, 10, 10, 10, 10], 
        theta=display_cats,
        mode='lines',
        name="Max Potential",
        line=dict(color=color_theme, width=5, dash='dash'),
    ))

    # --- OUTER COMPLETE GRAPH (K7) ---
    # Connect every vertex to every other vertex for a complete heptagonal graph
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
                rotation=90,
                direction='clockwise',
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


def starchart(artist_data_list, user_id, scale=True, round_even=True):
    """
    Renders a 7-axis heptagonal star chart (spiky star geometry).
    Creates a 14-point path alternating between data values and origin (0).
    """
    if not artist_data_list:
        print("No artist data provided to starchart.")
        return

    fig = go.Figure()

    # The 7 axes of the Sonic DNA heptagon
    categories = ['INTENSITY', 'EUPHORIA', 'SPACE', 'PULSE', 'CHAOS', 'SWING', 'BASS']
    cat_keys = [c.lower() for c in categories]
    
    # Init average dict
    avg_dna = {cat: 0.0 for cat in cat_keys}
    total_plays = sum(artist.get('count', 1) for artist in artist_data_list)
    
    if total_plays == 0:
        total_plays = 1

    # Sum all the values weighted by play count
    for artist in artist_data_list:
        dna = artist['dna']
        count = artist.get('count', 1)
        for cat in cat_keys:
            avg_dna[cat] += float(dna.get(cat, 0.0)) * count
            
    # Divide and Scale (weighted averages -> 0-10)
    for cat in cat_keys:
        avg_dna[cat] /= total_plays
    
    if scale:
        current_max = max(avg_dna.values())
        if current_max > 0:
            scaler = 10.0 / current_max
            for cat in cat_keys:
                avg_dna[cat] *= scaler
                if round_even:
                    # Round to nearest even number (0, 2, 4, 6, 8, 10)
                    avg_dna[cat] = round(avg_dna[cat] / 2.0) * 2
    elif round_even:
        for cat in cat_keys:
            avg_dna[cat] = round(avg_dna[cat] / 2.0) * 2

    # Color Theme
    max_cat_key = max(avg_dna, key=avg_dna.get)
    max_idx = cat_keys.index(max_cat_key)
    max_hue = max_idx * (360 / 7)
    color_theme = f'hsla({max_hue}, 60%, 35%, 0.8)'
    color_theme = 'rgba(155,155,155,0.4)'
    
    # --- GEOMETRY CALCULATION (14 points for a 7-pointed star) ---
    # We use alternating Peak (data value) and Valley (inner base)
    angles = []
    r_values = []
    
    # A base radius for the "valleys" creates the triangular spike look
    # Increasing this makes the star's base wider
    valley_r = 3.56 
    
    for i in range(len(categories)):
        # 1. Peak Angle (The tip of the spike)
        peak_angle = i * (360 / 7)
        angles.append(peak_angle)
        r_values.append(avg_dna[cat_keys[i]])
        
        # 2. Valley Angle (The inner dip between spikes)
        # Offset by half a step (360/14) to be exactly between axes
        valley_angle = peak_angle + (360 / 14)
        angles.append(valley_angle)
        r_values.append(valley_r) 
    
    # Close the loop
    angles.append(angles[0])
    r_values.append(r_values[0])

    # --- INDIVIDUAL COLORED DIAMONDS ---
    # We create 7 diamond shapes that meet at the center (r=0)
    hues = [i * (360 / 7) for i in range(7)]
    max_cat_key = max(avg_dna, key=avg_dna.get)
    max_idx = cat_keys.index(max_cat_key)
    max_hue = max_idx * (360 / 7)
    
    for i, (cat, hue) in enumerate(zip(categories, hues)):
        peak_val = avg_dna[cat_keys[i]]
        
        # Diamond Coordinates: Center -> Left Shoulder -> Tip -> Right Shoulder -> Center
        dia_angles = [
            i * (360/7),            # Center Point
            i * (360/7) - (360/14), # Left Shoulder (Valley)
            i * (360/7),            # Peak Tip
            i * (360/7) + (360/14), # Right Shoulder (Valley)
            i * (360/7)             # Back to Center
        ]
        
        dia_r = [1.33, valley_r, peak_val, valley_r, 1.33]
        
        # Unique color for this diamond
        color = f'hsla({hue}, 80%, 55%, 0.55)'
        line_color = f'hsla({hue}, 80%, 55%, 0.9)'
        
        fig.add_trace(go.Scatterpolar(
            r=dia_r,
            theta=dia_angles,
            fill='toself',
            name=cat,
            fillcolor=color,
            line=dict(color=line_color, width=1.5),
            marker=dict(size=4, color='white', symbol='diamond'),
            hoverinfo='name+r'
        ))


    # --- RADIAL AXIS DOTS ---
    # Draw dots at r = 2, 4, 6, 8, 10 for each of the 7 axes
    for i in range(7):
        axis_angle = i * (360 / 7)
        fig.add_trace(go.Scatterpolar(
            r=[2, 4, 6, 8, 10],
            theta=[axis_angle] * 5,
            mode='markers',
            marker=dict(
                size=4,
                color='rgba(255, 255, 255, 0.4)',
                symbol='circle'
            ),
            showlegend=False,
            hoverinfo='skip'
        ))


    # --- OUTER BOUNDARY (Static Heptagon) ---
    outer_angles = [i * (360 / 7) for i in range(7)]
    outer_angles.append(outer_angles[0])
    fig.add_trace(go.Scatterpolar(
        r=[10] * 8,
        theta=outer_angles,
        mode='lines',
        name="MAX POTENTIAL",
        line=dict(color=color_theme, width=5), #remove dash if you want
    ))

    # --- ACUTE HEPTAGRAM {7/3} BACKGROUND STAR ---
    # Creates a sharper background star (3x thicker)
    acute_angles = [(i * 3 * (360 / 7)) for i in range(8)]
    fig.add_trace(go.Scatterpolar(
        r=[10] * 8,
        theta=acute_angles,
        mode='lines',
        name="ACUTE HEPTAGRAM",
        line=dict(color=color_theme, width=2.8),
        showlegend=False,
        hoverinfo='skip'
    ))

    # --- OBTUSE HEPTAGRAM {7/2} BACKGROUND STAR ---
    # Creates the wider background star (standard thickness)
    obtuse_angles = [(i * 2 * (360 / 7)) for i in range(8)]
    fig.add_trace(go.Scatterpolar(
        r=[10] * 8,
        theta=obtuse_angles,
        mode='lines',
        name="OBTUSE HEPTAGRAM",
        line=dict(color=color_theme, width=1.0),
        showlegend=False,
        hoverinfo='skip'
    ))

    # --- UPSIDEDOWN ACUTE INNER HEPTAGRAM (Rotated) ---
    # Adds a final layer of geometric depth with a color matching the highest category
    inverted_angles = [(i * 3 * (360 / 7)) + (360 / 14) for i in range(8)]
    fig.add_trace(go.Scatterpolar(
        r=[3.56] * 8, #2.175 = inner
        theta=inverted_angles,
        fill='toself',
        fillcolor='rgba(150, 150, 150, 0.1)',
        mode='lines',
        name="INVERTED HEPTAGRAM",
        line=dict(color=color_theme, width=1.5),
        showlegend=False,
        hoverinfo='skip'
    ))

    fig.update_layout(
        polar=dict(
            gridshape='linear',
            radialaxis=dict(visible=False, range=[0, 10]),
            angularaxis=dict(
                rotation=90,
                direction='clockwise',
                tickvals=[i * (360 / 7) for i in range(7)],
                ticktext=categories,
                gridcolor=color_theme,
                linecolor=color_theme
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=True,
        title="SONIC DNA STAR CHART (Normalized & Scaled)",
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
    u_id = "af78e583-fb39-4a05-9ec4-7bc4bb2286e6"
    user_dna = fetch_user_dna(u_id)
    if not user_dna:
        print("No DNA profile found in the database. Run app.py or test_db.py first!")
    else:
        print(f"Generating Persona 5 Star Chart for user: {u_id}")
        starchart([{'name': 'My Profile', 'dna': user_dna, 'count': 1}], u_id)