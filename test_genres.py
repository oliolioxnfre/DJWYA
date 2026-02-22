import pylast
import os
from dotenv import load_dotenv

load_dotenv()
network = pylast.LastFMNetwork(api_key=os.environ.get("LASTFM_API_KEY"), api_secret=os.environ.get("LASTFM_API_SECRET"))

def print_artist(name):
    artist = network.get_artist(name)
    top_tags = artist.get_top_tags(limit=7)
    genres = [tag.item.get_name().lower() for tag in top_tags]
    print(f"{name}: {genres}")

print_artist("Avenged Sevenfold")
print_artist("Title Fight")
