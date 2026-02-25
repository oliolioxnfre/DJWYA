import requests
import os
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get("EDMTRAIN_API_KEY")
def fetch_usa_festivals(api_key):
    url = "https://edmtrain.com/api/events"
    
    # These match the parameters in the documentation you pasted
    params = {
        "festivalInd": "true",        # Only get festivals
        "client": api_key             # Your API Key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Check for errors
        
        data = response.json()
        
        if data.get("success"):
            festivals = data.get("data", [])
            print(f"✅ Found {len(festivals)} upcoming festivals.")
            return festivals
        else:
            print(f"❌ API Error: {data.get('message')}")
            return []
            
    except Exception as e:
        print(f"⚠️ Request failed: {e}")
        return []

# Example Usage
MY_API_KEY = key
fest_list = fetch_usa_festivals(MY_API_KEY)

for f in fest_list[:30]: # Show first 5
    print(f"Name: {f['name']} | Date: {f['date']} | Location: {f['venue']['location']}")