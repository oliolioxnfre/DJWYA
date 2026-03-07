import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

import os
import sys

# Get the absolute path to the DJWYA root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)

# Add the root directory to sys.path
sys.path.append(root_dir)

from artists_categorize import bulk_categorize_artists, sync_artists_to_supabase
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow CORS so the Next.js app can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class ArtistRequest(BaseModel):
    name: str
    fallback_genres: List[str] = []
    count: int = 1

class IngestRequest(BaseModel):
    user_id: str
    artists: List[ArtistRequest]
    filter_electronic: bool = False

@app.post("/api/ingest")
async def ingest_music_data(payload: IngestRequest):
    try:
        if not payload.artists:
            return {"status": "success", "message": "No artists provided."}

        # Format for bulk_categorize_artists: (name, fallback_genres, filter_electronic)
        artist_tuples = [
            (artist.name, artist.fallback_genres, payload.filter_electronic)
            for artist in payload.artists
        ]

        print(f"📥 Received ingest request for user {payload.user_id} with {len(artist_tuples)} artists.")
        print(f"🧵 Fetching genres and categorizing...")
        
        # 1. Process Artists
        bulk_results = bulk_categorize_artists(artist_tuples, supabase)

        # 2. Add counts back into the categorized data
        final_artists = {}
        for artist_req in payload.artists:
            orig_name = artist_req.name
            if orig_name in bulk_results:
                categorized = bulk_results[orig_name]
                categorized["count"] = artist_req.count
                final_artists[orig_name] = categorized

        print(f"✅ Categorized {len(final_artists)} electronic artists. Syncing to Supabase...")

        # 3. Sync to Supabase
        sync_artists_to_supabase(final_artists, supabase, user_id=payload.user_id)

        return {"status": "success", "message": f"Successfully processed {len(final_artists)} artists.", "processed_count": len(final_artists)}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Typically run with: uvicorn web.api.ingest:app --reload
    uvicorn.run(app, host="0.0.0.1", port=8000)
