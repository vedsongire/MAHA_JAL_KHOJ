import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("notebook", exist_ok=True)
output_path = "notebook/ml_model_architecture.png"

# Setup high-resolution figure with modern dark aesthetic
fig, ax = plt.subplots(figsize=(20, 13), dpi=300)
fig.patch.set_facecolor('#0b0f19')
ax.set_facecolor('#0b0f19')

# Remove axes
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Color Palette
C_HEADER = '#06b6d4'      # Cyan
C_BG_CARD = '#131b2e'     # Dark navy card background
C_BORDER_INPUT = '#3b82f6' # Blue
C_BORDER_PREP = '#6366f1'  # Indigo
C_BORDER_FEAT = '#8b5cf6'  # Purple
C_BORDER_WEIGHT = '#ec4899'# Pink
C_BORDER_MODEL = '#10b981' # Emerald Green
C_BORDER_OUT = '#f59e0b'   # Amber
C_BORDER_SEASON = '#06b6d4'# Cyan
C_TEXT_MAIN = '#ffffff'
C_TEXT_MUTED = '#94a3b8'
C_TEXT_SUB = '#cbd5e1'

def draw_card(ax, x, y, w, h, title, subtitle, items, border_color, badge=None):
    # Shadow
    shadow = patches.FancyBboxPatch(
        (x + 0.4, y - 0.4), w, h,
        boxstyle="round,pad=0.5,rounding_size=1.2",
        facecolor='#05070d', edgecolor='none', alpha=0.6, zorder=2
    )
    ax.add_patch(shadow)

    # Main Card
    card = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.5,rounding_size=1.2",
        facecolor=C_BG_CARD, edgecolor=border_color, linewidth=2, zorder=3
    )
    ax.add_patch(card)

    # Header Bar Accent
    accent_bar = patches.FancyBboxPatch(
        (x + 0.2, y + h - 1.8), w - 0.4, 1.6,
        boxstyle="round,pad=0.2,rounding_size=0.6",
        facecolor=border_color, edgecolor='none', alpha=0.2, zorder=4
    )
    ax.add_patch(accent_bar)

    # Title
    ax.text(x + 1.2, y + h - 1.0, title, color=C_TEXT_MAIN, fontsize=12, fontweight='bold', zorder=5)

    if badge:
        ax.text(x + w - 1.2, y + h - 1.0, badge, color=border_color, fontsize=9, fontweight='bold',
                ha='right', zorder=5, bbox=dict(boxstyle='round,pad=0.2', facecolor='#0b0f19', edgecolor=border_color, lw=1))

    # Subtitle
    if subtitle:
        ax.text(x + 1.2, y + h - 3.0, subtitle, color=C_TEXT_MUTED, fontsize=9.5, style='italic', zorder=5)

    # Bullet items
    curr_y = y + h - 4.8
    for item in items:
        ax.text(x + 1.5, curr_y, item, color=C_TEXT_SUB, fontsize=9, zorder=5)
        curr_y -= 1.8

def draw_arrow(ax, start, end, label=None, color='#64748b'):
    ax.annotate(
        '', xy=end, xytext=start,
        arrowprops=dict(facecolor=color, edgecolor=color, width=2.5, headwidth=9, headlength=10, shrink=0.05),
        zorder=6
    )
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2 + 1.2
        ax.text(mid_x, mid_y, label, color='#38bdf8', fontsize=8.5, fontweight='bold', ha='center',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='#0b0f19', edgecolor='none', alpha=0.9), zorder=7)

# --- 1. TITLE & BANNER ---
ax.text(50, 96.5, "MAHA JAL KHOJ : DUAL-HEAD MACHINE LEARNING ARCHITECTURE",
        color='#38bdf8', fontsize=20, fontweight='heavy', ha='center')
ax.text(50, 94.0, "End-to-End Spatially-Weighted Machine Learning Pipeline for Groundwater Level Forecasting & Alert Detection",
        color=C_TEXT_MUTED, fontsize=11, ha='center')

# Horizontal divider line under title
ax.plot([4, 96], [92.2, 92.2], color='#1e293b', lw=1.5)

# --- 2. ROW 1: DATA INGESTION -> PREPROCESSING -> FEATURE ENGINEERING ---
# Card 1: Raw Telemetry Stream
draw_card(
    ax, x=4, y=69, w=26, h=21,
    title="1. RAW TELEMETRY INPUTS",
    subtitle="IoT DWLR Hydrogeological Stream",
    items=[
        "• 218,791 observations across Maharashtra",
        "• 1,016 Piezometer / Borewell Stations",
        "• 34 Districts & 304 Sub-districts (Tehsils)",
        "• 6-Hourly Interval (00:00, 06:00, 12:00, 18:00)",
        "• Station Coordinates (Latitude, Longitude)",
        "• Ground Elevation (RL_MSL in meters)",
        "• Raw Sensor Level (Telemetry Meter)"
    ],
    border_color=C_BORDER_INPUT,
    badge="STREAM"
)

# Card 2: Cleaning & Anomaly Isolation
draw_card(
    ax, x=36, y=69, w=27, h=21,
    title="2. DATA CLEANING & QA",
    subtitle="Anomaly Filtering & Standardization",
    items=[
        "• Dummy Code Filter: 9,222 placeholder 1.000m",
        "  disconnected probe logs eliminated",
        "• Physical Outlier Clip: (0m <= Depth <= 60m)",
        "  filters telemetry glitch spikes (< -60m)",
        "• Sign Inversion & Normalization:",
        "  Standardizes negative telemetry into positive",
        "  Depth Below Ground Level (Depth_mbgl)",
        "• 204,450 Verified Clean Records Retained"
    ],
    border_color=C_BORDER_PREP,
    badge="ETL CLEAN"
)

# Card 3: Feature Engineering Engine
draw_card(
    ax, x=69, y=69, w=27, h=21,
    title="3. FEATURE ENGINEERING",
    subtitle="12 Multi-Dimensional Input Features",
    items=[
        "• Spatial: Latitude, Longitude, RL_MSL",
        "• Administrative: District Frequency Encoding",
        "• Cyclical Seasonality: Sin & Cos (DayOfYear)",
        "  encodes circular 365-day repeating cycle",
        "• Diurnal & Seasonal: Month & Observation Hour",
        "• Hydro Lag-1: Depth recorded 6 hours prior",
        "• Hydro Lag-4: Depth recorded 24 hours prior",
        "• Rolling 7-Day Trend: 28-observation mean",
        "• Velocity: 24h Rate of Depletion (Lag1 - Lag4)"
    ],
    border_color=C_BORDER_FEAT,
    badge="12 FEATURES"
)

# Arrows between Row 1
draw_arrow(ax, (30.5, 79.5), (35.5, 79.5), "Clean Stream")
draw_arrow(ax, (63.5, 79.5), (68.5, 79.5), "Transform")

# Down arrow from Feature Engineering to Spatial Density Weighting
draw_arrow(ax, (82.5, 69.0), (82.5, 59.5), "Feature Vector X")

# --- 3. ROW 2: SPATIAL DENSITY WEIGHTING ---
draw_card(
    ax, x=18, y=43, w=64, h=16,
    title="4. INVERSE SPATIAL DENSITY BALANCING LAYER (Weighting Formulation)",
    subtitle="Eliminates Clustered Sampling Bias between Dense (Sangli: 92) and Sparse (Dhule: 4) Districts",
    items=[
        "• Problem Identified: Dense districts have up to 23x more telemetry points than sparse districts.",
        "• Formulation: Weight W_i = 1 / (N_district_stations), normalized such that mean(W) = 1.0",
        "• Sample Weight Scaling: W_min = 0.397 (Sangli clusters)  ◄───►  W_max = 8.942 (Dhule/Hingoli sparse)",
        "• Loss Function Integration: Directly passed into XGBoost training via sample_weight=sample_weights",
        "• Result: Sparse districts maintain 87% - 99% accuracy; Sangli/Nashik/Amravati clusters do not dominate gradients."
    ],
    border_color=C_BORDER_WEIGHT,
    badge="SPATIAL FAIRNESS"
)

# Connect Row 1 to Spatial Weighting, then split down into Dual-Head Models
draw_arrow(ax, (50, 43), (35, 33), "Weighted Train Set (X, W)", color='#ec4899')
draw_arrow(ax, (50, 43), (65, 33), "Weighted Train Set (X, W)", color='#ec4899')

# --- 4. ROW 3: DUAL-HEAD CORE ENSEMBLE ENGINE ---
# Model Head A: XGBRegressor
draw_card(
    ax, x=4, y=14, w=42, h=19,
    title="5A. CONTINUOUS DEPTH REGRESSOR",
    subtitle="Model: XGBRegressor (150 Estimators, max_depth=6)",
    items=[
        "• Objective: reg:squarederror (Mean Squared Error)",
        "• Training Target: Exact continuous Depth_mbgl (meters)",
        "• Regularization: Learning Rate = 0.08, Subsample = 0.8",
        "• Evaluation Metrics:",
        "  - Mean Absolute Error (MAE): 0.364 meters",
        "  - Root Mean Squared Error (RMSE): 0.612 meters",
        "  - Coefficient of Determination (R²): 0.9920",
        "• Output: Exact predicted depth below ground surface"
    ],
    border_color=C_BORDER_MODEL,
    badge="REGRESSOR"
)

# Model Head B: XGBClassifier
draw_card(
    ax, x=54, y=14, w=42, h=19,
    title="5B. MULTI-CLASS ALERT CLASSIFIER",
    subtitle="Model: XGBClassifier (150 Estimators x 5 Classes)",
    items=[
        "• Objective: multi:softprob (Multi-Class Cross-Entropy)",
        "• Training Target: 5 CGWB Alert Risk Categories",
        "• Class Probabilities: Softmax P(C_i) = e^(z_i) / Σ e^(z_k)",
        "• Evaluation Metrics:",
        "  - Overall Classification Accuracy: 96.71%",
        "  - Weighted F1-Score: 0.9671 | Macro F1: 0.9592",
        "  - Sparse District Accuracy: Dhule 87.1%, Washim 99.3%",
        "• Output: Discrete Risk Level + Model Confidence %"
    ],
    border_color=C_BORDER_MODEL,
    badge="CLASSIFIER"
)

# --- 5. BOTTOM ROW: OUTPUTS & RECURSIVE FORECASTING MODULE ---
draw_card(
    ax, x=4, y=1.5, w=92, h=10.5,
    title="6. INFERENCE, RECURSIVE 10-MONTH PROJECTIONS & SERVING LAYER",
    subtitle="Real-Time FastAPI Backend -> Interactive Command Center & Live Alerts",
    items=[
        "• Continuous Depth Output: Returns exact predicted depth (e.g. 13.14 mbgl) with sub-meter precision.",
        "• Alert Categorization: [Flood Risk <= 2m] | [Safe 2-5m] | [Normal 5-10m] | [Mod Drought 10-15m] | [Severe Drought > 15m]",
        "• Recursive 10-Month AI Forecaster: Advances week-by-week simulating Southwest Monsoon recharge & summer depletion through March 2027.",
        "• Production Deployment: Served via FastAPI REST API (/api/summary, /api/critical-alerts, /api/stations, /api/predict)."
    ],
    border_color=C_BORDER_OUT,
    badge="DECISION SUPPORT"
)

# Final arrows down to Output
draw_arrow(ax, (25, 14), (25, 12), "Depth Float", color='#10b981')
draw_arrow(ax, (75, 14), (75, 12), "Class & Prob", color='#10b981')

plt.tight_layout()
plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()

print(f"High-resolution architecture diagram successfully generated at: {output_path}")
