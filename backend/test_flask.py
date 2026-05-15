import requests
import time
import random

# Configuration
# Change this to 'http://YOUR_LAPTOP_IP:5000/data' if testing across devices
SERVER_URL = "http://127.0.0.1:5001/data"

def send_reading(flow, pressure, temp, gas, label):
    """Sends a single fake sensor reading to the Flask backend."""
    payload = {
        "flow_rate": flow,
        "pressure": pressure,
        "temperature": temp,
        "gas": gas,
        "label": label
    }
    
    try:
        response = requests.post(SERVER_URL, json=payload)
        if response.status_code == 200:
            print(f"✅ Success | Label: {label.upper()} | Status: {response.json().get('status')}")
        else:
            print(f"❌ Failed  | Status Code: {response.status_code} | Msg: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def run_test():
    """Generates 20 test readings to populate the CSV and verify the server logic."""
    print("🚀 Starting Flask System Validation Test...")
    print(f"Targeting Server: {SERVER_URL}\n")

    # 1. Send 15 Normal Readings
    print("--- Phase 1: Sending Normal Operations (15 readings) ---")
    for i in range(15):
        send_reading(
            flow=round(random.uniform(95.0, 105.0), 2),
            pressure=round(random.uniform(2.3, 2.5), 2),
            temp=round(random.uniform(24.0, 26.0), 2),
            gas=random.randint(100, 200),
            label="normal"
        )
        time.sleep(0.1) # Small delay

    # 2. Send 5 Leak Readings
    print("\n--- Phase 2: Sending Leak Anomalies (5 readings) ---")
    for i in range(5):
        send_reading(
            flow=round(random.uniform(50.0, 65.0), 2),
            pressure=round(random.uniform(1.5, 1.8), 2),
            temp=round(random.uniform(25.0, 27.0), 2),
            gas=random.randint(500, 700),
            label="leak"
        )
        time.sleep(0.1)

    print("\n✨ Test Complete! Check your 'sensor_data.csv' file or visit http://127.0.0.1:5000/stats")

if __name__ == "__main__":
    run_test()
