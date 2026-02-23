import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

print(f"Connecting to {url}...")
try:
    supabase: Client = create_client(url, key)
    
    tables_to_probe = ["users", "user", "profiles", "accounts", "Users", "User", "user_lib", "artists"]
    
    for table in tables_to_probe:
        print(f"Probing '{table}' table...")
        try:
            res = supabase.table(table).select("*").limit(1).execute()
            print(f"  >>> SUCCESS: '{table}' table found!")
        except Exception as e:
            # Safely get the error message
            msg = str(e)
            if "Could not find the table" in msg:
                print(f"  - Not found.")
            else:
                print(f"  - Error: {msg.splitlines()[0]}")

except Exception as e:
    print(f"Connection failed: {e}")
