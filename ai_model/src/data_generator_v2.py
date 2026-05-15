import csv
import random
from datetime import datetime, timedelta

def generate_fluid_dataset(filename="esp32_sensor_dataset.csv", num_rows=1500):
    start_time = datetime.now()
    
    base_flow = 500.0
    base_temp = 25.0
    base_pressure = 10.0
    base_gas = 5.0 # MQ6 baseline
    
    base_lat = 28.6139 
    base_lon = 77.2090
    
    dataset = []
    
    for i in range(num_rows):
        current_time = start_time + timedelta(seconds=i)
        
        leak_status = 0
        flow_1_drop = 0
        flow_2_drop = 0
        temp_increase = 0
        pressure_drop = 0
        gas_increase = 0
        
        lat = base_lat + (i * 0.000005)
        lon = base_lon + (i * 0.000005)
        
        if 300 <= i < 500:
            # Gradual leak
            leak_status = 1
            progress = (i - 300) / 200.0
            flow_2_drop = 120 * progress 
            flow_1_drop = 15 * progress
            temp_increase = 6 * progress
            pressure_drop = 3 * progress
            gas_increase = 150 * progress # Gas accumulating
            
        elif 800 <= i < 950:
            # Sudden burst leak
            leak_status = 1
            flow_2_drop = 180 + random.uniform(-10, 10)
            flow_1_drop = 30 + random.uniform(-5, 5)
            temp_increase = 8
            pressure_drop = 4.5
            gas_increase = 400 + random.uniform(-20, 20)
        
        noise_f1 = random.uniform(-10, 10)
        noise_f2 = random.uniform(-10, 10)
        noise_t = random.uniform(-0.5, 0.5)
        noise_p = random.uniform(-0.1, 0.1)
        noise_g = random.uniform(-1, 1)
        
        fs1 = base_flow - flow_1_drop + noise_f1
        fs2 = base_flow - flow_2_drop + noise_f2
        calc_flow_rate = (fs1 + fs2) / 2.0
        
        temp = base_temp + temp_increase + noise_t
        pressure = base_pressure - pressure_drop + noise_p
        gas = base_gas + gas_increase + noise_g
        
        dataset.append({
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "Latitude": round(lat, 6),
            "Longitude": round(lon, 6),
            "Flow_Sensor_1_Lmin": round(fs1, 2),
            "Flow_Sensor_2_Lmin": round(fs2, 2),
            "Flow_Rate": round(calc_flow_rate, 2),
            "Temperature_C": round(temp, 2),
            "Pressure_bar": round(pressure, 2),
            "Gas_Sensor_MQ6_ppm": round(gas, 2),
            "Leak_Status": leak_status
        })
        
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(dataset[0].keys()))
        writer.writeheader()
        writer.writerows(dataset)
    print(f"Dataset generated at {filename}")

if __name__ == '__main__':
    generate_fluid_dataset()
