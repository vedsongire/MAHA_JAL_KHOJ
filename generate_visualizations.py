import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("visualizations", exist_ok=True)
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.sans-serif': 'Arial', 'font.size': 11})

CSV_FILE = "gwl_tel_6_hourly_maharashtra_gw_mh_2026_2030 (1).csv"
print("Loading data for visualization generation...")
df = pd.read_csv(CSV_FILE, low_memory=False)
df.columns = df.columns.str.strip()

time_col = 'Data Acquisition Time'
val_col = 'Groundwater Level Telemetry 6 Hourly (meter)'

df['DateTime'] = pd.to_datetime(df[time_col], format='%d-%m-%Y %H:%M', errors='coerce')

# --- DATA CLEANING PIPELINE ---
# 1. Filter out known telemetry dummy error codes (1.000000 exactly)
is_dummy = (df[val_col] == 1.0)

# 2. Filter out extreme sensor glitches (< -60m or > 60m)
raw_val = df[val_col]
is_glitch = (raw_val < -60) | (raw_val > 60)

# Valid data mask
valid_mask = (~is_dummy) & (~is_glitch) & df['DateTime'].notna()
df_clean = df[valid_mask].copy()

# Standardize Depth Below Ground Level (mbgl)
# For stations where depth was recorded negatively (85% of stations), multiply by -1.
# If a station is predominantly positive, treat as positive.
station_means = df_clean.groupby('Station')[val_col].mean()
pos_stations = set(station_means[station_means > 0].index)

def calculate_depth(row):
    st = row['Station']
    v = row[val_col]
    if st in pos_stations:
        return v
    else:
        return -1.0 * v

df_clean['Depth_mbgl'] = df_clean.apply(calculate_depth, axis=1)
# Keep only physically realistic unconfined/semi-confined aquifer depths (0 to 60m bgl)
df_clean = df_clean[(df_clean['Depth_mbgl'] >= 0) & (df_clean['Depth_mbgl'] <= 60)]

# Categorization function
def classify(d):
    if d <= 2.0:
        return "Flood / Waterlogging Risk (<=2m)"
    elif d <= 5.0:
        return "Safe / High Water Table (2-5m)"
    elif d <= 10.0:
        return "Normal Range (5-10m)"
    elif d <= 15.0:
        return "Moderate Drought Alert (10-15m)"
    else:
        return "Severe Drought Alert (>15m)"

df_clean['Alert'] = df_clean['Depth_mbgl'].apply(classify)

color_map = {
    "Flood / Waterlogging Risk (<=2m)": "#1E88E5",
    "Safe / High Water Table (2-5m)": "#00ACC1",
    "Normal Range (5-10m)": "#43A047",
    "Moderate Drought Alert (10-15m)": "#FB8C00",
    "Severe Drought Alert (>15m)": "#E53935"
}

print(f"Cleaned valid records: {len(df_clean):,} of {len(df):,}")

# --- CHART 1: Statewide Alert Distribution ---
print("Generating Chart 1: Statewide Alert Distribution...")
fig, ax = plt.subplots(figsize=(10, 6))
alert_counts = df_clean['Alert'].value_counts()
ordered_categories = [
    "Flood / Waterlogging Risk (<=2m)",
    "Safe / High Water Table (2-5m)",
    "Normal Range (5-10m)",
    "Moderate Drought Alert (10-15m)",
    "Severe Drought Alert (>15m)"
]
counts = [alert_counts.get(cat, 0) for cat in ordered_categories]
colors = [color_map[cat] for cat in ordered_categories]

bars = ax.barh(ordered_categories, counts, color=colors, edgecolor='black', alpha=0.85)
ax.set_title("Groundwater Status & Alert Distribution across Maharashtra (Jan-May 2026)", fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Number of 6-Hourly Telemetry Observations", fontsize=11)
ax.invert_yaxis()

total = sum(counts)
for bar in bars:
    w = bar.get_width()
    pct = (w / total) * 100
    ax.text(w + total * 0.01, bar.get_y() + bar.get_height()/2, f"{w:,.0f} ({pct:.1f}%)", va='center', fontweight='bold', fontsize=10)

ax.set_xlim(0, max(counts) * 1.25)
plt.tight_layout()
plt.savefig("visualizations/01_statewide_alert_distribution.png", dpi=200)
plt.close()

# --- CHART 2: Temporal Progression / Depletion Trend (Jan - May) ---
print("Generating Chart 2: Temporal Progression Trend...")
df_clean['Date'] = df_clean['DateTime'].dt.date
daily_trend = df_clean.groupby('Date')['Depth_mbgl'].agg(['mean', 'median', lambda x: np.percentile(x, 25), lambda x: np.percentile(x, 75)])
daily_trend.columns = ['mean', 'median', 'p25', 'p75']
daily_trend.index = pd.to_datetime(daily_trend.index)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(daily_trend.index, daily_trend['median'], color='#D81B60', lw=2.5, label='Statewide Median Depth (mbgl)')
ax.fill_between(daily_trend.index, daily_trend['p25'], daily_trend['p75'], color='#D81B60', alpha=0.2, label='Interquartile Range (25th - 75th percentile)')

# Add threshold guideline lines
ax.axhline(2, color='#1E88E5', linestyle='--', alpha=0.7, label='Threshold: Flood / Waterlogging Risk (2m)')
ax.axhline(10, color='#FB8C00', linestyle='--', alpha=0.7, label='Threshold: Moderate Drought (10m)')
ax.axhline(15, color='#E53935', linestyle='--', alpha=0.7, label='Threshold: Severe Drought (15m)')

ax.set_title("Groundwater Depletion Trend Across Maharashtra (Jan - May 2026)", fontsize=13, fontweight='bold', pad=15)
ax.set_ylabel("Depth Below Ground Level (Meters - Deeper is Drier)", fontsize=11)
ax.set_xlabel("Date", fontsize=11)
ax.invert_yaxis() # Invert so deeper water table appears physically lower on y-axis!
ax.legend(loc='lower left', frameon=True)
plt.tight_layout()
plt.savefig("visualizations/02_temporal_depletion_trend.png", dpi=200)
plt.close()

# --- CHART 3: District-Wise Drought Vulnerability Ranking ---
print("Generating Chart 3: District Vulnerability Ranking...")
dist_avg = df_clean.groupby('District')['Depth_mbgl'].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 10))
bar_colors = ['#E53935' if v >= 15 else '#FB8C00' if v >= 10 else '#43A047' if v >= 5 else '#1E88E5' for v in dist_avg.values]
ax.barh(dist_avg.index, dist_avg.values, color=bar_colors, edgecolor='black', alpha=0.85)
ax.axvline(15, color='#E53935', linestyle='--', lw=1.5, label='Severe Drought Threshold (15m)')
ax.axvline(10, color='#FB8C00', linestyle='--', lw=1.5, label='Moderate Drought Threshold (10m)')
ax.set_title("District-Wise Average Groundwater Depth (mbgl) in Maharashtra", fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel("Average Depth Below Ground Level (Meters)", fontsize=11)
ax.invert_yaxis()
ax.legend(loc='lower right')
plt.tight_layout()
plt.savefig("visualizations/03_district_vulnerability_ranking.png", dpi=200)
plt.close()

# --- CHART 4: Station Case Study (AALEGAON in Akola) ---
print("Generating Chart 4: Station Case Study...")
st_data = df_clean[df_clean['Station'] == 'AALEGAON'].sort_values('DateTime')
if len(st_data) > 0:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(st_data['DateTime'], st_data['Depth_mbgl'], marker='o', markersize=3, color='#8E24AA', lw=1.5, label='Aalegaon Station Depth')
    ax.axhline(10, color='#FB8C00', linestyle='--', alpha=0.7, label='Moderate Drought Threshold (10m)')
    ax.axhline(15, color='#E53935', linestyle='--', alpha=0.7, label='Severe Drought Threshold (15m)')
    ax.set_title("Station Telemetry Profile: AALEGAON (Akola District, Patur Tehsil)", fontsize=13, fontweight='bold', pad=15)
    ax.set_ylabel("Depth Below Ground Level (mbgl)", fontsize=11)
    ax.set_xlabel("Observation Time", fontsize=11)
    ax.invert_yaxis()
    ax.legend(loc='lower left')
    plt.tight_layout()
    plt.savefig("visualizations/04_aalegaon_station_profile.png", dpi=200)
    plt.close()

print("All charts successfully generated in visualizations/ folder!")
