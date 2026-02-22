import csv

def read_and_print_genres(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            print(f"{'Artist Name(s)':<40} | {'Song Name':<40} | {'Genres'}")
            print("-" * 100)
            
            for row in reader:
                artist_names = row.get("Artist Name(s)", "Unknown")
                track_name = row.get("Track Name", "Unknown")
                genres = row.get("Genres", "None")
                
                print(f"{artist_names:<40} | {track_name:<40} | {genres}")
                
    except FileNotFoundError:
        print(f"Could not find the file: {file_path}")

if __name__ == "__main__":
    csv_path = "liked_songs/quarter_songs.csv"
    read_and_print_genres(csv_path)
