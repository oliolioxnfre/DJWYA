# 🧠 DJWYA Project Context & Memory Bank

## 📋 Handover Instructions
If you are switching accounts, please follow these steps to ensure I (in your new account) am fully caught up:
1.  **Open this file** (`gemini.md`) in the workspace.
2.  **Tell me:** *"Hey Gemini, I've switched accounts. Please read `gemini.md` to get the context of where we are in the DJWYA project."*
3.  I will then process this summary and we can continue exactly where we left off.

---

## 🚀 Project Overview: DJWYA
**DJWYA (DJ WHERE YOU AT!??)** is a sophisticated music analysis tool that scours the internet for festivals featuring your favorite DJs based on your unique **Sonic DNA**. The main goal of this project is to help you discover new festivals, find where your favorite artists are playing, and categorize/classify your taste in electronic music, your favorite artists taste in electronic music, and festivals types of electronic music. Core beleif: Electronic Music is the widest genre of music and often is difficult to navigate the landscape of electronic music. Everyone likes some form of electronic music but almost no one knows where to start or how to describe their preference. Electronic music is for everyone. 

### 🛠 Tech Stack
- **Backend:** Python
- **Database:** Supabase (PostgreSQL)
- **APIs:** Spotify (Spotipy), Last.fm (Pylast)
- **Visuals:** Matplotlib/Starchart for Radar Charts

---

## 🏗 Core Architecture
1.  **`classifier.py`**: The "Brain".
    - **`VibeClassifier`**: Maps subgenres to a 7-axis sonic vector: `[Intensity, Euphoria, Space, Pulse, Chaos, Swing, Bass]`.
    - **DNA Calculation**: Centralized `calculate_dna` method using frequency-weighted averages (Artist Play Count / Entry Count).
    - **Vector Extraction**: `extract_top_subgenres` generates a normalized, weighted subgenre vector (Top 25) for high-precision "Cultural Fit" matching.
2.  **`app.py`**: The CLI Interface.
    - Handles data ingestion, visual chart toggles (Scaling/Rounding), and system-wide recalculations.
3.  **`compare.py`**: The Hybrid Matching Engine.
    - Combines Subgenre similarity and DNA distance into a single unified score.
4.  **`radarchart.py`**: The "Artist Prism".
    - Renders dynamic Radarcharts/Starcharts with theme-aware coloring based on dominant traits.

---

## ✅ Recent Milestones & Fixes
- **Hybrid Matching System**: Moved from simple DNA distance to a 70/30 Hybrid Model ($70\% \text{ Subgenre Cosine Similarity} + 30\% \text{ DNA Euclidean Distance}$).
- **Frequency-Weighted Standardization**: Fixed consistency issues; User DNA and Festival DNA are now calculated using the exact same frequency-weighting logic, ensuring 100% Synergy Match for identical datasets.
- **Missing Bass Bug**: Resolved a major data omission where festival DNA was missing the `bass` component.
- **Interactive Visual Toggles**: Added front-end toggles for "Scaling" and "Rounding" in the Sonic DNA visualization menu.

---

## 📝 Ongoing Tasks & TODOs

- [ ] **Spotify Specific Track Data**: Use Spotify CSV's Danceability,Energy,Key,Loudness,Mode,Speechiness,Acousticness,Instrumentalness,Liveness,Valence,Tempo,Time Signature to create a more accurate "Sonic DNA".
- [ ] **Genre Taxonomy**: Use RYM's API to find the relationships (parent/child genres) and use that to create the new genre table in the database. We will do this by Pulling all Genres under EDM as well as their descriptions and filling the Genres Table in the DB.to be perfect so perfect my approach here:
    0) a DB genres table & a DB genre_relationships table with the schema
        genres: id, name, slug, aliases, description, sonic_dna
        genre_relationships: genre_id, parent_genre_id, influence_genre_id
    1) We call RYM's API to fill all EDM subgenres into the names column
    2) For each of those genres we call RYM to feed the long description into the Description col
    3) For each row with a description we call our LLM to process the data and come up with at least one direct parent genre and at most 2 parent genres. The LLM will also scan for at most 2 influences that are not the parent to fill the influences column with. BUT These parent/influence genres must already be in the database

- [ ] **Web Interface**: Transition from the CLI to a full React/Next.js frontend (planned).
    - [ ] **Landing Page**: Create a landing page for the website. DJWYA logo placed in the middle. Underneath the logo will be "EDM is for Everyone", but the "EDM" shifts to all the genres of music in the database. There Will be a button to login or signup.
    - [ ] **Login/Signup**: Make it so that after google SSO login, the user is prompted for a display name and a profile picture.
    - [ ] **User Profile**: Create a user profile page to display user information and preferences.
        - [ ] **Analytics**: Analytics will be displayed on the user page. At the forefront will be their Sonic DNA StarChart. Off to the side will be their top 25 artists and their top genres displayed in a sunburst chart with sections colored based on the bucket category of electronic music or even sonic DNA scores. One Idea is to have a multiple pie chart for each bucket category of electronic music.
    - [ ] **Genres Page**: Create a page to display all the genres of electronic music in the database. This page will be a force directed graph of all the genres of electronic music in the database.
    #MAYBE WILL ADD THIS LATER
    - [ ] **Festival Map**: Create a map of the world with nodes (Cities/towns with festivals) being Larger based on the number of festivals in that city. When Clicking on a city/town, it will display all the festivals cards in that city/town in a google maps sort of styling.
        - [ ] **Festival Card**: Create a festival card to display information about festivals. It will have the festival picture, name, date, location and user specific information like Hybrid Match Score and matching artists.
    
    - [ ] **Playlist Ingestion**: Create a playlist ingestion page for users to upload playlists.
    - [ ] **Festival Discovery**: Only after the user has created an account, logged in, and given some data, have a festival discovery page to display festivals that match user preferences.
    - [ ] **Artist Lookups**: Create an artist lookup page to display information about artists.
    - [ ] **Artist Pages**: Create an artist page to display information about artists, including their genres, festivals they are playing, and their sonic DNA StarChart.
- [ ] **Poster Scraping Automation**: Integrate EDMTRAIN API for with openclaw for automated festival discovery, and use openclaw to scrape festival posters for DJ names.
- [ ] **API Intergration**: Eventual Support of Spotify, Apple Music, Anghami, Tencent Music, Deezer, Soundcloud.
- [ ] **Artist Lookups**: Find an Where a specific Artist is playing.



---

## 💡 Key Logic Notes (The "God-Tier" Math)

### 1. Hybrid Scoring ($Final = 0.7 \times S_{score} + 0.3 \times A_{score}$)
- **$S_{score}$ (Cultural Fit)**: Cosine Similarity between the User's subgenre vector and a Festival's lineup vector. This prevents diverse tastes (e.g., Techno + Ambient) from cancelling each other out into a "boring middle."
- **$A_{score}$ (Vibe Fit)**: Exponential decay of Euclidean distance: $e^{-0.15 \times \text{distance}}$. This metrics the "Vibe" similarity across all 7 Sonic DNA axes.

### 2. Weighted DNA Methodology
DNA is calculated using a **Frequency-Weighted Average**. If an artist appears 10 times in a dataset, their DNA contributes 10x more weight than a one-off artist. This guarantees parity between an uploaded "Festival Playlist" and the festival's own aggregated DNA profile.

### 3. Subgenre "Top 25" Constraint
Only the top 20-25 subgenres by weight are stored in the `subgenres` JSONB column. This maintains a high "Signal-to-Noise" ratio and prevents obscure, irrelevant genres from diluting the match quality.
