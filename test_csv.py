import csv
import os

def check_unique_artists():
    """Reads a CSV from the liked_songs folder and counts unique artists."""
    
    # List available CSVs
    csv_dir = "liked_songs"
    if not os.path.exists(csv_dir):
        print(f"❌ Error: {csv_dir} folder not found.")
        return

    files = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]
    if not files:
        print(f"⚠️ No CSV files found in {csv_dir}.")
        return

    print("\n📂 Available CSV files:")
    for f in files:
        print(f"  - {f}")

    target = input("\nEnter the filename to check (e.g., liked_songs_complete): ").strip()
    if not target.endswith(".csv"):
        target += ".csv"

    filepath = os.path.join(csv_dir, target)
    if not os.path.exists(filepath):
        print(f"❌ Error: {filepath} not found.")
        return

    unique_artists = set()
    total_tracks = 0

    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                total_tracks += 1
                # Format is usually: "Artist 1; Artist 2"
                raw_artists = row.get("Artist Name(s)", "")
                if raw_artists:
                    # Split by semicolon and clean up
                    names = [n.strip() for n in raw_artists.split(";") if n.strip()]
                    for name in names:
                        unique_artists.add(name.lower()) # Case-insensitive uniqueness

        print("\n" + "="*30)
        print(f"📊 REPORT: {target}")
        print("="*30)
        print(f"📑 Total Tracks:    {total_tracks}")
        print(f"🎙️  Unique Artists: {len(unique_artists)}")
        print("="*30)

    except Exception as e:
        print(f"❌ Error reading CSV: {e}")

if __name__ == "__main__":
    check_unique_artists()
