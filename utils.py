import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# 📂 Historical Data Loader
def load_historical_data():
    return pd.read_csv("../simulator/historical_drone_data.csv")

# ✅ Live Drone Data Reader (with fallback for missing columns)
def get_live_drone_data():
    df = pd.read_csv("../simulator/live_drone_data.csv")

    # Add missing columns if not present
    if "public_key" not in df.columns:
        df["public_key"] = "NA"
    if "role" not in df.columns:
        df["role"] = "UNKNOWN"

    df["public_key"] = df["public_key"].astype(str)
    df["role"] = df["role"].astype(str)
    return df

# 🧠 AI Path Prediction + Risk Scoring
def predict_paths(df):
    predictions = []

    for _, drone in df.iterrows():
        # Simulate time steps
        time_steps = np.array([0, 1, 2, 3, 4]).reshape(-1, 1)

        # Simulate lat/lon drift based on speed
        lat_series = drone["lat"] + 0.0001 * drone["speed"] * time_steps.flatten()
        lon_series = drone["lon"] + 0.0001 * drone["speed"] * time_steps.flatten()

        # Fit regression models
        lat_model = LinearRegression().fit(time_steps, lat_series)
        lon_model = LinearRegression().fit(time_steps, lon_series)

        # Predict next position (t = 5)
        next_lat = lat_model.predict([[5]])[0]
        next_lon = lon_model.predict([[5]])[0]

        # Risk score based on speed and altitude
        risk_score = round((drone["speed"] / 100) + (drone["altitude"] / 1000), 2)

        predictions.append({
            "drone_id": drone["drone_id"],
            "current_lat": round(drone["lat"], 5),
            "current_lon": round(drone["lon"], 5),
            "predicted_lat": round(next_lat, 5),
            "predicted_lon": round(next_lon, 5),
            "risk_score": risk_score
        })

    return pd.DataFrame(predictions)

# ⚠️ Anomaly Detection Logic
def detect_anomalies(df):
    anomalies = df[
        (df["status"] == "CRITICAL") |
        (df["speed"] > 120) |
        (df["altitude"] < 100)
    ]
    return anomalies.reset_index(drop=True)