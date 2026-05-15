# 💧 AI-Driven Predictive Maintenance & Autonomous Fluid Leakage Mitigation

### **Project Name:** EcoMinds | *The Intelligent Pipeline Safeguard*

This project is a production-grade Industrial IoT (IIoT) ecosystem designed to detect, predict, and mitigate fluid leakages in real-time. By combining high-frequency hardware sensing with a dual-model AI architecture, it identifies micro-anomalies long before they become catastrophic failures.

---

## 🚀 System Implementation

The framework is built on a distributed **Edge-to-Cloud** architecture:

### **1. Hardware & Edge Layer**
*   **Microcontroller:** ESP32-C3 SuperMini (High-speed, low-power processing).
*   **Sensor Suite:** 
    *   **YF-S201 Flow Sensor:** Monitors throughput and volumetric consistency.
    *   **Pressure Transducer:** Detects internal pipe pressure drops (Hydraulic Gradient).
    *   **MQ-2 Gas Sensor:** Monitors for environmental gas traces (Chemical leak detection).
    *   **DHT-11/Thermistor:** Tracks thermal fluctuations indicative of mechanical stress.
*   **Firmware:** Written in C++ (Arduino Framework) with non-blocking polling and data serialization.

### **2. Telemetry & Middleware Layer**
*   **Data Pipeline:** A Python-based **Real-Time Streamer** manages the telemetry flow between hardware (simulated/real) and the database.
*   **Backend API:** Flask-based REST API handles cross-process communication, system state management (Normal/Leak), and historical data retrieval.
*   **Workflow Automation:** Integrated with **n8n** for autonomous alert routing (WhatsApp/Email) and emergency protocol triggers.

### **3. Visualization Layer**
*   **Live Historian:** An industrial-style table view for raw telemetry audit logs.
*   **Digital Twin Dashboard:** A 3D/2D visual representation of the physical pipeline with real-time fluid animations synced to the AI output.

---

## 🧠 Machine Learning Architecture

The "Intelligence" of EcoMinds relies on two distinct models working in tandem:

### **Model A: Random Forest (RF)**
*   **Role:** Static Snapshot Classifier.
*   **Purpose:** Instantaneous detection of "Out-of-Bounds" events. It looks at a single moment in time (Current Flow, Current Pressure) and decides if the system is currently in a failure state.
*   **Key Advantage:** extremely low latency and high accuracy for massive, sudden leaks.

### **Model B: LSTM (Long Short-Term Memory)**
*   **Role:** Sequential Trend Analyzer.
*   **Purpose:** This deep learning model analyzes a **10-second sliding window** of data. It doesn't just look at the *current* flow; it looks at the *rate of change*.
*   **Key Advantage:** Detecting "Micro-Leaks" or "Drift" where values are slowly declining over time—something traditional static thresholds always miss.

---

## 📁 Project Structure

```bash
├── ai_model/           # Model training scripts (LSTM/RF)
├── backend/            # Flask API & Telemetry endpoints
├── frontend/           # Dashboards & ML Explainer Simulations
├── hardware/           # ESP32 Firmware (C++) & Circuit schematics
├── simulation/         # Data streamers & historical generators
└── sensor_data.csv     # Central telemetry database
```

---

## 🛠️ Setup & Execution

1. **Start the Backend:**
   ```bash
   python3 backend/app.py
   ```
2. **Start the Data Streamer:**
   ```bash
   python3 simulation/real_time_streamer.py
   ```
3. **Open the Dashboards:**
   Open `frontend/simulations/physics_vs_ai.html` in any modern browser.

---

### **Vision**
*EcoMinds aims to reduce industrial water wastage and chemical contamination by 40% through early-stage AI intervention.*
