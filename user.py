import os
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Use Service Key for maximum permissions
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(url, key)

def interactive_user_sync():
    print(f"--- DJWYA User Population Tool ---")
    print(f"Connected to: {url}")
    print("Type 'exit' or 'q' at any time to quit.\n")

    while True:
        username = input("Enter Username: ").strip()
        if username.lower() in ['exit', 'q']: break
        if not username: continue

        email = input("Enter Email: ").strip()
        if email.lower() in ['exit', 'q']: break
        if not email: continue

        # Prepare User Data
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": username,
            "email": email,
            "sonic_dna": {"intensity": 0, "euphoria": 0, "space": 0, "pulse": 0, "chaos": 0, "swing": 0}
        }

        try:
            print(f"Attempting to add user '{username}'...")
            # We use insert() here to specifically trigger conflicts if username/email are unique
            response = supabase.table("public.users").insert(user_data).execute()
            
            if response.data:
                print(f"✅ SUCCESS: Created user {username} ({user_id})")
            else:
                print("⚠️ Something went wrong? No data returned.")

        except Exception as e:
            print(f"❌ ERROR: Could not create user.")
            print(f"Details: {e}")
            print("Try a different username or email.\n")
            continue

        print("-" * 30)

if __name__ == "__main__":
    interactive_user_sync()