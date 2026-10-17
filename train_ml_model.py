import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, f1_score, mean_absolute_error, r2_score
from xgboost import XGBClassifier, XGBRegressor

os.makedirs("models", exist_ok=True)
CSV_FILE = "gwl_tel_6_hourly_maharashtra_gw_mh_2026_2030 (1).csv"

print("--- Step 1: Loading and Preprocessing Telemetry Data ---")
df = pd.read_csv(CSV_FILE, low_memory=False)
df.columns = df.columns.str.strip()

time_col = 'Data Acquisition Time'
val_col = 'Groundwater Level Telemetry 6 Hourly (meter)'

df['DateTime'] = pd.to_datetime(df[time_col], format='%d-%m-%Y %H:%M', errors='coerce')

# Filter error code 1.0000 and extreme outliers
is_dummy = (df[val_col] == 1.0)
is_glitch = (df[val_col] < -60) | (df[val_col] > 60)
valid_mask = (~is_dummy) & (~is_glitch) & df['DateTime'].notna() & df['Latitude'].notna() & df['Longitude'].notna()

df_clean = df[valid_mask].copy()

# Standardize depth to positive meters below ground level (mbgl)
station_means = df_clean.groupby('Station')[val_col].mean()
pos_stations = set(station_means[station_means > 0].index)

def calculate_depth(row):
    return row[val_col] if row['Station'] in pos_stations else -1.0 * row[val_col]

df_clean['Depth_mbgl'] = df_clean.apply(calculate_depth, axis=1)
df_clean = df_clean[(df_clean['Depth_mbgl'] >= 0) & (df_clean['Depth_mbgl'] <= 60)]

# Sort by station and time for feature engineering
df_clean = df_clean.sort_values(['Station', 'DateTime']).reset_index(drop=True)

print(f"Total clean samples for ML: {len(df_clean):,}")

# --- Step 2: Feature Engineering & Spatial Density Weighting ---
print("\n--- Step 2: Engineering Spatial Features & Calculating Inverse Density Weights ---")

# Temporal cyclical features
df_clean['Month'] = df_clean['DateTime'].dt.month
df_clean['Day'] = df_clean['DateTime'].dt.day
df_clean['Hour'] = df_clean['DateTime'].dt.hour
df_clean['DayOfYear'] = df_clean['DateTime'].dt.dayofyear

df_clean['Sin_DayOfYear'] = np.sin(2 * np.pi * df_clean['DayOfYear'] / 365.25)
df_clean['Cos_DayOfYear'] = np.cos(2 * np.pi * df_clean['DayOfYear'] / 365.25)

# Hydrological Lag features per station (telemetry history)
df_clean['Lag_1_Depth'] = df_clean.groupby('Station')['Depth_mbgl'].shift(1)
df_clean['Lag_4_Depth'] = df_clean.groupby('Station')['Depth_mbgl'].shift(4)
df_clean['Rolling_7d_Mean'] = df_clean.groupby('Station')['Depth_mbgl'].transform(lambda x: x.rolling(28, min_periods=1).mean())
df_clean['Rate_Of_Decline_24h'] = df_clean['Lag_1_Depth'] - df_clean['Lag_4_Depth']

df_clean['Lag_1_Depth'] = df_clean['Lag_1_Depth'].fillna(df_clean['Depth_mbgl'])
df_clean['Lag_4_Depth'] = df_clean['Lag_4_Depth'].fillna(df_clean['Depth_mbgl'])
df_clean['Rate_Of_Decline_24h'] = df_clean['Rate_Of_Decline_24h'].fillna(0.0)

# Fill elevation if missing with district median
district_elev = df_clean.groupby('District')['RL_MSL'].median().to_dict()
df_clean['RL_MSL'] = df_clean.apply(lambda r: district_elev.get(r['District'], 350.0) if pd.isna(r['RL_MSL']) or r['RL_MSL'] == '-' else float(r['RL_MSL']), axis=1)

# Categorical Alert Label:
def get_alert_label(d):
    if d <= 2.0:
        return 0
    elif d <= 5.0:
        return 1
    elif d <= 10.0:
        return 2
    elif d <= 15.0:
        return 3
    else:
        return 4

df_clean['Alert_Class'] = df_clean['Depth_mbgl'].apply(get_alert_label)

# District Frequency Encoding
district_freq = df_clean['District'].value_counts(normalize=True).to_dict()
df_clean['District_Freq'] = df_clean['District'].map(district_freq)

# --- SPATIAL DENSITY WEIGHTING (CRITICAL FIX FOR SPATIAL IMBALANCE) ---
# Calculate number of monitoring stations per district
st_counts = df_clean.groupby('District')['Station'].nunique()
print("\nSpatial Sampling Profile:")
print(f"Most Dense District: {st_counts.idxmax()} ({st_counts.max()} stations)")
print(f"Most Sparse District: {st_counts.idxmin()} ({st_counts.min()} stations)")

# Inverse spatial density weight: W_i = 1 / (Station Count in District)
raw_weights = 1.0 / df_clean['District'].map(st_counts)
# Normalize so mean weight = 1.0 (preserves standard gradient scale)
df_clean['Spatial_Weight'] = raw_weights / raw_weights.mean()

print(f"Sample weight range: Min = {df_clean['Spatial_Weight'].min():.3f} (for dense clusters) to Max = {df_clean['Spatial_Weight'].max():.3f} (for sparse regions)")

# Feature matrix
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

# --- Step 3: Train-Test Split with Spatial Weights ---
print("\n--- Step 3: Splitting Dataset (80% Train, 20% Test) ---")
X_train, X_test, y_train_cls, y_test_cls, w_train, w_test, d_train, d_test = train_test_split(
    X, y_class, weights, districts, test_size=0.2, random_state=42, stratify=y_class
)
_, _, y_train_reg, y_test_reg = train_test_split(X, y_reg, test_size=0.2, random_state=42, stratify=y_class)

# --- Step 4: Training Spatially-Weighted XGBoost Alert Classifier ---
print("\n--- Step 4: Training Spatially-Weighted XGBoost Alert Classifier ---")
clf = XGBClassifier(
    n_estimators=150,
    learning_rate=0.08,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist',
    n_jobs=-1
)
# Train with sample weights to balance sparse vs dense districts!
clf.fit(X_train, y_train_cls, sample_weight=w_train)

y_pred_cls = clf.predict(X_test)
acc = accuracy_score(y_test_cls, y_pred_cls)
f1 = f1_score(y_test_cls, y_pred_cls, average='weighted')

print(f"\n>>> Model 1 (Alert Classifier) Overall Performance:")
print(f"Accuracy: {acc * 100:.2f}%")
print(f"Weighted F1-Score: {f1:.4f}")

# Per-District Evaluation (Dense vs Sparse)
test_results_df = pd.DataFrame({
    'District': d_test,
    'True_Class': y_test_cls,
    'Pred_Class': y_pred_cls
})

sparse_districts = ['Dhule', 'Hingoli', 'Nandurbar', 'Palghar', 'Washim']
dense_districts = ['Sangli', 'Nashik', 'Amravati', 'Jalgaon', 'Latur']

print("\n--- Spatial Evaluation: Dense vs Sparse Districts Accuracy ---")
for d in sparse_districts:
    sub = test_results_df[test_results_df['District'] == d]
    if len(sub) > 0:
        d_acc = accuracy_score(sub['True_Class'], sub['Pred_Class'])
        print(f"Sparse District [{d.ljust(10)}] (4-5 stations): Accuracy = {d_acc * 100:.2f}% (Test Samples: {len(sub)})")

print("")
for d in dense_districts:
    sub = test_results_df[test_results_df['District'] == d]
    if len(sub) > 0:
        d_acc = accuracy_score(sub['True_Class'], sub['Pred_Class'])
        print(f"Dense District  [{d.ljust(10)}] (80-92 stations): Accuracy = {d_acc * 100:.2f}% (Test Samples: {len(sub)})")

# --- Step 5: Training Spatially-Weighted XGBoost Depth Regressor ---
print("\n--- Step 5: Training Spatially-Weighted XGBoost Depth Regressor ---")
reg = XGBRegressor(
    n_estimators=150,
    learning_rate=0.08,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    tree_method='hist',
    n_jobs=-1
)
# Train with sample weights!
reg.fit(X_train, y_train_reg, sample_weight=w_train)

y_pred_reg = reg.predict(X_test)
mae = mean_absolute_error(y_test_reg, y_pred_reg)
r2 = r2_score(y_test_reg, y_pred_reg)

print(f"\n>>> Model 2 (Depth Regressor) Overall Performance:")
print(f"Mean Absolute Error (MAE): {mae:.3f} meters")
print(f"R-Squared (R²): {r2:.4f}")

# --- Step 6: Save Models & Metadata ---
print("\n--- Step 6: Saving Spatially-Balanced Model Bundle ---")
model_artifacts = {
    'classifier': clf,
    'regressor': reg,
    'feature_cols': feature_cols,
    'district_freq': district_freq,
    'district_elev': district_elev,
    'st_counts': st_counts.to_dict(),
    'metrics': {
        'classification_accuracy': float(acc),
        'classification_f1': float(f1),
        'regression_mae': float(mae),
        'regression_r2': float(r2),
        'spatial_weighting_applied': True
    }
}

joblib.dump(model_artifacts, 'models/groundwater_ml_bundle.joblib')
print("Successfully saved spatially-balanced models to 'models/groundwater_ml_bundle.joblib'!")
