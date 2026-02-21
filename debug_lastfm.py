import pylast

LASTFM_API_KEY = "278dd2789daa67c37bb1369fb6311bb2"
LASTFM_API_SECRET = "b63a70bf592daacaa90092b153ef6ca7" 

network = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET)

def debug_track(artist_name, song_name):
    print(f"--- Debugging: {artist_name} - {song_name} ---")
    try:
        track = network.get_track(artist_name, song_name)
        print(f"Track object: {track}")
        
        # Check for corrections (Last.fm might have a different canonical name)
        correction = track.get_correction()
        print(f"Correction: {correction}")
        
        top_tags = track.get_top_tags(limit=10)
        print(f"Top Tags count: {len(top_tags)}")
        for i, tag in enumerate(top_tags):
            print(f"  {i+1}. {tag.item.get_name()} (weight: {tag.weight})")
            
        # Try searching for the track
        print("\n--- Search Test ---")
        search = network.search_for_track(artist_name, song_name)
        results = search.get_next_page()
        if results:
            first_match = results[0]
            print(f"First search result: {first_match.get_artist().get_name()} - {first_match.get_title()}")
            search_tags = first_match.get_top_tags(limit=5)
            print(f"Search result tags count: {len(search_tags)}")
            for i, tag in enumerate(search_tags):
                print(f"  {i+1}. {tag.item.get_name()}")
            
    except Exception as e:
        print(f"Error: {e}")

debug_track("Skrillex", "Bangarang")
