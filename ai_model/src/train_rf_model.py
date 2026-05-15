import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import os

# 1. Load the ESP32 dataset
dataset_path = 'ai_model/data/raw/esp32_sensor_dataset.csv'
if not os.path.exists(dataset_path):
    print(f"Error: {dataset_path} not found. Please generate it first.")
    exit()

df = pd.read_csv(dataset_path)

# 2. Select Features for ML (excluding Location and Timestamp as they don't *cause* leaks)
# We train the model strictly on the sensor readings
features = ['Flow_Sensor_1_Lmin', 'Flow_Sensor_2_Lmin', 'Flow_Rate', 'Temperature_C', 'Pressure_bar', 'Gas_Sensor_MQ6_ppm']
X = df[features]
y = df['Leak_Status']

# 3. Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Initialize Random Forest Model
# We use max_depth=10 and n_estimators=50 to keep the model lightweight (< 1MB) for fast backend responses
model = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)

# 5. Train Model
print("Training Random Forest ML Model...")
model.fit(X_train, y_train)

# 6. Check Accuracy quickly
accuracy = model.score(X_test, y_test)
print(f"Model Training Complete! Accuracy on test set: {accuracy * 100:.2f}%")

# 7. Save Model as a Pickle (.pkl) file
model_filename = 'ai_model/models/leakage_ml_model.pkl'
with open(model_filename, 'wb') as f:
    pickle.dump(model, f)

print(f"Model successfully saved to {model_filename}. Ready for Backend!")
