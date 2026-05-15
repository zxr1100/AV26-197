from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# --- CORS Configuration ---
# Needed so that a React/HTML frontend running on a different port can call these APIs without security blocks.
CORS(app)

LEAK_STATE = False
STREAMING_STATE = True

@app.route('/api/set_leak', methods=['POST'])
def set_leak():
    global LEAK_STATE
    LEAK_STATE = True
    return jsonify({"status": "leak_triggered"})

@app.route('/api/reset_leak', methods=['POST'])
def reset_leak():
    global LEAK_STATE
    LEAK_STATE = False
    return jsonify({"status": "system_reset"})

@app.route('/api/set_streaming', methods=['POST'])
def set_streaming():
    global STREAMING_STATE
    data = request.get_json()
    STREAMING_STATE = data.get('active', True)
    return jsonify({"status": "streaming_updated", "active": STREAMING_STATE})

@app.route('/api/get_status', methods=['GET'])
def get_status():
    return jsonify({
        "leak": LEAK_STATE,
        "streaming": STREAMING_STATE
    })

@app.route('/api/get_leak', methods=['GET'])
def get_leak():
    return jsonify({"leak": LEAK_STATE})

CSV_FILE = 'sensor_data.csv'
HEADERS = ['timestamp', 'flow_rate', 'pressure', 'temperature', 'gas', 'label']

def initialize_csv():
    """Checks if the CSV file exists. If not, creates it with the correct headers."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
        print(f"Initialized new CSV file: {CSV_FILE}")

@app.route('/ping', methods=['GET'])
def ping():
    """Simple health check route to verify the Flask server is reachable."""
    return jsonify({"status": "Flask is running", "timestamp": datetime.now().isoformat()}), 200

@app.route('/data', methods=['POST'])
def receive_data():
    """
    Receives JSON data from the ESP32.
    Validates fields, saves to CSV, and prints to terminal.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # Validate required fields
        required = ['flow_rate', 'pressure', 'temperature', 'gas', 'label']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400

        # Prepare row with timestamp
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data['flow_rate'],
            data['pressure'],
            data['temperature'],
            data['gas'],
            data['label']
        ]

        # Append to CSV immediately
        # We use flush() to ensure data is physically written to the disk even if the server crashes.
        initialize_csv() # Ensure file exists if it was deleted while running
        with open(CSV_FILE, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
            f.flush() 

        # Print to terminal for real-time monitoring
        status_color = "\033[91m[LEAK]\033[0m" if data['label'] == 'leak' else "\033[92m[NORM]\033[0m"
        print(f"{status_color} Flow: {data['flow_rate']} | Pres: {data['pressure']} | Gas: {data['gas']}")

        return jsonify({"status": "saved", "message": "Data appended to CSV"}), 200

    except Exception as e:
        print(f"Error processing data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/view', methods=['GET'])
def view_all():
    """Reads the entire CSV file and returns it as a JSON array for the browser."""
    if not os.path.exists(CSV_FILE):
        return jsonify([])
    df = pd.read_csv(CSV_FILE)
    return jsonify(df.to_dict(orient='records'))

@app.route('/latest', methods=['GET'])
def get_latest():
    """Returns the last 10 readings from the CSV for the real-time dashboard."""
    if not os.path.exists(CSV_FILE):
        return jsonify([])
    df = pd.read_csv(CSV_FILE)
    return jsonify(df.tail(10).to_dict(orient='records'))

@app.route('/stats', methods=['GET'])
def get_stats():
    """
    Calculates and returns system-wide statistics.
    Useful for showing 'Total Leaks' or 'Average Flow' on the UI.
    """
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "No data available"}), 404
    
    df = pd.read_csv(CSV_FILE)
    if df.empty:
        return jsonify({"error": "Dataset is empty"}), 404

    total_count = len(df)
    leak_count = len(df[df['label'] == 'leak'])
    normal_count = total_count - leak_count
    leak_percent = (leak_count / total_count) * 100

    stats = {
        "total_readings": total_count,
        "leak_count": leak_count,
        "normal_count": normal_count,
        "leak_percentage": round(leak_percent, 2),
        "avg_flow": round(df['flow_rate'].mean(), 2),
        "avg_pressure": round(df['pressure'].mean(), 2),
        "avg_temp": round(df['temperature'].mean(), 2),
        "avg_gas": round(df['gas'].mean(), 2)
    }
    return jsonify(stats)

@app.route('/api/data', methods=['GET'])
def get_latest_data():
    try:
        with open('sensor_data.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                return jsonify({"error": "No data yet"}), 404
            
            # Get header and last line
            header = lines[0].strip().split(',')
            last_line = lines[-1].strip().split(',')
            
            data = dict(zip(header, last_line))
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_data_history():
    try:
        with open('sensor_data.csv', 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                return jsonify([])
            
            header = lines[0].strip().split(',')
            # Get last 20 lines
            history = []
            for line in lines[-20:]:
                if line.strip() and not line.startswith('timestamp'):
                    vals = line.strip().split(',')
                    history.append(dict(zip(header, vals)))
            
            return jsonify(history[::-1]) # Newest first
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    initialize_csv()
    # Run on 0.0.0.0 so it is accessible from the ESP32 on the same network
    app.run(host='0.0.0.0', port=5001, debug=True)