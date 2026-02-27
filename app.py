from radarchart import starchart
from artists_categorize import bulk_categorize_artists, sync_artists_to_supabase
import csv
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from compare import run_matching_engine

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Global Supabase Client
supabase: Client = create_client(url, key)
resolved_user_id = None


def add_playlist(user_id):
    """Prompts for a CSV and processes it."""
    while True:
        file_input = input("\nEnter CSV filename from 'liked_songs' (e.g. Max_Songs) or 'b' to go back: ").strip()
        if file_input.lower() == 'b': return
        if not file_input: continue
        
        if not file_input.lower().endswith('.csv'):
            file_input += '.csv'
            
        target_csv_file = f"liked_songs/{file_input}"
        if not os.path.exists(target_csv_file):
            print(f"❌ Error: File '{target_csv_file}' not found.")
            continue
            
        print(f"📂 Analyzing {target_csv_file}...")
        break

    # Ask the user if they want to filter for electronic music only
    filter_input = input("🔍 Filter for electronic artists only? (y/n, default: y): ").strip().lower()
    filter_choice = filter_input != 'n' # Default to True unless 'n' is explicitly entered

    electronic_artists = {}
    artist_requests = []
    try:
        with open(target_csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                raw_artists = row.get("Artist Name(s)", "")
                csv_genres_raw = row.get("Genres", "")
                track_artists = [a.strip() for a in raw_artists.split(';') if a.strip()]
                
                csv_genres_list = []
                if csv_genres_raw:
                    csv_genres_list = [g.strip().lower().replace(" ", "-") for g in csv_genres_raw.split(',') if g.strip()]
                
                for artist_name in track_artists:
                    # Normalize for tracking to avoid duplicates with different casing
                    norm_name = artist_name.lower().strip()
                    if norm_name in electronic_artists:
                        electronic_artists[norm_name]["count"] += 1
                        continue
                    
                    electronic_artists[norm_name] = {"original_name": artist_name, "count": 1}
                    artist_requests.append((artist_name, csv_genres_list, filter_choice))

        if artist_requests:
            print(f"🧵 Fetching genres for {len(artist_requests)} unique artists concurrently...")
            bulk_results = bulk_categorize_artists(artist_requests, supabase)
            
            final_artists = {}
            for name, categorized in bulk_results.items():
                norm_name = name.lower().strip()
                if norm_name in electronic_artists:
                    categorized["count"] = electronic_artists[norm_name]["count"]
                    final_artists[name] = categorized

            sync_artists_to_supabase(final_artists, supabase, user_id=user_id)
    except Exception as e:
        print(f"❌ Critical Error during sync: {e}")

def reset_user_taste(user_id):
    answer = input("Are you sure you want to reset your taste? (y/n): ").strip().lower()
    if answer == "y":
        supabase.table("user_lib").delete().eq("user_id", user_id).execute()
        supabase.table("public.users").update({"sonic_dna": None}).eq("id", user_id).execute()
        print(f"🧹 Taste reset for user {user_id}")
    else:
        print("❌ Taste not reset")

def check_sonic_dna(user_id):
    """Fetches user DNA and triggers the radar chart."""
    from radarchart import fetch_user_dna, radarchart, starchart
    dna = fetch_user_dna(user_id)
    if dna:
        # Default visualization settings
        do_scale = True
        do_round = True
        
        while True:
            print("\n" + "="*40)
            print("      🧬 DJWYA SONIC DNA 🧬")
            print("="*40)
            print(f" Settings: Scale={'[ON]' if do_scale else 'OFF'}, Rounding={'[ON]' if do_round else 'OFF'}")
            print("-" * 40)
            print(" 1. View Radarchart")
            print(" 2. View Starchart")
            print("-" * 40)
            print(" 3. Toggle Scaling (Normalize peaks to 10)")
            print(" 4. Toggle Rounding (Snap to nearest 2)")
            print("-" * 40)
            print(" 0. Go Back")
            print("="*40)
            
            select = input("\nSelect tuning: ").strip()
            if select == "1":
                radarchart([{'name': 'My Profile', 'dna': dna, 'count': 1}], user_id, scale=do_scale, round_even=do_round)
            elif select == "2":
                starchart([{'name': 'My Profile', 'dna': dna, 'count': 1}], user_id, scale=do_scale, round_even=do_round)
            elif select == "3":
                do_scale = not do_scale
            elif select == "4":
                do_round = not do_round
            elif select == "0":
                break
            else:
                print("❌ Invalid option. Choose 0-4.")
    else:
        print("❌ No Sonic DNA found. Try adding a playlist first!")

def find_festivals(user_id):
    """Runs the matching engine and prints the top festival matches."""
    print("🎪 Analyzing festival lineups...")
    results = run_matching_engine(user_id)
    
    if not results:
        print("❌ No matches found or your library is empty. Please add a playlist first!")
        return
        
    print("\n--- 🎟️ YOUR TOP FESTIVAL MATCHES 🎟️ ---")
    for match in results:
        # Only show festivals where there is at least some match
        if match['total_match'] > 0:
            print(f"🔥 {match['festival']}")
            print(f"   Artist % Match:  {match['artist_perc']:.1f}%")
            print(f"   Artist Score:    {match['artist_score']:.2f}")
            print(f"   Synergy Match:   {match['synergy_match']:.2f}%")
            print(f"   Total Match:     {match['total_match']:.2f}")
            print(f"   Artist Overlap:  {', '.join(match['shared_artists'])} ({match['matched_count']}/{match['total_artists']})")
            print("-" * 40 + "\n")

def recalculate_system_dna(user_id):
    """Triggers a full system-wide DNA refresh for all artists and the current user."""
    from classifier import VibeClassifier
    print("\n" + "="*40)
    print("      🔄 SYSTEM MAINTENANCE 🔄")
    print("="*40)
    print("⚠️  This will recalculate DNA for EVERY artist in the database")
    print("based on your newest dramatic sonic mappings.")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm == 'y':
        # 1. Update all artists in the 'artists' table
        VibeClassifier.recalculate_all_artist_dna()
        # 2. Update the current user's aggregate DNA based on those new artist values
        VibeClassifier.update_user_dna(user_id)
        print("\n✅ System-wide DNA refresh complete!")
    else:
        print("❌ Operation cancelled.")

def show_menu():
    """Prints a premium styled menu."""
    print("\n" + "="*40)
    print("      🎧 DJWYA CONTROL CENTER 🎧")
    print("="*40)
    print(" 1. ➕ Add New Playlist (CSV Sync)")
    print(" 2. 🧹 Reset User Taste (Wipe Library & DNA)")
    print(" 3. 🎪 Find Festival Matches")
    print(" 4. 🧬 Check My Sonic DNA")
    print(" 5. 📊 View Favorite Genres (Coming Soon)")
    print(" 6. 🎙️ View Favorite Artists (Coming Soon)")
    print(" 7. 🔄 Recalculate System DNA (All Artists)")
    print("-" * 40)
    print(" 9. 🚪 Logout")
    print(" 0. 🏁 Exit")
    print("="*40)

def main_loop():
    """Main program execution loop."""
    print("\nWelcome to DJWYA - Don't Just Wear Your Artists.")
    
    while True:
        # Step 1: Login / Auth
        global resolved_user_id
        username = input("\n👤 Enter your DJWYA username or 'exit': ").strip()
        
        if username.lower() == 'exit':
            print("Goodbye! 👋")
            break
            
        if not username: continue
        
        response = supabase.table("public.users").select("id").eq("username", username).execute()
        if not response.data:
            print(f"❌ User '{username}' not found. Use user.py to create one.")
            continue
            
        resolved_user_id = response.data[0]['id']
        print(f"✅ Authenticated as: {username}")
        
        # Step 2: Command Loop
        while True:
            show_menu()
            choice = input("\n👉 Select an option: ").strip()
            
            match choice:
                case "1":
                    add_playlist(resolved_user_id)
                case "2":
                    reset_user_taste(resolved_user_id)
                case "3":
                    find_festivals(resolved_user_id)
                case "4":
                    check_sonic_dna(resolved_user_id)
                case "5" | "6":
                    print("🚧 Visual analytics are coming in the next update!")
                case "7":
                    recalculate_system_dna(resolved_user_id)
                    
                case "9":
                    print(f"Logging out {username}...")
                    break # Back to the username prompt
                case "0":
                    print("Exiting application...")
                    return # Exit everything
                case _:
                    print("❌ Invalid command. Please choose 0-9.")

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nForce exiting... Goodbye!")
