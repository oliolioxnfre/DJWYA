# 🧠 DJWYA Project Context & Memory Bank

## 📋 Handover Instructions
If you are switching accounts, please follow these steps to ensure I (in your new account) am fully caught up:
1.  **Open this file** (`gemini.md`) in the workspace.
2.  **Tell me:** *"Hey Gemini, I've switched accounts. Please read `gemini.md` to get the context of where we are in the DJWYA project."*
3.  I will then process this summary and we can continue exactly where we left off.

---

## 🚀 Project Overview: DJWYA
**DJWYA (Did J. Work Yet? / DJ Who You Are)** is a sophisticated music analysis tool that scours the internet for festivals featuring your favorite DJs based on your unique **Sonic DNA**.

### 🛠 Tech Stack
- **Backend:** Python
- **Database:** Supabase (PostgreSQL)
- **APIs:** Spotify (Spotipy), Last.fm (Pylast)
- **Visuals:** Matplotlib/Starchart for Radar Charts

---

## 🏗 Core Architecture
1.  **`classifier.py`**: The "Brain".
    - **`VibeClassifier`**: Maps music genres to a 7-axis sonic vector: `[Intensity, Euphoria, Space, Pulse, Chaos, Swing, Bass]`.
    - **DNA Calculation**: Computes weighted averages for both artists and users.
2.  **`app.py`**: The CLI Interface.
    - Handles playlist ingestion, system-wide recalculations, and the main user flow.
3.  **`compare.py`**: The Matching Engine.
    - Compares User DNA with Festival lineups to find the best matches.

---

## ✅ Recent Milestones & Fixes
- **Artist DNA Fix**: Resolved a database error in `recalculate_all_artist_dna` where the column name was incorrectly referenced as `all_genres` instead of `genres`.
- **Performance Optimization**: Implemented batch upserts for database updates to significantly speed up system-wide DNA recalculations.
- **Genre Expansion**: Continually refining the `BUCKET_MAP` and `SONIC_DNA` values in `classifier.py` for more accurate "vibes".

---

## 📝 Ongoing Tasks & TODOs
- [ ] **Genre Taxonomy**: Add ~40 more electronic subgenres to the classifier.
- [ ] **Multi-User Support**: Expand database logic to handle multiple users more efficiently.
- [ ] **Web Interface**: Transition from the CLI to a full React/Next.js frontend (planned).
- [ ] **API Automation**: Integrate EDMTRAIN API for automated festival discovery.

---

## 💡 Key Logic Notes
*The "Sonic DNA" is calculated using a weighted average. The primary genre has the most weight, decreasing as we move down the list of genres associated with an artist. This ensures that a "Techno" artist who occasionally makes "Ambient" tracks is still correctly weighted as Techno-forward.*
