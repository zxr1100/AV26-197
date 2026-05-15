import requests
import time
import json
from datetime import datetime

# --- Thinger.io Configuration ---
USERNAME = "jwoejrj"
DEVICE_ID = "leak_detector"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJNeU1hY0JyaWRnZSIsInN2ciI6ImFwLXNvdXRoZWFzdC5hd3MudGhpbmdlci5pbyIsInVzciI6Imp3b2VqcmoifQ.qIstEtZaD3nF9xQMCrMBGhiGlHB1CGquOGfzRPiFxg4"

# --- Local Backend Configuration ---
LOCAL_API_URL = "http://127.0.0.1:5001/data"

def fetch_from_thinger(resource):
    """Fetches and handles both dict and raw-value responses from Thinger.io."""
    url = f"https://ap-southeast.aws.thinger.io/v2/users/{USERNAME}/devices/{DEVICE_ID}/{resource}"
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  [DEBUG] Raw Cloud Data for {resource}: {data}") 
            # Handle if response is {"out": 34} or just 34
            if isinstance(data, dict):
                return data.get("out", 0)
            return data # Return raw value if it's not a dict
        return 0
    except:
        return 0

def run_bridge():
    print(f"🚀 Robust Cloud Bridge Started! (Skipping 0 values)")
    
    while True:
        try:
            f1 = fetch_from_thinger("flow1")
            gas = fetch_from_thinger("gas")
            temp = fetch_from_thinger("temperature")
            
            # ANTI-SPAM: Only send if we have real data (non-zero)
            if f1 == 0 and gas == 0 and temp == 0:
                print("  [Idle] Hardware is either offline or sending 0s. Skipping CSV save.")
            else:
                label = "leak" if (f1 > 1 and gas > 30) else "normal"
                payload = {
                    "flow_rate": f1, "pressure": 2.5, "temperature": temp, 
                    "gas": gas, "label": label
                }
                requests.post(LOCAL_API_URL, json=payload)
                print(f"✅ Data Saved! Temp: {temp}C | Flow: {f1} | Gas: {gas}")

        except Exception as e:
            print(f"⚠ Error: {e}")

        time.sleep(5)

if __name__ == "__main__":
    run_bridge()
