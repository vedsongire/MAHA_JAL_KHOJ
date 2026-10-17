import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("notebook", exist_ok=True)
output_path = "notebook/ml_model_architecture.png"

# Setup high-resolution figure with modern, clean dark aesthetic
fig, ax = plt.subplots(figsize=(24, 13), dpi=300)
fig.patch.set_facecolor('#090d16')
ax.set_facecolor('#090d16')

# Coordinate system: 0 to 100 on X, 0 to 55 on Y
ax.set_xlim(0, 100)
ax.set_ylim(0, 55)
ax.axis('off')

# Color Palette
C_TITLE = '#38bdf8'       # Sky Blue
C_SUBTITLE = '#94a3b8'    # Slate Gray
C_BG_CARD = '#111827'     # Deep Navy Card
C_BORDER_S1 = '#0ea5e9'   # Ocean Blue (Stage 1)
C_BORDER_S2 = '#818cf8'   # Indigo (Stage 2)
C_BORDER_REG = '#10b981'  # Emerald (Regressor)
C_BORDER_CLS = '#f59e0b'  # Amber (Classifier)
C_BORDER_S4 = '#f43f5e'   # Rose / Coral (Serving)
C_TEXT_WHITE = '#ffffff'
C_TEXT_LIGHT = '#e2e8f0'
C_TEXT_MUTED = '#94a3b8'

def draw_card(ax, x, y, w, h, title, subtitle, sections, border_color, stage_badge=None, metric_chips=None):
    # Card Background with Subtle Shadow
    shadow = patches.FancyBboxPatch(
        (x + 0.3, y - 0.3), w, h,
        boxstyle="round,pad=0.4,rounding_size=1.0",
        facecolor='#030712', edgecolor='none', alpha=0.7, zorder=2
    )
    ax.add_patch(shadow)

    card = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.4,rounding_size=1.0",
        facecolor=C_BG_CARD, edgecolor=border_color, linewidth=2.0, zorder=3
    )
    ax.add_patch(card)

    # Top Header Accent Ribbon
    accent = patches.FancyBboxPatch(
        (x + 0.2, y + h - 2.0), w - 0.4, 1.8,
        boxstyle="round,pad=0.15,rounding_size=0.5",
        facecolor=border_color, edgecolor='none', alpha=0.18, zorder=4
    )
    ax.add_patch(accent)

    # Stage Badge (if any)
    if stage_badge:
        ax.text(
            x + 1.2, y + h - 1.1, stage_badge,
            color='#ffffff', fontsize=8.5, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.25', facecolor=border_color, edgecolor='none'),
            zorder=6, va='center'
        )
        title_x = x + 1.2 + (len(stage_badge) * 0.45) + 1.1
    else:
        title_x = x + 1.2

    # Title
    ax.text(title_x, y + h - 1.1, title, color=C_TEXT_WHITE, fontsize=12.5, fontweight='bold', zorder=6, va='center')

    # Subtitle
    if subtitle:
        ax.text(x + 1.2, y + h - 3.2, subtitle, color=border_color, fontsize=9.5, fontweight='bold', zorder=6)

    # Sectional text rendering (heading + bullet items)
    curr_y = y + h - 5.0
    for sec_header, sec_items in sections:
        if sec_header:
            ax.text(x + 1.2, curr_y, sec_header, color=border_color, fontsize=9.5, fontweight='bold', zorder=6)
            curr_y -= 1.65
        for item in sec_items:
            ax.text(x + 1.4, curr_y, item, color=C_TEXT_LIGHT, fontsize=9.0, zorder=6)
            curr_y -= 1.50
        curr_y -= 0.6  # Gap between sections

    # Bottom Metric / Tech Chips
    if metric_chips:
        chip_x = x + 1.2
        chip_y = y + 1.6
        for chip_text, chip_color, chip_bg in metric_chips:
            chip_box = dict(boxstyle='round,pad=0.3', facecolor=chip_bg, edgecolor=chip_color, lw=1.2)
            ax.text(chip_x, chip_y, chip_text, color=chip_color, fontsize=8.5, fontweight='bold', bbox=chip_box, zorder=7)
            chip_x += len(chip_text) * 0.44 + 1.4

def draw_arrow(ax, start, end, label=None, color='#64748b'):
    ax.annotate(
        '', xy=end, xytext=start,
        arrowprops=dict(facecolor=color, edgecolor=color, width=2.2, headwidth=8.5, headlength=9, shrink=0.03),
        zorder=8
    )
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2 + 0.9
        ax.text(
            mid_x, mid_y, label,
            color=color, fontsize=8.2, fontweight='bold', ha='center',
            bbox=dict(boxstyle='round,pad=0.25', facecolor='#090d16', edgecolor=color, alpha=0.95, lw=0.8),
            zorder=9
        )

# ==============================================================================
# 1. HEADER BANNER
# ==============================================================================
ax.text(50, 52.8, "MAHA JAL KHOJ : SPATIALLY-WEIGHTED DUAL-HEAD ML ARCHITECTURE",
        color='#38bdf8', fontsize=19, fontweight='bold', ha='center')
ax.text(50, 50.8, "End-to-End Pipeline: Telemetry Ingestion -> Anomaly QA -> Spatial Balancing -> Dual-Head XGBoost -> Seasonal Forecaster",
        color=C_SUBTITLE, fontsize=10.5, ha='center')

# Subtle divider line
ax.plot([4, 96], [49.5, 49.5], color='#1e293b', lw=1.5, zorder=1)

# ==============================================================================
# 2. STAGE 1: INGESTION & DATA CLEANING
# ==============================================================================
draw_card(
    ax, x=4, y=6.5, w=19.5, h=41,
    title="Data Ingestion & QA",
    subtitle="IoT DWLR Hydrogeological Stream",
    stage_badge="STAGE 1",
    sections=[
        ("Telemetry Network Scale:", [
            "• 1,016 Monitoring Borewells",
            "• 34 Districts & 304 Tehsils",
            "• 218,791 Total Telemetry Records"
        ]),
        ("Sampling Resolution:", [
            "• 6-Hourly Automated Intervals",
            "• (00:00, 06:00, 12:00, 18:00)"
        ]),
        ("Hardware Error QA:", [
            "• 9,222 dummy probe disconnect",
            "  records (exact 1.000m) isolated"
        ]),
        ("Physical Range & Sign QA:", [
            "• Outliers clipped (0m <= depth <= 60m)",
            "• Sign-inverted to true Depth_mbgl"
        ]),
        ("Clean Retained Stream:", [
            "• 204,450 Verified Clean Records"
        ])
    ],
    border_color=C_BORDER_S1,
    metric_chips=[
        ("1,016 DWLRs", '#38bdf8', '#0c233c'),
        ("204k Clean Rows", '#38bdf8', '#0c233c')
    ]
)

# Arrow from Stage 1 to Stage 2
draw_arrow(ax, (24.0, 27.0), (27.0, 27.0), "Clean Stream", color=C_BORDER_S1)

# ==============================================================================
# 3. STAGE 2: FEATURE STORE & SPATIAL DENSITY BALANCING
# ==============================================================================
draw_card(
    ax, x=27.5, y=6.5, w=20.5, h=41,
    title="Features & Spatial Layer",
    subtitle="Sampling Bias Mitigation Engine",
    stage_badge="STAGE 2",
    sections=[
        ("12 Multi-Modal Features:", [
            "• Spatial: Latitude, Longitude",
            "• Elevation: Surface RL_MSL (meters)",
            "• Seasonality: Sin & Cos (DayOfYear)",
            "• Diurnal: Month & Observation Hour",
            "• Hydro Lags: Lag-1 (6h), Lag-4 (24h)",
            "• Dynamics: 7d Rolling, 24h Decline"
        ]),
        ("Inverse Spatial Balancing Layer:", [
            "• Problem: Dense Sangli has 92 stations",
            "  while sparse Dhule has only 4 stations",
            "• Weight: W_i = 1 / N_district_stations",
            "• Normalized: Mean(W) = 1.0",
            "• Gradient Scaling: 0.397 to 8.942",
            "• Eliminates regional sampling bias"
        ])
    ],
    border_color=C_BORDER_S2,
    metric_chips=[
        ("12 Features", '#818cf8', '#1e1b4b'),
        ("Bias Mitigated", '#818cf8', '#1e1b4b')
    ]
)

# Arrows from Stage 2 to Dual Heads (Split Top & Bottom)
draw_arrow(ax, (48.5, 37.0), (52.5, 37.0), "Features + W", color=C_BORDER_REG)
draw_arrow(ax, (48.5, 17.0), (52.5, 17.0), "Features + W", color=C_BORDER_CLS)

# ==============================================================================
# 4. STAGE 3: DUAL-HEAD MACHINE LEARNING CORE
# ==============================================================================
# 3A: Continuous Depth Regressor (Top)
draw_card(
    ax, x=53, y=27.5, w=22.5, h=20,
    title="XGBRegressor (Depth)",
    subtitle="Continuous Aquifer Level Estimator",
    stage_badge="HEAD A",
    sections=[
        ("Model Configuration:", [
            "• Target: Exact Water Depth (mbgl)",
            "• 150 Trees, max_depth = 6, lr = 0.08"
        ]),
        ("Validated Test Performance:", [
            "• Mean Absolute Error (MAE): 0.364 m",
            "• Root Mean Sq. Error (RMSE): 0.612 m",
            "• Coeff. of Determination (R²): 0.9920",
            "• Output: Exact predicted depth below surface"
        ])
    ],
    border_color=C_BORDER_REG,
    metric_chips=[
        ("MAE: 0.36m", '#10b981', '#064e3b'),
        ("R²: 0.9920", '#10b981', '#064e3b')
    ]
)

# 3B: Multi-Class Alert Classifier (Bottom)
draw_card(
    ax, x=53, y=6.5, w=22.5, h=20,
    title="XGBClassifier (Alerts)",
    subtitle="CGWB Multi-Class Risk Classifier",
    stage_badge="HEAD B",
    sections=[
        ("Model Configuration:", [
            "• Target: 5 CGWB Alert Categories",
            "  (Flood <=2m, Safe 2-5m, Normal 5-10m,",
            "   Mod Drought 10-15m, Severe Drought >15m)"
        ]),
        ("Validated Test Performance:", [
            "• Overall Accuracy: 96.71% | Weighted F1: 0.967",
            "• Sparse Districts Accuracy: 87.1% - 99.3%",
            "• Output: Risk Tier + Softmax Probability"
        ])
    ],
    border_color=C_BORDER_CLS,
    metric_chips=[
        ("Acc: 96.7%", '#fbbf24', '#451a03'),
        ("F1: 0.967", '#fbbf24', '#451a03')
    ]
)

# Arrows from Dual Heads to Stage 4 (Merge)
draw_arrow(ax, (76.0, 37.0), (79.5, 31.0), "Predicted Depth", color=C_BORDER_REG)
draw_arrow(ax, (76.0, 17.0), (79.5, 23.0), "Risk Tier + Prob", color=C_BORDER_CLS)

# ==============================================================================
# 5. STAGE 4: SERVING & RECURSIVE SEASONAL FORECASTER
# ==============================================================================
draw_card(
    ax, x=80, y=6.5, w=16, h=41,
    title="Serving & GIS UI",
    subtitle="Operational Decision Support",
    stage_badge="STAGE 4",
    sections=[
        ("10-Month Forecaster:", [
            "• 43-week recursive engine",
            "• Simulates monsoon recharge",
            "  & summer drawdown",
            "• Horizon: June 2026 - Mar 2027"
        ]),
        ("FastAPI REST Endpoints:", [
            "• Sub-10ms response latency",
            "• /api/summary",
            "• /api/stations",
            "• /api/critical-alerts",
            "• /api/predict"
        ]),
        ("GIS Command Center:", [
            "• Leaflet Dark Canvas GIS",
            "• Dynamic Station Hydrographs",
            "• Pinned Critical Alerts Ticker",
            "• Oct 2026 Current State Toggle"
        ])
    ],
    border_color=C_BORDER_S4,
    metric_chips=[
        ("FastAPI", '#f43f5e', '#4c0519'),
        ("GIS Center", '#f43f5e', '#4c0519')
    ]
)

# ==============================================================================
# 6. SAVE HIGH-RESOLUTION FIGURE
# ==============================================================================
plt.tight_layout()
plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
plt.close()

print(f"Clean, modern architecture diagram successfully generated at: {output_path}")
