import csv
import random
from datetime import datetime, timedelta

def generate_fluid_dataset(filename="ai_model/data/raw/fluid_leakage_dataset.csv", num_rows=1500):
    start_time = datetime.now()
    
    # Base normal conditions for an industrial pipeline
    base_flow = 500.0       # L/min
    base_temp = 25.0        # Celsius
    base_pressure = 10.0    # bar (typical industrial pressure)
    
    dataset = []
    
    for i in range(num_rows):
        current_time = start_time + timedelta(seconds=i)
        
        # Determine current phase (normal vs leak)
        leak_status = 0
        flow_1_drop = 0
        flow_2_drop = 0
        temp_increase = 0
        pressure_drop = 0
        
        # Phase 1: 0 - 300 normal
        # Phase 2: 300 - 500 gradual leak
        # Phase 3: 500 - 800 normal
        # Phase 4: 800 - 950 sudden leak
        # Phase 5: 950 - 1500 normal
        
        if 300 <= i < 500:
            # Gradual leak: starts small, grows over time
            leak_status = 1
            progress = (i - 300) / 200.0  # 0.0 to 1.0 linearly
            
            # flow_sensor_2 sees a drop because water escapes before reaching it
            flow_2_drop = 120 * progress 
            # maybe slight drop in upstream pressure/flow
            flow_1_drop = 15 * progress
            
            temp_increase = 6 * progress
            pressure_drop = 3 * progress
            
        elif 800 <= i < 950:
            # Sudden leak: sharp immediate drop
            leak_status = 1
            flow_2_drop = 180 + random.uniform(-10, 10)  # Sudden intense drop
            flow_1_drop = 30 + random.uniform(-5, 5)     # System compensates slightly
            temp_increase = 8
            pressure_drop = 4.5
        
        # Natural sensor noise
        noise_f1 = random.uniform(-15, 15) # +/- 3%
        noise_f2 = random.uniform(-15, 15) # +/- 3%
        noise_t = random.uniform(-0.8, 0.8)
        noise_p = random.uniform(-0.2, 0.2)
        
        fs1 = base_flow - flow_1_drop + noise_f1
        fs2 = base_flow - flow_2_drop + noise_f2
        
        # Usually, during a leak, some fluid doesn't reach the second sensor.
        # Average flow rate
        calc_flow_rate = (fs1 + fs2) / 2.0
        
        # Temperature & Pressure
        temp = base_temp + temp_increase + noise_t
        pressure = base_pressure - pressure_drop + noise_p
        
        # Ensure temperature stays within 20 to 40 per requirements
        temp = max(20.0, min(temp, 40.0))
        
        # Add to dataset
        dataset.append({
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Flow_Sensor_1 (L/min)": round(fs1, 2),
            "Flow_Sensor_2 (L/min)": round(fs2, 2),
            "Flow_Rate": round(calc_flow_rate, 2),
            "Temperature (C)": round(temp, 2),
            "Pressure (bar)": round(pressure, 2),
            "Leak_Status": leak_status
        })
        
    with open(filename, 'w', newline='') as f:
        # Define fieldnames
        writer = csv.DictWriter(f, fieldnames=[
            "Timestamp", 
            "Flow_Sensor_1 (L/min)", 
            "Flow_Sensor_2 (L/min)", 
            "Flow_Rate", 
            "Temperature (C)", 
            "Pressure (bar)", 
            "Leak_Status"
        ])
        writer.writeheader()
        writer.writerows(dataset)
        
    print(f"Successfully generated synthetic dataset with {num_rows} rows at '{filename}'.")

if __name__ == '__main__':
    generate_fluid_dataset()
