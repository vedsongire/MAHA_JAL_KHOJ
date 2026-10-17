import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(BASE_DIR, "models", "groundwater_ml_bundle.joblib")
CSV_FILE = os.path.join(BASE_DIR, "gwl_tel_6_hourly_maharashtra_gw_mh_2026_2030 (1).csv")

def generate_10_month_forecast(station_name, df_clean=None, bundle=None):
    """
    Generates a 10-month (300-day) forward projection from the latest observation (May 30, 2026)
    up to March 31, 2027, incorporating regional Maharashtra seasonal monsoon recharge
    and post-monsoon depletion dynamics.
    """
    if bundle is None:
        bundle = joblib.load(MODEL_FILE)
    
    if df_clean is None:
        df = pd.read_csv(CSV_FILE, low_memory=False)
        df.columns = df.columns.str.strip()
        val_col = 'Groundwater Level Telemetry 6 Hourly (meter)'
        time_col = 'Data Acquisition Time'
        df['DateTime'] = pd.to_datetime(df[time_col], format='%d-%m-%Y %H:%M', errors='coerce')
        valid = (df[val_col] != 1.0) & (df[val_col] >= -60) & (df[val_col] <= 60) & df['DateTime'].notna()
        df_clean = df[valid].copy()
        station_means = df_clean.groupby('Station')[val_col].mean()
        pos_stations = set(station_means[station_means > 0].index)
        df_clean['Depth_mbgl'] = df_clean.apply(lambda r: r[val_col] if r['Station'] in pos_stations else -1.0 * r[val_col], axis=1)
        df_clean = df_clean[(df_clean['Depth_mbgl'] >= 0) & (df_clean['Depth_mbgl'] <= 60)]

    station_history = df_clean[df_clean['Station'] == station_name].sort_values('DateTime')
    if station_history.empty:
        return None

    last_record = station_history.iloc[-1]
    last_date = last_record['DateTime'] # Around May 30, 2026
    start_depth = float(last_record['Depth_mbgl'])
    district = str(last_record['District'])
    lat = float(last_record['Latitude'])
    lng = float(last_record['Longitude'])
    rl = float(last_record['RL_MSL']) if pd.notna(last_record['RL_MSL']) and last_record['RL_MSL'] != '-' else 350.0

    # Regional Monsoon Recharge Profile for Maharashtra (CGWB standard):
    # Coastal Konkan gets ~2500-3000mm rain (massive water rise, risk of flood)
    # Marathwada/Vidarbha gets ~600-900mm rain (moderate recharge)
    # Western Ghats plateau gets ~700-1000mm
    is_coastal = district in ['Thane', 'Raigad', 'Ratnagiri', 'Sindudurg', 'Palghar']
    is_drought_prone = district in ['Jalna', 'Beed', 'Osmanabad', 'Solapur', 'Parbhani', 'Latur', 'Ahmednagar']
    
    # Maximum seasonal recharge water level rise (meters)
    max_recharge_rise = 8.0 if is_coastal else 5.5 if not is_drought_prone else 4.0

    projections = []
    current_depth = start_depth
    current_date = last_date

    # Project forward week by week for 42 weeks (~10 months: June 2026 to March 2027)
    for week in range(1, 44):
        future_date = last_date + timedelta(weeks=week)
        m = future_date.month
        doy = future_date.timetuple().tm_yday

        # Hydrological seasonal shift per week:
        # June - Sept (Monsoon): Water table RISES (Depth decreases)
        if m in [6, 7]: # Early monsoon onset & heavy downpours
            weekly_delta = -0.65 * (1.3 if is_coastal else 1.0)
        elif m in [8, 9]: # Peak saturation / peak water table
            weekly_delta = -0.35
        # October - November (Post-Monsoon stabilization):
        elif m in [10, 11]:
            weekly_delta = +0.10 # Slight extraction starts
        # December - February (Rabi agricultural season drawdown):
        elif m in [12, 1, 2]:
            weekly_delta = +0.35 * (1.2 if is_drought_prone else 1.0)
        # March (Summer peak onset):
        else:
            weekly_delta = +0.55

        # Update recursive depth with natural bounds
        current_depth = current_depth + weekly_delta
        min_depth_limit = 0.8 if is_coastal else 1.8 # Groundwater rarely rises above 1-2m bgl without ponding
        max_depth_limit = 45.0
        current_depth = max(min_depth_limit, min(max_depth_limit, current_depth))

        # Alert classification
        if current_depth <= 2.0:
            status = "Flood / Waterlogging Risk"
            alert_code = 0
        elif current_depth <= 5.0:
            status = "Safe / High Water Table"
            alert_code = 1
        elif current_depth <= 10.0:
            status = "Normal Range"
            alert_code = 2
        elif current_depth <= 15.0:
            status = "Moderate Drought Alert"
            alert_code = 3
        else:
            status = "Severe Drought Alert"
            alert_code = 4

        projections.append({
            "date": future_date.strftime('%Y-%m-%d'),
            "month_name": future_date.strftime('%B %Y'),
            "predicted_depth": round(current_depth, 2),
            "alert_status": status,
            "alert_code": alert_code,
            "season_phase": "Monsoon Recharge" if m in [6,7,8,9] else "Post-Monsoon Peak" if m in [10,11] else "Rabi Depletion" if m in [12,1,2] else "Summer Drought Onset"
        })

    return {
        "station": station_name,
        "district": district,
        "last_observed_date": last_date.strftime('%Y-%m-%d'),
        "last_observed_depth": round(start_depth, 2),
        "forecast_horizon": "10 Months (June 2026 - March 2027)",
        "projections": projections
    }

if __name__ == "__main__":
    res = generate_10_month_forecast("AALEGAON")
    print(f"Station: {res['station']} ({res['district']})")
    print(f"Last Observed Depth: {res['last_observed_depth']} mbgl on {res['last_observed_date']}")
    print("\nSample 10-Month Projections:")
    for p in res['projections'][::4]: # Every 4 weeks
        print(f"[{p['date']}] ({p['season_phase']}): {p['predicted_depth']} mbgl -> {p['alert_status']}")
