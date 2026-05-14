import time
import random

class LeakSimulation:
    def __init__(self):
        self.running = False
        self.pressure = 101.3
        self.flow_rate = 5.4
        self.temp = 24.2
        self.leak_detected = False

    def start(self):
        self.running = True
        print("Starting Telemetry Simulation...")
        print("Nominal State: 101.3 kPa, 5.4 L/s")
        
        try:
            while self.running:
                # Random fluctuations
                self.pressure += random.uniform(-0.1, 0.1)
                self.flow_rate += random.uniform(-0.05, 0.05)
                
                if random.random() > 0.98 and not self.leak_detected:
                    self.trigger_leak()
                
                status = "NORMAL" if not self.leak_detected else "CRITICAL"
                print(f"[{status}] Pressure: {self.pressure:.2f} kPa | Flow: {self.flow_rate:.2f} L/s", end="\r")
                
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def trigger_leak(self):
        self.leak_detected = True
        print("\n[!] ANOMALY DETECTED: Sudden pressure drop at Sensor 06")
        self.pressure -= 15.0
        self.flow_rate += 2.0

    def stop(self):
        self.running = False
        print("\nSimulation Stopped.")

if __name__ == "__main__":
    sim = LeakSimulation()
    sim.start()
