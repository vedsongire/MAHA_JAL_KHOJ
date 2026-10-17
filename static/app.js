// MAHA JAL KHOJ - Frontend Application Logic

let map;
let markerLayerGroup;
let allStationsData = [];
let criticalAlertsData = { critical_drought_places: [], critical_flood_places: [] };
let activeAlertTab = 'drought';
let stationChartInstance = null;
let currentSelectedStation = null;

const COLOR_MAP = {
    "Flood / Waterlogging Risk": "#0284c7",       // Ocean Blue
    "Safe / High Water Table": "#06b6d4",        // Cyan
    "Normal Range": "#10b981",                   // Green
    "Moderate Drought Alert": "#f59e0b",         // Amber
    "Severe Drought Alert": "#ef4444"            // Crimson Red
};

let currentTimelineMode = 'current'; // Default to CURRENT October 2026 water level!

document.addEventListener("DOMContentLoaded", () => {
    initMap();
    fetchSummary();
    fetchCriticalAlerts();
    fetchAllStations();
    setupEventListeners();
});

function setTimelineMode(mode) {
    currentTimelineMode = mode;
    const btnCur = document.getElementById('btn-mode-current');
    const btnHist = document.getElementById('btn-mode-historical');
    if (btnCur && btnHist) {
        btnCur.className = mode === 'current' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-secondary';
        btnHist.className = mode === 'historical' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-secondary';
    }
    fetchSummary();
    fetchCriticalAlerts();
    fetchAllStations();
}

// --- STEP 1: INITIALIZE MAP CENTERED ON INDIA ---
function initMap() {
    // Initial coordinates centered on India (lat: 22.0, lng: 79.0, zoom 5)
    map = L.map('india-map', {
        zoomControl: false,
        attributionControl: false
    }).setView([22.0, 79.0], 5);

    // Zoom control in bottom left
    L.control.zoom({ position: 'bottomleft' }).addTo(map);

    // 1. High-contrast Dark Command Map (ESRI Dark Canvas - 100% free, no API key, crystal-clear India borders)
    const esriDarkBase = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16
    });
    const esriDarkLabels = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 16
    });
    const darkLayerGroup = L.layerGroup([esriDarkBase, esriDarkLabels]).addTo(map);

    // 2. OpenStreetMap Standard (Full topographical India map with roads, rivers & states)
    const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap'
    });

    // 3. Satellite Imagery Map
    const satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 18,
        attribution: 'Esri World Imagery'
    });

    // Layer Switcher in bottom left above zoom
    const baseMaps = {
        "🌙 Dark Command Map": darkLayerGroup,
        "🗺️ OpenStreetMap": osmLayer,
        "🛰️ Satellite Imagery": satelliteLayer
    };
    L.control.layers(baseMaps, null, { position: 'bottomleft', collapsed: true }).addTo(map);

    // Marker layer group
    markerLayerGroup = L.layerGroup().addTo(map);

    // Add Maharashtra highlighting boundary box for spatial context
    const mhBounds = [[15.6, 72.6], [22.1, 80.9]];
    L.rectangle(mhBounds, {
        color: "#06b6d4",
        weight: 1.5,
        dashArray: "4, 6",
        fillColor: "#06b6d4",
        fillOpacity: 0.03
    }).addTo(map);
}

// --- STEP 2: FETCH SUMMARY STATS ---
async function fetchSummary() {
    try {
        const res = await fetch(`/api/summary?mode=${currentTimelineMode}`);
        const data = await res.json();

        document.getElementById('metric-stations').textContent = data.total_stations.toLocaleString();
        document.getElementById('metric-depth').textContent = `${data.avg_depth_mbgl} mbgl`;
        document.getElementById('metric-drought').textContent = data.severe_drought_count.toLocaleString();
        document.getElementById('metric-flood').textContent = data.flood_risk_count.toLocaleString();

        if (data.model_metrics && data.model_metrics.classification_accuracy) {
            const acc = (data.model_metrics.classification_accuracy * 100).toFixed(1);
            document.getElementById('metric-ml').textContent = `${acc}% Acc (MAE: ${data.model_metrics.regression_mae.toFixed(2)}m)`;
        }
    } catch (e) {
        console.error("Failed to load summary stats:", e);
    }
}

// --- STEP 3: FETCH AND POPULATE CRITICAL ALERTS HUD (TOP-RIGHT) ---
async function fetchCriticalAlerts() {
    try {
        const res = await fetch(`/api/critical-alerts?mode=${currentTimelineMode}`);
        criticalAlertsData = await res.json();

        document.getElementById('drought-count').textContent = criticalAlertsData.total_drought_critical;
        document.getElementById('flood-count').textContent = criticalAlertsData.total_flood_critical;

        renderCriticalAlerts();
    } catch (e) {
        console.error("Failed to load critical alerts:", e);
    }
}

function switchAlertTab(tab) {
    activeAlertTab = tab;
    document.getElementById('tab-drought').classList.toggle('active', tab === 'drought');
    document.getElementById('tab-flood').classList.toggle('active', tab === 'flood');
    renderCriticalAlerts();
}

function renderCriticalAlerts() {
    const container = document.getElementById('alert-list');
    container.innerHTML = '';

    const list = activeAlertTab === 'drought' 
        ? criticalAlertsData.critical_drought_places 
        : criticalAlertsData.critical_flood_places;

    if (!list || list.length === 0) {
        container.innerHTML = `<div style="padding: 20px; text-align: center; color: #64748b;">No active ${activeAlertTab} alerts in this period.</div>`;
        return;
    }

    list.forEach(item => {
        const card = document.createElement('div');
        const isDrought = activeAlertTab === 'drought';
        card.className = `alert-card ${isDrought ? 'drought-card' : 'flood-card'}`;

        card.innerHTML = `
            <div class="alert-info">
                <h4><i class="fa-solid fa-location-dot" style="color: ${isDrought ? '#ef4444' : '#0284c7'}; margin-right: 5px;"></i>${item.station}</h4>
                <div class="alert-sub">${item.district} • ${item.tehsil || 'Tehsil'}</div>
            </div>
            <div class="alert-val-box">
                <div class="alert-depth ${isDrought ? 'drought-depth' : 'flood-depth'}">${item.depth_mbgl.toFixed(1)} m</div>
                <span class="alert-badge ${isDrought ? 'badge-drought' : 'badge-flood'}">
                    ${isDrought ? 'CRITICAL DEPLETION' : 'WATERLOGGING'}
                </span>
            </div>
        `;

        card.onclick = () => {
            flyToStation(item.latitude, item.longitude, item.station);
        };

        container.appendChild(card);
    });
}

// --- STEP 4: FETCH ALL STATIONS & RENDER MAP MARKERS ---
async function fetchAllStations() {
    try {
        const res = await fetch(`/api/stations?mode=${currentTimelineMode}`);
        const data = await res.json();
        allStationsData = data.stations;

        populateDistrictDropdown();
        renderMapMarkers();
    } catch (e) {
        console.error("Failed to fetch stations:", e);
    }
}

function populateDistrictDropdown() {
    const select = document.getElementById('district-select');
    const districts = [...new Set(allStationsData.map(s => s.district))].sort();

    districts.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d;
        opt.textContent = d;
        select.appendChild(opt);
    });
}

function renderMapMarkers() {
    markerLayerGroup.clearLayers();

    const selectedDistrict = document.getElementById('district-select').value;
    const checkedAlerts = Array.from(document.querySelectorAll('.checkbox-group input:checked')).map(cb => cb.value);

    let visibleCount = 0;

    allStationsData.forEach(st => {
        if (selectedDistrict !== "All" && st.district !== selectedDistrict) return;
        if (!checkedAlerts.includes(st.alert)) return;

        visibleCount++;
        const color = COLOR_MAP[st.alert] || '#94a3b8';
        const isCritical = st.alert === "Severe Drought Alert" || st.alert === "Flood / Waterlogging Risk";

        const circleMarker = L.circleMarker([st.lat, st.lng], {
            radius: isCritical ? 6 : 4.5,
            fillColor: color,
            color: isCritical ? '#ffffff' : color,
            weight: isCritical ? 1.5 : 0.8,
            opacity: 1,
            fillOpacity: 0.85
        });

        // Tooltip
        circleMarker.bindTooltip(`
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 11px;">
                <b>${st.station}</b> (${st.district})<br>
                Depth: <b style="color:${color}; font-size: 13px;">${st.depth} mbgl</b><br>
                Status: <b>${st.alert}</b>
            </div>
        `, { sticky: true });

        // Click to open station drawer
        circleMarker.on('click', () => {
            openStationDrawer(st);
        });

        circleMarker.addTo(markerLayerGroup);
    });

    document.getElementById('visible-station-count').textContent = `${visibleCount} Stations`;
}

// --- STEP 5: CAMERA FLY TO & ZOOM ---
function flyToStation(lat, lng, stationName) {
    map.flyTo([lat, lng], 13, {
        duration: 1.5,
        easeLinearity: 0.25
    });

    const target = allStationsData.find(s => s.station === stationName);
    if (target) {
        openStationDrawer(target);
    }
}

let currentStationHistory = [];
let currentStationForecast = null;
let currentChartMode = 'past';

// --- STEP 6: STATION HYDROGRAPH DRAWER & CHART.JS ---
async function openStationDrawer(st) {
    currentSelectedStation = st;
    currentChartMode = 'past';
    currentStationForecast = null;
    updateChartToggleButtons();

    const drawer = document.getElementById('station-drawer');
    drawer.style.display = 'block';

    document.getElementById('drawer-station-name').textContent = st.station;
    document.getElementById('drawer-station-meta').textContent = `${st.district} District • ${st.tehsil || '-'} • Coordinates: [${st.lat.toFixed(3)}, ${st.lng.toFixed(3)}]`;
    document.getElementById('drawer-depth').textContent = `${st.depth.toFixed(2)} mbgl`;
    document.getElementById('drawer-rl').textContent = st.rl_msl ? `${st.rl_msl} m MSL` : 'N/A';
    document.getElementById('drawer-time').textContent = st.last_updated || 'Telemetry Active';

    const badge = document.getElementById('drawer-status-badge');
    badge.textContent = st.alert;
    badge.style.backgroundColor = `${COLOR_MAP[st.alert]}33`;
    badge.style.color = COLOR_MAP[st.alert];
    badge.style.border = `1px solid ${COLOR_MAP[st.alert]}`;

    // Reset ML result view
    document.getElementById('ml-result-grid').style.display = 'none';

    // Fetch past history
    try {
        const res = await fetch(`/api/station/${encodeURIComponent(st.station)}/history`);
        const historyData = await res.json();
        currentStationHistory = historyData.history;
        renderHydrograph(currentStationHistory);
    } catch (e) {
        console.error("Failed to load station history:", e);
    }
}

function updateChartToggleButtons() {
    const btnPast = document.getElementById('btn-chart-past');
    const btnFuture = document.getElementById('btn-chart-future');
    if (btnPast && btnFuture) {
        btnPast.className = currentChartMode === 'past' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-secondary';
        btnFuture.className = currentChartMode === 'future' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-secondary';
    }
}

async function switchChartMode(mode) {
    currentChartMode = mode;
    updateChartToggleButtons();

    if (mode === 'past') {
        document.getElementById('chart-sub-label').textContent = "Recorded Water Table Depth (Jan - May 2026)";
        renderHydrograph(currentStationHistory);
    } else {
        document.getElementById('chart-sub-label').textContent = "AI 10-Month Forward Projected Trajectory (June 2026 - March 2027)";
        if (!currentStationForecast) {
            try {
                const res = await fetch(`/api/station/${encodeURIComponent(currentSelectedStation.station)}/forecast-10-months`);
                currentStationForecast = await res.json();
            } catch (e) {
                console.error("Failed to load 10-month forecast:", e);
                return;
            }
        }
        renderForecastChart(currentStationForecast.projections);
    }
}

function closeDrawer() {
    document.getElementById('station-drawer').style.display = 'none';
}

function renderHydrograph(history) {
    const ctx = document.getElementById('stationChart').getContext('2d');
    const labels = history.map(h => h.time.split(' ')[0]);
    const depths = history.map(h => h.depth);

    const minD = Math.min(...depths);
    const maxD = Math.max(...depths);
    document.getElementById('drawer-range').textContent = `${minD.toFixed(1)} to ${maxD.toFixed(1)} m`;

    if (stationChartInstance) {
        stationChartInstance.destroy();
    }

    stationChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Recorded Depth (mbgl)',
                data: depths,
                borderColor: '#06b6d4',
                backgroundColor: 'rgba(6, 182, 212, 0.12)',
                borderWidth: 2,
                pointRadius: depths.length > 80 ? 0 : 2,
                fill: true,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    reverse: true,
                    title: { display: true, text: 'Depth (mbgl - Deeper is Lower)', color: '#94a3b8', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', maxTicksLimit: 8 }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: (ctx) => `Recorded Depth: ${ctx.parsed.y} meters below surface`
                    }
                }
            }
        }
    });
}

function renderForecastChart(projections) {
    const ctx = document.getElementById('stationChart').getContext('2d');
    const labels = projections.map(p => p.date);
    const depths = projections.map(p => p.predicted_depth);

    if (stationChartInstance) {
        stationChartInstance.destroy();
    }

    stationChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: '10-Month AI Projected Depth (mbgl)',
                data: depths,
                borderColor: '#a855f7',
                backgroundColor: 'rgba(168, 85, 247, 0.15)',
                borderWidth: 2.5,
                pointRadius: 3,
                pointHoverRadius: 6,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    reverse: true,
                    title: { display: true, text: 'Projected Depth (mbgl - Deeper is Lower)', color: '#a855f7', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', maxTicksLimit: 9 }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: (ctx) => {
                            const p = projections[ctx.dataIndex];
                            return `Depth: ${p.predicted_depth} m | ${p.alert_status} [${p.season_phase}]`;
                        }
                    }
                }
            }
        }
    });
}

// --- STEP 7: ML PREDICTION TRIGGER ---
async function runMLPrediction() {
    if (!currentSelectedStation) return;
    const btn = document.getElementById('btn-run-ml');
    btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Predicting...`;
    btn.disabled = true;

    try {
        const payload = {
            station_name: currentSelectedStation.station,
            district: currentSelectedStation.district,
            latitude: currentSelectedStation.lat,
            longitude: currentSelectedStation.lng,
            rl_msl: currentSelectedStation.rl_msl || 350.0,
            current_depth: currentSelectedStation.depth,
            lag_4_depth: currentSelectedStation.depth * 0.98,
            rolling_7d_mean: currentSelectedStation.depth,
            month: 5,
            day_of_year: 140
        };

        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const pred = await res.json();

        document.getElementById('ml-pred-depth').textContent = `${pred.predicted_depth_mbgl} mbgl`;
        document.getElementById('ml-pred-alert').textContent = pred.predicted_alert;
        document.getElementById('ml-pred-alert').style.color = COLOR_MAP[pred.predicted_alert] || '#fff';
        document.getElementById('ml-confidence').textContent = `${pred.model_confidence}%`;

        document.getElementById('ml-result-grid').style.display = 'grid';
    } catch (e) {
        console.error("Prediction failed:", e);
        alert("ML Prediction error. Please ensure server is running.");
    } finally {
        btn.innerHTML = `<i class="fa-solid fa-bolt"></i> Run Forecast`;
        btn.disabled = false;
    }
}

// --- STEP 8: BUTTON LISTENERS & CONTROLS ---
function setupEventListeners() {
    // Whole India View
    document.getElementById('btn-india-view').addEventListener('click', () => {
        map.flyTo([21.8, 79.5], 5, { duration: 1.5 });
    });

    // Focus Maharashtra View
    document.getElementById('btn-mh-view').addEventListener('click', () => {
        map.flyToBounds([[15.6, 72.6], [22.1, 80.9]], { duration: 1.5 });
    });

    // District filter dropdown change
    document.getElementById('district-select').addEventListener('change', () => {
        renderMapMarkers();
        const d = document.getElementById('district-select').value;
        if (d !== "All") {
            const districtStations = allStationsData.filter(s => s.district === d);
            if (districtStations.length > 0) {
                const lats = districtStations.map(s => s.lat);
                const lngs = districtStations.map(s => s.lng);
                map.flyToBounds([
                    [Math.min(...lats), Math.min(...lngs)],
                    [Math.max(...lats), Math.max(...lngs)]
                ], { padding: [50, 50], duration: 1.2 });
            }
        }
    });

    // Checkboxes filter change
    document.querySelectorAll('.checkbox-group input').forEach(cb => {
        cb.addEventListener('change', () => {
            renderMapMarkers();
        });
    });
}
