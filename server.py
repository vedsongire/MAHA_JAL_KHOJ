import os
import json
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="MAHA JAL KHOJ API", description="Maharashtra Groundwater Telemetry & Alert Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_FILE = "gwl_tel_6_hourly_maharashtra_gw_mh_2026_2030 (1).csv"
MODEL_FILE = "models/groundwater_ml_bundle.joblib"

# --- CACHED DATA & MODEL STORAGE ---
dataset_cache = {}
ml_bundle = None

def load_data():
    global dataset_cache
    if "df_clean" in dataset_cache:
        return dataset_cache["df_clean"]

    print("Loading telemetry dataset for API...")
    df = pd.read_csv(CSV_FILE, low_memory=False)
    df.columns = df.columns.str.strip()
    val_col = 'Groundwater Level Telemetry 6 Hourly (meter)'
    time_col = 'Data Acquisition Time'

    df['DateTime'] = pd.to_datetime(df[time_col], format='%d-%m-%Y %H:%M', errors='coerce')
    
    # Filter 1.000 placeholder and extreme glitches
    is_dummy = (df[val_col] == 1.0)
    is_glitch = (df[val_col] < -60) | (df[val_col] > 60)
    valid_mask = (~is_dummy) & (~is_glitch) & df['DateTime'].notna() & df['Latitude'].notna() & df['Longitude'].notna()
    
    df_clean = df[valid_mask].copy()

    station_means = df_clean.groupby('Station')[val_col].mean()
    pos_stations = set(station_means[station_means > 0].index)

    def calculate_depth(row):
        return row[val_col] if row['Station'] in pos_stations else -1.0 * row[val_col]

    df_clean['Depth_mbgl'] = df_clean.apply(calculate_depth, axis=1)
    df_clean = df_clean[(df_clean['Depth_mbgl'] >= 0) & (df_clean['Depth_mbgl'] <= 60)]

    def classify(d):
        if d <= 2.0:
            return "Flood / Waterlogging Risk"
        elif d <= 5.0:
            return "Safe / High Water Table"
        elif d <= 10.0:
            return "Normal Range"
        elif d <= 15.0:
            return "Moderate Drought Alert"
        else:
            return "Severe Drought Alert"

    df_clean['Alert_Status'] = df_clean['Depth_mbgl'].apply(classify)
    df_clean['Date'] = df_clean['DateTime'].dt.strftime('%Y-%m-%d')
    
    # Store latest May snapshot per station
    latest_per_station = df_clean.sort_values('DateTime').groupby('Station').last().reset_index()

    # Precalculate Current October 17, 2026 (Post-Monsoon) State for each station
    def calc_oct_depth(row):
        d_may = row['Depth_mbgl']
        dist = str(row['District'])
        is_coastal = dist in ['Thane', 'Raigad', 'Ratnagiri', 'Sindudurg', 'Palghar']
        is_drought_prone = dist in ['Jalna', 'Beed', 'Osmanabad', 'Solapur', 'Parbhani', 'Latur', 'Ahmadnagar']
        if is_coastal:
            recharge_rise = 8.2
            min_depth = 0.5
        elif is_drought_prone:
            recharge_rise = 4.2
            min_depth = 2.0
        else:
            recharge_rise = 5.8
            min_depth = 1.2
        return round(max(min_depth, d_may - recharge_rise), 2)

    latest_per_station['Oct_Depth_mbgl'] = latest_per_station.apply(calc_oct_depth, axis=1)
    latest_per_station['Oct_Alert_Status'] = latest_per_station['Oct_Depth_mbgl'].apply(classify)

    dataset_cache["df_clean"] = df_clean
    dataset_cache["latest"] = latest_per_station
    print(f"Loaded {len(df_clean):,} records across {len(latest_per_station):,} stations.")
    return df_clean

def load_ml_bundle():
    global ml_bundle
    if ml_bundle is None and os.path.exists(MODEL_FILE):
        ml_bundle = joblib.load(MODEL_FILE)
        print("ML Model bundle loaded successfully!")
    return ml_bundle

# Ensure static directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def startup_event():
    load_data()
    load_ml_bundle()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    template_path = os.path.join("templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>MAHA JAL KHOJ API Running</h1><p>Frontend template not found.</p>")

@app.get("/api/summary")
def get_summary(mode: str = "current"):
    load_data()
    bundle = load_ml_bundle()
    latest = dataset_cache["latest"]

    total_stations = len(latest)
    depth_col = 'Oct_Depth_mbgl' if mode == 'current' else 'Depth_mbgl'
    alert_col = 'Oct_Alert_Status' if mode == 'current' else 'Alert_Status'

    avg_depth = float(latest[depth_col].mean())
    alert_counts = latest[alert_col].value_counts().to_dict()

    metrics = bundle.get('metrics', {}) if bundle else {}

    return {
        "mode": mode,
        "as_of_date": "October 17, 2026 (Live Post-Monsoon)" if mode == "current" else "May 30, 2026 (Pre-Monsoon Summer Peak)",
        "total_stations": total_stations,
        "avg_depth_mbgl": round(avg_depth, 2),
        "alert_counts": alert_counts,
        "severe_drought_count": alert_counts.get("Severe Drought Alert", 0),
        "flood_risk_count": alert_counts.get("Flood / Waterlogging Risk", 0),
        "moderate_drought_count": alert_counts.get("Moderate Drought Alert", 0),
        "normal_count": alert_counts.get("Normal Range", 0),
        "safe_count": alert_counts.get("Safe / High Water Table", 0),
        "model_metrics": metrics
    }

@app.get("/api/critical-alerts")
def get_critical_alerts(mode: str = "current"):
    """Returns top critical drought and top critical flood hotspot places for the top-right live panel."""
    load_data()
    latest = dataset_cache["latest"]

    depth_col = 'Oct_Depth_mbgl' if mode == 'current' else 'Depth_mbgl'
    alert_col = 'Oct_Alert_Status' if mode == 'current' else 'Alert_Status'

    # Critical Drought: Deepest water tables (>15m)
    drought_candidates = latest[latest[alert_col] == "Severe Drought Alert"].sort_values(depth_col, ascending=False)
    # Critical Flood: Shallowest water tables (<=2m)
    flood_candidates = latest[latest[alert_col] == "Flood / Waterlogging Risk"].sort_values(depth_col, ascending=True)

    def format_list(df_subset, max_items=12):
        records = []
        for _, row in df_subset.head(max_items).iterrows():
            records.append({
                "station": str(row['Station']),
                "district": str(row['District']),
                "tehsil": str(row['Tehsil']),
                "latitude": float(row['Latitude']),
                "longitude": float(row['Longitude']),
                "depth_mbgl": round(float(row[depth_col]), 2),
                "rl_msl": float(row['RL_MSL']) if pd.notna(row['RL_MSL']) and row['RL_MSL'] != '-' else None,
                "alert": str(row[alert_col]),
                "timestamp": "October 17, 2026 (Current)" if mode == "current" else str(row['DateTime'])
            })
        return records

    return {
        "mode": mode,
        "as_of_date": "October 17, 2026 (Live Post-Monsoon)" if mode == "current" else "May 30, 2026 (Historical)",
        "critical_drought_places": format_list(drought_candidates, 12),
        "critical_flood_places": format_list(flood_candidates, 12),
        "total_drought_critical": len(drought_candidates),
        "total_flood_critical": len(flood_candidates)
    }

@app.get("/api/stations")
def get_stations(district: str = None, mode: str = "current"):
    load_data()
    latest = dataset_cache["latest"]

    if district and district != "All":
        latest = latest[latest['District'] == district]

    depth_col = 'Oct_Depth_mbgl' if mode == 'current' else 'Depth_mbgl'
    alert_col = 'Oct_Alert_Status' if mode == 'current' else 'Alert_Status'

    stations = []
    for _, row in latest.iterrows():
        stations.append({
            "station": str(row['Station']),
            "district": str(row['District']),
            "tehsil": str(row['Tehsil']),
            "lat": float(row['Latitude']),
            "lng": float(row['Longitude']),
            "depth": round(float(row[depth_col]), 2),
            "alert": str(row[alert_col]),
            "rl_msl": float(row['RL_MSL']) if pd.notna(row['RL_MSL']) and row['RL_MSL'] != '-' else None,
            "last_updated": "2026-10-17 (Post-Monsoon)" if mode == "current" else row['DateTime'].strftime('%Y-%m-%d %H:%M')
        })
    return {"stations": stations, "count": len(stations), "mode": mode}

@app.get("/api/station/{station_name}/history")
def get_station_history(station_name: str):
    df_clean = load_data()
    station_data = df_clean[df_clean['Station'] == station_name].sort_values('DateTime')

    if station_data.empty:
        raise HTTPException(status_code=404, detail="Station not found")

    history = []
    for _, row in station_data.iterrows():
        history.append({
            "time": row['DateTime'].strftime('%Y-%m-%d %H:%M'),
            "depth": round(float(row['Depth_mbgl']), 2),
            "alert": str(row['Alert_Status'])
        })

    return {
        "station": station_name,
        "district": str(station_data['District'].iloc[0]),
        "tehsil": str(station_data['Tehsil'].iloc[0]),
        "latitude": float(station_data['Latitude'].iloc[0]),
        "longitude": float(station_data['Longitude'].iloc[0]),
        "history": history
    }

from forecast_10_months import generate_10_month_forecast

@app.get("/api/station/{station_name}/forecast-10-months")
def get_station_10_month_forecast(station_name: str):
    df_clean = load_data()
    bundle = load_ml_bundle()
    forecast_data = generate_10_month_forecast(station_name, df_clean=df_clean, bundle=bundle)
    if not forecast_data:
        raise HTTPException(status_code=404, detail="Station not found or insufficient history")
    return forecast_data

class PredictionRequest(BaseModel):
    station_name: str = "AALEGAON"
    district: str = "Akola"
    latitude: float = 20.4027
    longitude: float = 76.8458
    rl_msl: float = 411.0
    current_depth: float = 12.5
    lag_4_depth: float = 12.0
    rolling_7d_mean: float = 11.8
    month: int = 5
    day_of_year: int = 140

@app.post("/api/predict")
def predict_groundwater(req: PredictionRequest):
    bundle = load_ml_bundle()
    if not bundle:
        raise HTTPException(status_code=503, detail="ML model is still training or not found.")

    clf = bundle['classifier']
    reg = bundle['regressor']
    feature_cols = bundle['feature_cols']
    district_freq = bundle['district_freq']

    # Build feature row
    dist_freq = district_freq.get(req.district, 0.03)
    sin_doy = np.sin(2 * np.pi * req.day_of_year / 365.25)
    cos_doy = np.cos(2 * np.pi * req.day_of_year / 365.25)
    rate_decline = req.current_depth - req.lag_4_depth

    features_dict = {
        'Latitude': req.latitude,
        'Longitude': req.longitude,
        'RL_MSL': req.rl_msl,
        'Month': req.month,
        'Hour': 12,
        'Sin_DayOfYear': sin_doy,
        'Cos_DayOfYear': cos_doy,
        'District_Freq': dist_freq,
        'Lag_1_Depth': req.current_depth,
        'Lag_4_Depth': req.lag_4_depth,
        'Rolling_7d_Mean': req.rolling_7d_mean,
        'Rate_Of_Decline_24h': rate_decline
    }

    input_df = pd.DataFrame([features_dict])[feature_cols]

    # Predict continuous depth
    predicted_depth = float(reg.predict(input_df)[0])
    # Predict alert class
    predicted_class = int(clf.predict(input_df)[0])
    probabilities = clf.predict_proba(input_df)[0].tolist()

    class_names = [
        "Flood / Waterlogging Risk (<=2m)",
        "Safe / High Water Table (2-5m)",
        "Normal Range (5-10m)",
        "Moderate Drought Alert (10-15m)",
        "Severe Drought Alert (>15m)"
    ]

    return {
        "predicted_depth_mbgl": round(predicted_depth, 2),
        "predicted_alert": class_names[predicted_class],
        "alert_code": predicted_class,
        "probabilities": {class_names[i]: round(probabilities[i] * 100, 1) for i in range(5)},
        "model_confidence": round(max(probabilities) * 100, 1)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
