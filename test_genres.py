import pylast
import os
from dotenv import load_dotenv

load_dotenv()
network = pylast.LastFMNetwork(api_key=os.environ.get("LASTFM_API_KEY"), api_secret=os.environ.get("LASTFM_API_SECRET"))

def print_artist(name):
    artist = network.get_artist(name)
    top_tags = artist.get_top_tags(limit=7)
    genres = [tag.item.get_name().lower() for tag in top_tags]
def print_artist(name):
    # Try with autocorrect
    try:
        artist = network.get_artist(name)
        # artist.autocorrect() might be a thing in pylast? Or maybe network.get_artist(name).get_correction()
        top_tags = artist.get_top_tags(limit=7)
        genres = [tag.item.get_name().lower() for tag in top_tags]
        print(f"Artist {name} top tags: {genres}")
    except Exception as e:
        print("Error getting artist:", e)
        
def print_track(artist, title):
    try:
        track = network.get_track(artist, title)
        top_tags = track.get_top_tags(limit=7)
        genres = [tag.item.get_name().lower() for tag in top_tags]
        print(f"Track {artist} - {title} top tags: {genres}")
    except Exception as e:
        print("Error getting track:", e)

print_artist("crayvxn")
print_artist("vjorka")
print_track("vjorka", "crystal clear")
print_track("crayvxn", "crystal clear")
