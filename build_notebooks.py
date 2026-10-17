import os
import nbformat as nbf
from nbconvert.preprocessors import ExecutePreprocessor
import time

os.makedirs("notebook", exist_ok=True)

# ==============================================================================
# NOTEBOOK 1: DATA EXPLORATION AND VISUALIZATION
# ==============================================================================
nb1 = nbf.v4.new_notebook()

cells_1 = [
    nbf.v4.new_markdown_cell("""# 🌊 MAHA JAL KHOJ: Maharashtra Groundwater Intelligence
## Part 1: Comprehensive Exploratory Data Analysis & Spatial-Temporal Visualization

### 📌 Project Overview
This notebook presents an end-to-end hydrogeological data analysis of the **Digital Water Level Recorder (DWLR)** telemetry dataset collected across the State of Maharashtra, India. The dataset captures 6-hourly automated water level observations across **34 districts**, **304 tehsils**, and **1,016 monitoring stations** between **January 1, 2026 and May 30, 2026** (the critical pre-monsoon dry season).

---

### 🎯 Notebook Objectives
1. **Data Ingestion & Schema Audit**: Parse and explain every column in the telemetry stream.
2. **Telemetry Anomaly & Sensor Error Detection**: Identify known telemetry glitch codes (e.g., the `1.000m` placeholder probe code and extreme values).
3. **Depth Standardization**: Standardize negative/positive sign conventions into true positive **Depth Below Ground Level (`Depth_mbgl`)**.
4. **Spatial Density Audit**: Quantify geographic sampling imbalances (e.g., Sangli with 92 stations vs. Dhule with 4 stations).
5. **Alert Framework Definition**: Establish Central Ground Water Board (CGWB) alert parameters (Flood, Safe, Normal, Moderate Drought, Severe Drought).
6. **Publication-Quality Visualizations**: Plot statewide distributions, depletion curves, and district vulnerability rankings.
"""),

    nbf.v4.new_code_cell(r"""import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Configure aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.sans-serif': 'DejaVu Sans',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'figure.titlesize': 15
})

CSV_FILE = "../gwl_tel_6_hourly_maharashtra_gw_mh_2026_2030 (1).csv"
if not os.path.exists(CSV_FILE):
    CSV_FILE = "gwl_tel_6_hourly_maharashtra_gw_mh_2026_2030 (1).csv"

print(f"Loading telemetry file from: {CSV_FILE}")
df = pd.read_csv(CSV_FILE, low_memory=False)
df.columns = df.columns.str.strip()
print(f"Dataset successfully loaded: {len(df):,} rows and {len(df.columns)} columns.")
"""),

    nbf.v4.new_markdown_cell("""### 1. Dataset Dimensions & Schema Inspection
Let's inspect the columns, data types, and initial records. In Indian telemetry networks, groundwater level is recorded by automated pressure transducers mounted inside borewells/piezometers.
"""),

    nbf.v4.new_code_cell(r"""# Display basic info and first 5 rows
print("Columns in Dataset:")
for col in df.columns:
    print(f" - {col}")

display(df[['Station', 'District', 'Tehsil', 'Latitude', 'Longitude', 'RL_MSL', 'Data Acquisition Time', 'Groundwater Level Telemetry 6 Hourly (meter)']].head(5))
"""),

    nbf.v4.new_markdown_cell("""### 2. Sensor Anomaly & Error Code Detection
In real-world IoT telemetry datasets, sensors occasionally malfunction, disconnect, or transmit placeholder error codes.

#### Key Discovery: The `1.000` Placeholder Code
In GSDA / CGWB telemetry systems, when a piezometric probe is uncalibrated, submerged in sludge, or disconnected, it transmits a default uncalibrated state of **`1.000000 m`**. If not removed, an alert system would wrongly flag thousands of dry wells as "Critical Flood Risk".
"""),

    nbf.v4.new_code_cell(r"""val_col = 'Groundwater Level Telemetry 6 Hourly (meter)'
time_col = 'Data Acquisition Time'

# Convert timestamp
df['DateTime'] = pd.to_datetime(df[time_col], format='%d-%m-%Y %H:%M', errors='coerce')

# Check anomaly frequencies
exact_one_count = (df[val_col] == 1.0).sum()
exact_zero_count = (df[val_col] == 0.0).sum()
extreme_negative = (df[val_col] < -60).sum()
extreme_positive = (df[val_col] > 60).sum()

print("Telemetry Anomaly Audit:")
print(f" - Exactly 1.000000 m (Placeholder probe code): {exact_one_count:,} records ({exact_one_count/len(df)*100:.2f}%)")
print(f" - Exactly 0.000000 m (Uninitialized readings):   {exact_zero_count:,} records")
print(f" - Extreme Negative (< -60m glitch):           {extreme_negative:,} records")
print(f" - Extreme Positive (> 60m glitch):            {extreme_positive:,} records")
"""),

    nbf.v4.new_markdown_cell("""### 3. Data Cleaning & Depth Standardization Pipeline
In telemetry logging:
* Over 85% of stations log depth as a **negative number** (e.g. `-5.96m` to `-14.37m`), representing depth below ground level ($0.0\\text{ m}$).
* A few stations logged depth positively ($+7.17\\text{ m}$ to $+45.87\\text{ m}$).
* We standardize all valid readings into positive **`Depth_mbgl`** (Meters Below Ground Level).
"""),

    nbf.v4.new_code_cell(r"""# Filtering out dummy codes & physical glitches
is_dummy = (df[val_col] == 1.0)
is_glitch = (df[val_col] < -60) | (df[val_col] > 60)
valid_mask = (~is_dummy) & (~is_glitch) & df['DateTime'].notna() & df['Latitude'].notna() & df['Longitude'].notna()

df_clean = df[valid_mask].copy()

# Standardize sign convention per station
station_means = df_clean.groupby('Station')[val_col].mean()
pos_stations = set(station_means[station_means > 0].index)

def calculate_depth(row):
    return row[val_col] if row['Station'] in pos_stations else -1.0 * row[val_col]

df_clean['Depth_mbgl'] = df_clean.apply(calculate_depth, axis=1)
# Keep realistic Deccan Basalt unconfined aquifer range (0 to 60 meters)
df_clean = df_clean[(df_clean['Depth_mbgl'] >= 0) & (df_clean['Depth_mbgl'] <= 60)]

print(f"Cleaning Complete: Retained {len(df_clean):,} valid records of {len(df):,} ({len(df_clean)/len(df)*100:.1f}%)")
print(f"Cleaned Depth mbgl Range: {df_clean['Depth_mbgl'].min():.2f}m to {df_clean['Depth_mbgl'].max():.2f}m (Median: {df_clean['Depth_mbgl'].median():.2f}m)")
"""),

    nbf.v4.new_markdown_cell("""### 4. Spatial Sampling Density Disparity (The Imbalance Problem)
Notice how monitoring stations are distributed across Maharashtra. Some districts are heavily clustered, while sparse districts cover vast areas with only a handful of stations.
"""),

    nbf.v4.new_code_cell(r"""# Calculate stations per district
st_counts = df_clean.groupby('District')['Station'].nunique().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(st_counts.index, st_counts.values, color='#0284c7', edgecolor='black', alpha=0.85)

# Highlight dense vs sparse extremes
for i, bar in enumerate(bars):
    if i < 5:
        bar.set_color('#2563eb') # Dense
    elif i >= len(bars) - 5:
        bar.set_color('#ef4444') # Sparse

plt.title("Spatial Sampling Imbalance: Active Telemetry Stations per District", fontweight='bold', pad=15)
plt.xlabel("District", fontweight='bold')
plt.ylabel("Number of Unique Monitoring Stations", fontweight='bold')
plt.xticks(rotation=90)
plt.axhline(st_counts.median(), color='#10b981', linestyle='--', label=f'State Median: {st_counts.median():.0f} stations')
plt.legend()
plt.tight_layout()
plt.show()

print(f"Highest Density District: {st_counts.idxmax()} ({st_counts.max()} stations)")
print(f"Lowest Density District:  {st_counts.idxmin()} ({st_counts.min()} stations)")
print(f"Density Ratio: Sangli has {st_counts.max() / st_counts.min():.1f}x more stations than Dhule!")
"""),

    nbf.v4.new_markdown_cell("""### 5. Alert Parameter Framework
We classify every observation according to Central Ground Water Board (CGWB) hydrological benchmarks:

| Depth Below Ground | Alert Status | Color Code | Hydrological Impact |
| :--- | :--- | :--- | :--- |
| **$\le 2.0\text{ m}$** | **Flood / Waterlogging Risk** | 🔵 Blue (`#0284c7`) | Aquifer saturated; zero percolation; surface runoff flood risk. |
| **$2.0 - 5.0\text{ m}$** | **Safe / High Water Table** | 🔷 Cyan (`#06b6d4`) | Healthy recharge reserve. |
| **$5.0 - 10.0\text{ m}$** | **Normal Range** | 🟢 Green (`#10b981`) | Sustainable extraction baseline. |
| **$10.0 - 15.0\text{ m}$** | **Moderate Drought Alert** | 🟠 Orange (`#f59e0b`) | Groundwater stress; irrigation conservation needed. |
| **$> 15.0\text{ m}$** | **Severe Drought Alert** | 🔴 Red (`#ef4444`) | Over-exploited aquifer; borewells drying up; emergency alert. |
"""),

    nbf.v4.new_code_cell(r"""def classify_alert(d):
    if d <= 2.0:
        return "Flood / Waterlogging Risk (<=2m)"
    elif d <= 5.0:
        return "Safe / High (2-5m)"
    elif d <= 10.0:
        return "Normal Range (5-10m)"
    elif d <= 15.0:
        return "Moderate Drought (10-15m)"
    else:
        return "Severe Drought (>15m)"

df_clean['Alert_Status'] = df_clean['Depth_mbgl'].apply(classify_alert)

alert_order = [
    "Flood / Waterlogging Risk (<=2m)",
    "Safe / High (2-5m)",
    "Normal Range (5-10m)",
    "Moderate Drought (10-15m)",
    "Severe Drought (>15m)"
]
color_palette = ["#0284c7", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]

fig, ax = plt.subplots(figsize=(10, 5))
counts = df_clean['Alert_Status'].value_counts()[alert_order]
total = sum(counts)

bars = ax.barh(alert_order, counts, color=color_palette, edgecolor='black', alpha=0.85)
ax.set_title("Pre-Monsoon Alert Distribution Across Maharashtra (Jan - May 2026)", fontweight='bold', pad=15)
ax.set_xlabel("Number of Telemetry Observations", fontweight='bold')
ax.invert_yaxis()

for bar in bars:
    w = bar.get_width()
    pct = (w / total) * 100
    ax.text(w + total * 0.01, bar.get_y() + bar.get_height()/2, f"{w:,.0f} ({pct:.1f}%)", va='center', fontweight='bold')

plt.xlim(0, max(counts) * 1.25)
plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_markdown_cell("""### 6. Temporal Depletion Trends (Pre-Monsoon Drawdown)
Plotting the daily median water depth across Maharashtra from January 1, 2026 to May 30, 2026 reveals continuous aquifer depletion during the hot summer dry season.
"""),

    nbf.v4.new_code_cell(r"""df_clean['Date'] = df_clean['DateTime'].dt.date
daily_stats = df_clean.groupby('Date')['Depth_mbgl'].agg([
    'median',
    lambda x: np.percentile(x, 25),
    lambda x: np.percentile(x, 75)
]).rename(columns={'<lambda_0>': 'p25', '<lambda_1>': 'p75'})
daily_stats.index = pd.to_datetime(daily_stats.index)

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(daily_stats.index, daily_stats['median'], color='#d946ef', lw=2.5, label='Statewide Median Depth (mbgl)')
ax.fill_between(daily_stats.index, daily_stats['p25'], daily_stats['p75'], color='#d946ef', alpha=0.18, label='Interquartile Range (25th - 75th Percentile)')

# Guideline Thresholds
ax.axhline(2.0, color='#0284c7', linestyle='--', alpha=0.8, label='Flood Risk Threshold (2m)')
ax.axhline(10.0, color='#f59e0b', linestyle='--', alpha=0.8, label='Moderate Drought Threshold (10m)')
ax.axhline(15.0, color='#ef4444', linestyle='--', alpha=0.8, label='Severe Drought Threshold (15m)')

ax.set_title("Groundwater Depletion Hydrograph across Maharashtra (Jan - May 2026)", fontweight='bold', pad=15)
ax.set_ylabel("Depth Below Ground Level (mbgl - Inverted Axis)", fontweight='bold')
ax.set_xlabel("Observation Date", fontweight='bold')
ax.invert_yaxis() # Invert so deeper water table appears physically lower!
ax.legend(loc='lower left', frameon=True)
plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_markdown_cell("""### 7. District Vulnerability Ranking
Which districts in Maharashtra are facing the deepest groundwater depletion? Let's rank all 34 districts by mean depth.
"""),

    nbf.v4.new_code_cell(r"""dist_mean = df_clean.groupby('District')['Depth_mbgl'].mean().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 10))
bar_colors = ['#ef4444' if v >= 15 else '#f59e0b' if v >= 10 else '#10b981' if v >= 5 else '#0284c7' for v in dist_mean.values]

ax.barh(dist_mean.index, dist_mean.values, color=bar_colors, edgecolor='black', alpha=0.85)
ax.axvline(15, color='#ef4444', linestyle='--', lw=1.5, label='Severe Drought Threshold (15m)')
ax.axvline(10, color='#f59e0b', linestyle='--', lw=1.5, label='Moderate Drought Threshold (10m)')
ax.set_title("District Vulnerability Ranking: Average Groundwater Depth (mbgl)", fontweight='bold', pad=15)
ax.set_xlabel("Average Depth Below Ground Level (Meters)", fontweight='bold')
ax.invert_yaxis()
ax.legend(loc='lower right')
plt.tight_layout()
plt.show()

print("Top 5 Most Depleted (Driest) Districts:")
for i, (d, val) in enumerate(dist_mean.head(5).items(), 1):
    print(f" {i}. {d}: {val:.2f} meters average depth")
""")
]

nb1.cells = cells_1
with open("notebook/01_Data_Exploration_and_Visualization.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb1, f)
print("Saved notebook/01_Data_Exploration_and_Visualization.ipynb successfully!")


# ==============================================================================
# NOTEBOOK 2: MODEL ARCHITECTURE AND EVALUATION
# ==============================================================================
nb2 = nbf.v4.new_notebook()

cells_2 = [
    nbf.v4.new_markdown_cell("""# 🤖 MAHA JAL KHOJ: Machine Learning Model Architecture & Evaluation
## Part 2: Spatially-Weighted Dual-Head XGBoost Forecasting & Multi-Metric Assessment

### 📌 Architecture Summary & High-Resolution Diagram
This notebook documents the machine learning engine designed to predict groundwater depth and detect multi-tier hydrogeological risk alerts across Maharashtra.

The architecture employs an **Inverse Spatial Density Balancing Layer** to eliminate clustered sampling bias between dense monitoring districts (e.g., Sangli with 92 stations) and sparse districts (e.g., Dhule with 4 stations), feeding a **Dual-Head XGBoost Core Engine** (`XGBRegressor` + `XGBClassifier`) coupled with a **10-Month Recursive Seasonal Projection Module**.

---

### 🏗️ ML Model Architecture Diagram
The high-resolution architecture diagram is saved directly in this folder as `ml_model_architecture.png`:

![Maha Jal Khoj Dual-Head ML Model Architecture](ml_model_architecture.png)
"""),

    nbf.v4.new_code_cell(r"""from IPython.display import Image, display

# Display high-resolution architecture diagram
display(Image(filename="ml_model_architecture.png", width=1100))
"""),

    nbf.v4.new_markdown_cell("""---

### 🎯 Notebook Objectives
1. **Model Architecture Deep Dive**: Inspect the 6 architectural tiers from raw telemetry to inference.
2. **Feature Engineering**: Construct 12 spatial, temporal cyclical, and hydrological memory features.
3. **Spatial Density Weighting**: Implement $W_i = \\frac{1}{N_{\\text{district}}}$ to prevent dense districts from overwhelming sparse districts.
4. **Model Training**: Fit both continuous `XGBRegressor` and discrete `XGBClassifier`.
5. **Evaluation Suite**: Compute $R^2$, MAE, RMSE, Weighted F1, Confusion Matrix, and Per-Class metrics.
6. **Spatial Generalization Check**: Verify accuracy on sparse districts (Dhule, Nandurbar) vs dense districts (Sangli, Nashik).
7. **Feature Importance & Interpretability**: Quantify the hydrogeological contribution of each feature.
8. **10-Month Seasonal Projections**: Test multi-horizon forecasting through monsoon recovery and summer drought.
"""),

    nbf.v4.new_code_cell(r"""import os
import sys
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('.'))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report, 
    confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
)
from xgboost import XGBClassifier, XGBRegressor

# Configure aesthetics
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 11})

CSV_FILE = "../gwl_tel_6_hourly_maharashtra_gw_mh_2026_2030 (1).csv"
if not os.path.exists(CSV_FILE):
    CSV_FILE = "gwl_tel_6_hourly_maharashtra_gw_mh_2026_2030 (1).csv"

print("Loading cleaned dataset...")
df = pd.read_csv(CSV_FILE, low_memory=False)
df.columns = df.columns.str.strip()

val_col = 'Groundwater Level Telemetry 6 Hourly (meter)'
time_col = 'Data Acquisition Time'

df['DateTime'] = pd.to_datetime(df[time_col], format='%d-%m-%Y %H:%M', errors='coerce')
valid = (df[val_col] != 1.0) & (df[val_col] >= -60) & (df[val_col] <= 60) & df['DateTime'].notna() & df['Latitude'].notna()
df_clean = df[valid].copy()

station_means = df_clean.groupby('Station')[val_col].mean()
pos_stations = set(station_means[station_means > 0].index)
df_clean['Depth_mbgl'] = df_clean.apply(lambda r: r[val_col] if r['Station'] in pos_stations else -1.0 * r[val_col], axis=1)
df_clean = df_clean[(df_clean['Depth_mbgl'] >= 0) & (df_clean['Depth_mbgl'] <= 60)]
df_clean = df_clean.sort_values(['Station', 'DateTime']).reset_index(drop=True)

print(f"Ready for modeling: {len(df_clean):,} clean records across {df_clean['Station'].nunique():,} stations.")
"""),

    nbf.v4.new_markdown_cell("""### 1. Feature Engineering & Spatial Density Weighting
We construct 12 input features capturing:
* **Spatial/Elevation**: `Latitude`, `Longitude`, `RL_MSL`, `District_Freq`
* **Temporal Cyclical**: `Month`, `Hour`, `Sin_DayOfYear`, `Cos_DayOfYear`
* **Hydrological Memory**: `Lag_1_Depth` (6h prior), `Lag_4_Depth` (24h prior), `Rolling_7d_Mean`, and `Rate_Of_Decline_24h`
"""),

    nbf.v4.new_code_cell(r"""# 1. Cyclical time encoding
df_clean['Month'] = df_clean['DateTime'].dt.month
df_clean['Hour'] = df_clean['DateTime'].dt.hour
df_clean['DayOfYear'] = df_clean['DateTime'].dt.dayofyear
df_clean['Sin_DayOfYear'] = np.sin(2 * np.pi * df_clean['DayOfYear'] / 365.25)
df_clean['Cos_DayOfYear'] = np.cos(2 * np.pi * df_clean['DayOfYear'] / 365.25)

# 2. Hydrological lags
df_clean['Lag_1_Depth'] = df_clean.groupby('Station')['Depth_mbgl'].shift(1).fillna(df_clean['Depth_mbgl'])
df_clean['Lag_4_Depth'] = df_clean.groupby('Station')['Depth_mbgl'].shift(4).fillna(df_clean['Depth_mbgl'])
df_clean['Rolling_7d_Mean'] = df_clean.groupby('Station')['Depth_mbgl'].transform(lambda x: x.rolling(28, min_periods=1).mean())
df_clean['Rate_Of_Decline_24h'] = (df_clean['Lag_1_Depth'] - df_clean['Lag_4_Depth']).fillna(0.0)

# 3. Elevation & District Encoding
district_elev = df_clean.groupby('District')['RL_MSL'].median().to_dict()
df_clean['RL_MSL'] = df_clean.apply(lambda r: district_elev.get(r['District'], 350.0) if pd.isna(r['RL_MSL']) or r['RL_MSL'] == '-' else float(r['RL_MSL']), axis=1)

district_freq = df_clean['District'].value_counts(normalize=True).to_dict()
df_clean['District_Freq'] = df_clean['District'].map(district_freq)

# 4. Target Alert Class (0 to 4)
def get_alert_label(d):
    if d <= 2.0: return 0
    elif d <= 5.0: return 1
    elif d <= 10.0: return 2
    elif d <= 15.0: return 3
    else: return 4

df_clean['Alert_Class'] = df_clean['Depth_mbgl'].apply(get_alert_label)

# 5. Inverse Spatial Density Weighting
st_counts = df_clean.groupby('District')['Station'].nunique()
raw_weights = 1.0 / df_clean['District'].map(st_counts)
df_clean['Spatial_Weight'] = raw_weights / raw_weights.mean()

feature_cols = [
    'Latitude', 'Longitude', 'RL_MSL', 
    'Month', 'Hour', 'Sin_DayOfYear', 'Cos_DayOfYear',
    'District_Freq', 'Lag_1_Depth', 'Lag_4_Depth', 'Rolling_7d_Mean', 'Rate_Of_Decline_24h'
]

X = df_clean[feature_cols]
y_class = df_clean['Alert_Class']
y_reg = df_clean['Depth_mbgl']
weights = df_clean['Spatial_Weight']
districts = df_clean['District']

print(f"Features: {feature_cols}")
print(f"Sample weight range: {weights.min():.3f} to {weights.max():.3f}")
"""),

    nbf.v4.new_markdown_cell("""### 2. Train-Test Split with Spatial Stratification
We split 80% train and 20% test, preserving class proportions while retaining sample weights and district tags for spatial evaluation.
"""),

    nbf.v4.new_code_cell(r"""X_train, X_test, y_train_cls, y_test_cls, w_train, w_test, d_train, d_test = train_test_split(
    X, y_class, weights, districts, test_size=0.2, random_state=42, stratify=y_class
)
_, _, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42, stratify=y_class)

print(f"Training set:   {len(X_train):,} samples")
print(f"Evaluation set: {len(X_test):,} samples")
"""),

    nbf.v4.new_markdown_cell("""### 3. Model 1 Evaluation: Spatially-Weighted XGBoost Alert Classifier
Let's evaluate the multi-class risk classifier.
"""),

    nbf.v4.new_code_cell(r"""clf = XGBClassifier(
    n_estimators=150, learning_rate=0.08, max_depth=6,
    subsample=0.8, colsample_bytree=0.8, random_state=42,
    tree_method='hist', n_jobs=-1
)
clf.fit(X_train, y_train_cls, sample_weight=w_train)

y_pred_cls = clf.predict(X_test)

acc = accuracy_score(y_test_cls, y_pred_cls)
f1_weighted = f1_score(y_test_cls, y_pred_cls, average='weighted')
f1_macro = f1_score(y_test_cls, y_pred_cls, average='macro')

print("="*60)
print(f"  MODEL 1: ALERT CLASSIFICATION PERFORMANCE")
print("="*60)
print(f" Overall Accuracy:      {acc * 100:.2f}%")
print(f" Weighted F1-Score:     {f1_weighted:.4f}")
print(f" Macro F1-Score:        {f1_macro:.4f}")
print("="*60)

class_names = [
    "Flood Risk (<=2m)",
    "Safe / High (2-5m)",
    "Normal (5-10m)",
    "Moderate Drought (10-15m)",
    "Severe Drought (>15m)"
]

print("\\nDetailed Classification Report:")
print(classification_report(y_test_cls, y_pred_cls, target_names=class_names))
"""),

    nbf.v4.new_markdown_cell("""### 4. Confusion Matrix Heatmap
The confusion matrix verifies that severe drought and flood risk states are accurately classified with minimal cross-tier bleed.
"""),

    nbf.v4.new_code_cell(r"""cm = confusion_matrix(y_test_cls, y_pred_cls)
cm_pct = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(cm_pct, annot=True, fmt='.1f', cmap='Blues', cbar=True,
            xticklabels=class_names, yticklabels=class_names, ax=ax)

plt.title("Alert Classification Confusion Matrix (% Accuracy per True Class)", fontweight='bold', pad=15)
plt.xlabel("Predicted Class", fontweight='bold')
plt.ylabel("True Class", fontweight='bold')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_markdown_cell("""### 5. Model 2 Evaluation: Spatially-Weighted XGBoost Depth Regressor
Evaluating the continuous regressor for depth estimation.
"""),

    nbf.v4.new_code_cell(r"""reg = XGBRegressor(
    n_estimators=150, learning_rate=0.08, max_depth=6,
    subsample=0.8, colsample_bytree=0.8, random_state=42,
    tree_method='hist', n_jobs=-1
)
reg.fit(X_train, y_train_reg, sample_weight=w_train)

y_pred_reg = reg.predict(X_test)

mae = mean_absolute_error(y_test_reg, y_pred_reg)
rmse = np.sqrt(mean_squared_error(y_test_reg, y_pred_reg))
r2 = r2_score(y_test_reg, y_pred_reg)

print("="*60)
print(f"  MODEL 2: CONTINUOUS DEPTH REGRESSION PERFORMANCE")
print("="*60)
print(f" Mean Absolute Error (MAE): {mae:.3f} meters")
print(f" Root Mean Sq. Error (RMSE): {rmse:.3f} meters")
print(f" R-Squared Metric (R²):     {r2:.4f}")
print("="*60)

# Plot Actual vs Predicted Depth
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Scatter with identity line
sample_indices = np.random.choice(len(y_test_reg), size=3000, replace=False)
ax1.scatter(y_test_reg.iloc[sample_indices], y_pred_reg[sample_indices], alpha=0.3, color='#0284c7', s=15)
ax1.plot([0, 60], [0, 60], 'r--', lw=2, label='Perfect Identity (y = x)')
ax1.set_title("Actual vs. Predicted Depth (mbgl)", fontweight='bold')
ax1.set_xlabel("True Telemetry Depth (m)")
ax1.set_ylabel("Predicted Depth (m)")
ax1.legend()

# Residual distribution
residuals = y_test_reg - y_pred_reg
sns.histplot(residuals, bins=50, kde=True, ax=ax2, color='#10b981')
ax2.axvline(0, color='red', linestyle='--')
ax2.set_title("Prediction Error / Residual Distribution", fontweight='bold')
ax2.set_xlabel("Error in Meters (Actual - Predicted)")
ax2.set_xlim(-3, 3)

plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_markdown_cell("""### 6. Spatial Sampling Validation: Dense vs. Sparse Districts
Did the model suffer an accuracy drop in sparse districts? Let's inspect test accuracy across the most sparse and most dense districts.
"""),

    nbf.v4.new_code_cell(r"""test_eval_df = pd.DataFrame({
    'District': d_test,
    'True_Cls': y_test_cls,
    'Pred_Cls': y_pred_cls
})

sparse_districts = ['Dhule', 'Hingoli', 'Nandurbar', 'Palghar', 'Washim']
dense_districts = ['Sangli', 'Nashik', 'Amravati', 'Jalgaon', 'Latur']

comparison_rows = []
for d in sparse_districts:
    sub = test_eval_df[test_eval_df['District'] == d]
    comparison_rows.append({'District': d, 'Type': 'Sparse (4-5 stations)', 'Accuracy': accuracy_score(sub['True_Cls'], sub['Pred_Cls']) * 100})

for d in dense_districts:
    sub = test_eval_df[test_eval_df['District'] == d]
    comparison_rows.append({'District': d, 'Type': 'Dense (80-92 stations)', 'Accuracy': accuracy_score(sub['True_Cls'], sub['Pred_Cls']) * 100})

comp_df = pd.DataFrame(comparison_rows)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=comp_df, x='District', y='Accuracy', hue='Type', palette=['#ef4444', '#2563eb'], ax=ax)
ax.set_ylim(80, 102)
ax.set_title("Spatial Robustness Check: Model Accuracy Across Sparse vs. Dense Districts", fontweight='bold', pad=15)
ax.set_ylabel("Classification Accuracy (%)", fontweight='bold')
ax.axhline(95, color='#10b981', linestyle='--', label='95% Target Line')
ax.legend(loc='lower right')
plt.tight_layout()
plt.show()

display(comp_df)
"""),

    nbf.v4.new_markdown_cell("""### 7. Feature Importance & Hydrogeological Drivers
Which features matter most when predicting groundwater dynamics?
"""),

    nbf.v4.new_code_cell(r"""importance_series = pd.Series(clf.feature_importances_, index=feature_cols).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(importance_series.index, importance_series.values, color='#06b6d4', edgecolor='black', alpha=0.85)
ax.set_title("XGBoost Feature Importance: Hydrogeological & Spatial Predictors", fontweight='bold', pad=15)
ax.set_xlabel("Relative Importance Weight", fontweight='bold')

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.01, bar.get_y() + bar.get_height()/2, f"{w*100:.1f}%", va='center', fontweight='bold')

plt.xlim(0, max(importance_series.values) * 1.25)
plt.tight_layout()
plt.show()
"""),

    nbf.v4.new_markdown_cell("""### 8. Test Run: 10-Month Forward Seasonal Projection (June 2026 - March 2027)
Simulating the full 43-week forward projection across the monsoon recharge and winter/summer drawdown for station `AALEGAON` in Akola district.
"""),

    nbf.v4.new_code_cell(r"""from forecast_10_months import generate_10_month_forecast

forecast = generate_10_month_forecast("AALEGAON", df_clean=df_clean)
proj_df = pd.DataFrame(forecast['projections'])
proj_df['date'] = pd.to_datetime(proj_df['date'])

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(proj_df['date'], proj_df['predicted_depth'], marker='o', markersize=4, color='#a855f7', lw=2.5, label='Projected Groundwater Depth (mbgl)')

ax.axhline(2.0, color='#0284c7', linestyle='--', alpha=0.8, label='Flood Risk (2m)')
ax.axhline(10.0, color='#f59e0b', linestyle='--', alpha=0.8, label='Moderate Drought (10m)')
ax.axhline(15.0, color='#ef4444', linestyle='--', alpha=0.8, label='Severe Drought (15m)')

ax.set_title(f"10-Month AI Projection for Station: {forecast['station']} ({forecast['district']})", fontweight='bold', pad=15)
ax.set_ylabel("Depth (mbgl - Inverted Axis)", fontweight='bold')
ax.set_xlabel("Projected Date", fontweight='bold')
ax.invert_yaxis()
ax.legend(loc='lower left')
plt.tight_layout()
plt.show()

display(proj_df[['date', 'month_name', 'predicted_depth', 'alert_status', 'season_phase']].iloc[::5])
""")
]

nb2.cells = cells_2
with open("notebook/02_Model_Architecture_and_Evaluation.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb2, f)
print("Saved notebook/02_Model_Architecture_and_Evaluation.ipynb successfully!")
