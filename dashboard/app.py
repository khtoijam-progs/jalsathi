# dashboard/app.py
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Page Config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JalSaathi — Water Management",
    page_icon="💧",
    layout="wide"
)
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>

<style>
  body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #e9faff, #ffffff);
  }

  /* Semi-governmental banner */
  .gov-banner {
    background: linear-gradient(135deg, #071a33, #0b3a66);
    color: white;
    border-radius: 20px;
    padding: 24px 28px;
    text-align: center;
    box-shadow: 0 10px 36px rgba(56, 189, 248, 0.30);
    margin-bottom: 14px;
  }

  /* Glassmorphism cards */
  .glass-card {
    backdrop-filter: blur(14px);
    background: rgba(255, 255, 255, 0.14);
    border-radius: 20px;
    box-shadow: 0 8px 28px rgba(56, 189, 248, 0.25);
    padding: 20px;
    margin: 8px auto;
    transition: transform 0.2s ease-in-out;
  }
  .glass-card:hover {
    transform: translateY(-4px);
  }

  /* Typography */
  h1, h2, h3 {
    font-family: 'Playfair Display', serif;
  }
  p, span, div {
    font-family: 'Inter', sans-serif;
  }
  .metric-label {
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 600;
  }
</style>
""", unsafe_allow_html=True)

# ── Global Theme ──────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;800&family=Inter:wght@300;400;500;600&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
  /* ── Root Variables ─────────────────────────────────────────── */
  :root {
    --navy:       #071a33;
    --navy-mid:   #0b3a66;
    --mint:       #2dd4bf;
    --sky:        #38bdf8;
    --amber:      #f59e0b;
    --amber-light:#fde68a;
    --ice:        #e6f7ff;
    --ice-mid:    #bfe9ff;
    --glass-bg:   rgba(255,255,255,0.14);
    --glass-border: rgba(56,189,248,0.28);
    --shadow-blue: rgba(56,189,248,0.22);
  }

  /* ── Base Typography ────────────────────────────────────────── */
  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
  }
  h1, h2, h3, .gov-banner h1 {
    font-family: 'Playfair Display', serif !important;
    letter-spacing: 0.01em;
  }
  h4, h5, h6, .section-label {
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600;
  }
  code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
  }

  /* ── Streamlit Overrides ────────────────────────────────────── */
  .stApp {
    background: linear-gradient(160deg, #f0fbff 0%, #eaf2ff 40%, #ffffff 100%) !important;
  }
  section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #041527 0%, #0b3a66 100%) !important;
    backdrop-filter: blur(14px) saturate(180%);
  }
  section[data-testid="stSidebar"] * {
    color: #cfe9ff !important;
  }
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stRadio label {
    color: #9bd0ff !important;
    font-family: 'Source Sans 3', sans-serif !important;
  }

  /* ── Glassmorphism Card ─────────────────────────────────────── */
  .glass-card {
    backdrop-filter: blur(18px) saturate(170%);
    -webkit-backdrop-filter: blur(18px) saturate(170%);
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    box-shadow: 0 10px 38px var(--shadow-blue);
    padding: 22px 22px;
    margin: 6px 0;
    transition: transform 0.25s cubic-bezier(.4,0,.2,1),
                box-shadow 0.25s cubic-bezier(.4,0,.2,1);
  }
  .glass-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 52px rgba(56,189,248,0.40);
  }

  /* ── Government Banner ──────────────────────────────────────── */
  .gov-banner {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 60%, var(--mint) 100%);
    border-radius: 22px;
    padding: 28px 32px;
    text-align: center;
    box-shadow: 0 14px 46px var(--shadow-blue);
    border-bottom: 4px solid var(--amber);
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
  }
  .gov-banner::before {
    content: '';
    position: absolute; inset: 0;
    background:
      radial-gradient(ellipse at 26% 18%, rgba(45,212,191,0.20) 0%, transparent 58%),
      radial-gradient(ellipse at 75% 10%, rgba(56,189,248,0.15) 0%, transparent 55%);
    pointer-events: none;
  }
  .gov-banner h1 {
    color: #ffffff; margin: 0;
    font-size: 2.2rem; font-weight: 700;
    text-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }
  .gov-banner p {
    color: var(--amber-light); margin: 6px 0 0;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 1.05rem; font-weight: 400;
    letter-spacing: 0.03em;
  }

  /* ── Score Cards ────────────────────────────────────────────── */
  .score-card {
    border-radius: 22px;
    padding: 26px 18px;
    text-align: center;
    box-shadow: 0 12px 44px var(--shadow-blue);
    border: 1px solid rgba(56,189,248,0.18);
    backdrop-filter: blur(12px) saturate(160%);
    position: relative;
    overflow: hidden;
    transition: transform 0.25s cubic-bezier(.4,0,.2,1);
  }
  .score-card:hover { transform: translateY(-4px); }
  .score-card .label {
    color: rgba(255,255,255,0.85); margin: 0;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 14px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.06em;
  }
  .score-card .value {
    color: #ffffff; margin: 10px 0 6px;
    font-family: 'Playfair Display', serif;
    font-size: 48px; font-weight: 800;
  }
  .score-card .sub {
    color: rgba(255,255,255,0.7); margin: 0;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
  }

  /* ── Architecture Pill ──────────────────────────────────────── */
  .arch-pill {
    border-radius: 18px;
    padding: 20px 12px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 32px var(--shadow-blue);
    transition: transform 0.2s ease;
    border: 1px solid rgba(56,189,248,0.20);
  }
  .arch-pill:hover { transform: translateY(-3px); }
  .arch-pill h3 { font-family: 'Inter', sans-serif; margin: 0 0 4px; font-size: 28px; }
  .arch-pill b  { font-family: 'Source Sans 3', sans-serif; font-size: 15px; }
  .arch-pill small { font-family: 'Inter', sans-serif; font-size: 12px; opacity: 0.85; }

  /* ── Quality Labels ─────────────────────────────────────────── */
  .quality-badge {
    padding: 14px 16px;
    border-radius: 16px;
    color: white;
    margin-bottom: 8px;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 15px;
    box-shadow: 0 8px 26px var(--shadow-blue);
    border: 1px solid rgba(56,189,248,0.18);
    transition: transform 0.2s ease;
  }
  .quality-badge:hover { transform: translateY(-2px); }
  .quality-badge b { font-family: 'Inter', sans-serif; }

  /* ── Sim Result Card ────────────────────────────────────────── */
  .sim-result {
    border-radius: 22px;
    padding: 28px 22px;
    text-align: center;
    box-shadow: 0 16px 55px var(--shadow-blue);
    margin-bottom: 12px;
    position: relative;
    overflow: hidden;
  }
  .sim-result::after {
    content: ''; position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.10) 0%, transparent 60%);
    pointer-events: none;
  }
  .sim-result h2 {
    color: white; margin: 0;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 1.3rem; font-weight: 600;
  }
  .sim-result .big-num {
    color: white;
    font-family: 'Playfair Display', serif;
    font-size: 68px; font-weight: 800;
    margin: 10px 0 6px;
  }
  .sim-result h3 {
    color: rgba(255,255,255,0.9); margin: 0;
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem; font-weight: 400;
  }

  /* ── Footer ─────────────────────────────────────────────────── */
  .gov-footer {
    text-align: center;
    color: #6b7c93;
    font-family: 'Source Sans 3', sans-serif;
    font-size: 13px;
    padding: 12px 0;
    letter-spacing: 0.02em;
    border-top: 1px solid var(--ice-mid);
    margin-top: 10px;
  }

  /* ── Divider override ───────────────────────────────────────── */
  hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--ice-mid), transparent);
    margin: 14px 0;
  }
</style>
""", unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────────────────────────
page = st.sidebar.radio("🧭 Navigation",
    ["🏠 Dashboard", "🎮 Simulation Mode", "📊 Model Accuracy"],
    index=0
)

# ── Load Data & Models ─────────────────────────────────────────────────────
@st.cache_data
def load_data():
    rain = pd.read_csv("data/rainfall.csv", parse_dates=["date"])
    dam  = pd.read_csv("data/dam_levels.csv", parse_dates=["date"])
    gw   = pd.read_csv("data/groundwater.csv")
    wq   = pd.read_csv("data/water_quality.csv")
    return rain, dam, gw, wq

@st.cache_resource
def load_models():
    with open("models/flood_model.pkl", "rb") as f:
        flood_model = pickle.load(f)
    with open("models/groundwater_model.pkl", "rb") as f:
        gw_model = pickle.load(f)
    with open("models/water_quality_model.pkl", "rb") as f:
        wq_model = pickle.load(f)
    return flood_model, gw_model, wq_model

rain, dam, gw, wq = load_data()
flood_model, gw_model, wq_model = load_models()

DISTRICTS = sorted(rain["district"].unique().tolist())

# ══════════════════════════════════════════════════════════════════════════
# PAGE 1: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════
if page == "🏠 Dashboard":

    st.markdown("""
    <div class="gov-banner">
      <h1>💧 JalSaathi</h1>
      <p>Intelligent Water Resource Management & Flood Prediction System</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ────────────────────────────────────────────────────────────
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Emblem_of_India.svg/100px-Emblem_of_India.svg.png", width=60)
    st.sidebar.title("🔧 Controls")
    selected_district = st.sidebar.selectbox("📍 Select District", DISTRICTS)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**About JalSaathi**") 
    st.sidebar.info("AI-powered platform integrating rainfall, dam, groundwater & water quality data for real-time flood prediction.")

    # ── Filter Data ────────────────────────────────────────────────────────
    rain_d = rain[rain["district"] == selected_district].sort_values("date").copy()
    dam_d  = dam[dam["district"] == selected_district].sort_values("date")
    gw_d   = gw[gw["district"] == selected_district]
    wq_d   = wq[wq["district"] == selected_district]

    # Latest values
    latest_rain = float(rain_d["rainfall_mm"].iloc[-1].item())
    latest_dam  = float(dam_d["reservoir_level_pct"].iloc[-1].item())
    rain_d["rolling_7d"] = rain_d["rainfall_mm"].rolling(7, min_periods=1).sum()
    rolling_7d  = float(rain_d["rolling_7d"].iloc[-1].item())
    latest_gw   = float(gw_d["depth_meters"].iloc[-1].item())

    # Flood prediction
    X_pred = pd.DataFrame([[latest_rain, rolling_7d, latest_dam]],
                           columns=["rainfall_mm", "rolling_7d", "reservoir_level_pct"])
    flood_prob = float(flood_model.predict_proba(X_pred)[0][1].item())

    # Water quality
    wq_counts = wq_d["quality_label"].value_counts()
    dominant_quality = wq_counts.index[0]

    # ── ALERTS BANNER ──────────────────────────────────────────────────────
    alerts = []
    if flood_prob > 0.75:
        alerts.append(f"🚨 **HIGH FLOOD RISK** in {selected_district} — {flood_prob*100:.0f}% probability. Immediate action required!")
    elif flood_prob > 0.45:
        alerts.append(f"⚠️ **MODERATE FLOOD RISK** in {selected_district} — {flood_prob*100:.0f}% probability. Monitor closely.")
    if latest_dam > 88:
        alerts.append(f"⚠️ **DAM OVERFLOW RISK** — Reservoir at {latest_dam:.1f}% capacity!")
    if latest_gw > 20:
        alerts.append(f"📉 **GROUNDWATER DEPLETION** — Water table at {latest_gw:.1f}m depth.")
    if dominant_quality == "Contaminated":
        alerts.append(f"🧪 **WATER QUALITY ALERT** — Contaminated sources detected in {selected_district}!")

    if alerts:
        for alert in alerts:
            st.error(alert)
    else:
        st.success(f"✅ All systems normal in **{selected_district}**. No active alerts.")

    # ── KPI METRICS ────────────────────────────────────────────────────────
    st.markdown("### 📊 Current Status")
    col1, col2, col3, col4 = st.columns(4)

    flood_label = "🔴 HIGH" if flood_prob > 0.7 else "🟠 MEDIUM" if flood_prob > 0.4 else "🟢 LOW"
    col1.metric("🌊 Flood Risk",       flood_label, f"{flood_prob*100:.0f}%")
    col2.metric("🌧 Today's Rainfall", f"{latest_rain:.1f} mm", f"7-day: {rolling_7d:.0f} mm")
    col3.metric("🏞 Reservoir Level",  f"{latest_dam:.1f}%")
    col4.metric("🪨 Groundwater Depth",f"{latest_gw:.1f} m")

    st.markdown("---")

    # ── CHARTS ROW 1 ───────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("🌧 Rainfall — Last 60 Days")
        rain_recent = rain_d.tail(60)
        fig_rain = px.bar(rain_recent, x="date", y="rainfall_mm",
                          color="rainfall_mm",
                          color_continuous_scale="Blues",
                          labels={"rainfall_mm": "Rainfall (mm)", "date": "Date"})
        fig_rain.update_layout(showlegend=False, height=300, margin=dict(t=10))
        st.plotly_chart(fig_rain, use_container_width=True)

    with col_b:
        st.subheader("🏞 Reservoir Level — Last 60 Days")
        dam_recent = dam_d.tail(60)
        fig_dam = px.line(dam_recent, x="date", y="reservoir_level_pct",
                          labels={"reservoir_level_pct": "Level (%)", "date": "Date"},
                          color_discrete_sequence=["#0077b6"])
        fig_dam.add_hline(y=85, line_dash="dash", line_color="red",
                          annotation_text="⚠️ Overflow Threshold")
        fig_dam.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig_dam, use_container_width=True)

    # ── CHARTS ROW 2 ───────────────────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("🪨 Groundwater Depth Trend")
        fig_gw = px.line(gw_d, x="month", y="depth_meters",
                         color="year",
                         labels={"depth_meters": "Depth (m)", "month": "Month"},
                         color_discrete_sequence=["#0077b6", "#f77f00"])
        fig_gw.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig_gw, use_container_width=True)

    with col_d:
        st.subheader("🧪 Water Quality Distribution")
        colors = {"Safe": "#2dc653", "Moderate Risk": "#f77f00", "Contaminated": "#e63946"}
        fig_wq = px.pie(wq_d, names="quality_label",
                        color="quality_label",
                        color_discrete_map=colors,
                        hole=0.4)
        fig_wq.update_layout(height=300, margin=dict(t=10))
        st.plotly_chart(fig_wq, use_container_width=True)

    # ── FLOOD RISK GAUGE ───────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🌊 Flood Risk Gauge")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=flood_prob * 100,
        title={"text": f"Flood Risk — {selected_district}"},
            gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "darkblue"},
            "steps": [
                {"range": [0,  40], "color": "#2dc653"},
                {"range": [40, 70], "color": "#f77f00"},
                {"range": [70,100], "color": "#e63946"},
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 75
            }
        }
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── GIS MAP ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("🗺 GIS Flood Risk Map — Andhra Pradesh")
    if os.path.exists("gis/flood_map.html"):
        with open("gis/flood_map.html", "r", encoding="utf-8") as f:
            map_html = f.read()
        st.components.v1.html(map_html, height=500)
    else:
        st.warning("Map not generated yet. Run `python gis_map.py` first.")

    # ── FOOTER ────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("<div class='gov-footer'>JalSaathi — Built for National Exhibition &nbsp;|&nbsp; Data: IMD, CGWB, India-WRIS</div>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 2: SIMULATION MODE
# ══════════════════════════════════════════════════════════════════════════
elif page == "🎮 Simulation Mode":

    st.markdown("""
    <div class="gov-banner" style="background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 55%, var(--mint) 100%); border-bottom-color: var(--amber);">
      <h1>🎮 Flood Risk Simulator</h1>
      <p>Adjust parameters and see flood risk update in real time</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎛 Adjust Environmental Parameters")
    st.info("💡 Move the sliders to simulate different weather and water conditions. The flood risk will update instantly.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🌧 Rainfall Parameters")
        sim_rainfall = st.slider("Today's Rainfall (mm)",
            min_value=0.0, max_value=150.0, value=10.0, step=0.5,
            help="Daily rainfall in millimeters")
        sim_rolling = st.slider("7-Day Cumulative Rainfall (mm)",
            min_value=0.0, max_value=400.0, value=float(sim_rainfall * 5), step=1.0,
            help="Total rainfall over the past 7 days")
        sim_soil = st.slider("Soil Moisture Index",
            min_value=0.0, max_value=1.0, value=0.4, step=0.05,
            help="0 = completely dry, 1 = fully saturated")

    with col2:
        st.markdown("#### 🏞 Water Infrastructure")
        sim_dam = st.slider("Reservoir Level (%)",
            min_value=0.0, max_value=100.0, value=60.0, step=0.5,
            help="Current dam/reservoir fill percentage")
        sim_gw = st.slider("Groundwater Depth (m)",
            min_value=1.0, max_value=40.0, value=15.0, step=0.5,
            help="Depth to water table in meters")
        sim_district = st.selectbox("📍 Simulating District", DISTRICTS,
            help="Select which district to simulate")

    st.markdown("---")

    # ── Real-time prediction ───────────────────────────────────────────────
    X_sim = pd.DataFrame(
        [[sim_rainfall, sim_rolling, sim_dam]],
        columns=["rainfall_mm", "rolling_7d", "reservoir_level_pct"]
    )
    sim_flood_prob = float(flood_model.predict_proba(X_sim)[0][1].item())

    # Risk level
    if sim_flood_prob > 0.75:
        risk_label = "🔴 CRITICAL — Evacuate Immediately"
        risk_color = "#d62828"
    elif sim_flood_prob > 0.55:
        risk_label = "🟠 HIGH RISK — Issue Warnings"
        risk_color = "#f77f00"
    elif sim_flood_prob > 0.35:
        risk_label = "🟡 MODERATE — Monitor Closely"
        risk_color = "#fcbf49"
    else:
        risk_label = "🟢 LOW RISK — Normal Operations"
        risk_color = "#2dc653"

    # ── Big result display ─────────────────────────────────────────────────
    st.markdown(f"""
    <div class="sim-result" style="background: linear-gradient(135deg, {risk_color}, {risk_color}dd);">
      <h2>Flood Risk for {sim_district}</h2>
      <div class="big-num">{sim_flood_prob*100:.1f}%</div>
      <h3>{risk_label}</h3>
    </div>
    """, unsafe_allow_html=True)

    # ── Metrics row ────────────────────────────────────────────────────────
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🌧 Today's Rain",  f"{sim_rainfall:.1f} mm")
    m2.metric("📅 7-Day Total",   f"{sim_rolling:.0f} mm")
    m3.metric("🏞 Reservoir",     f"{sim_dam:.1f}%")
    m4.metric("🪨 Groundwater",   f"{sim_gw:.1f} m depth")

    # ── Gauge + Stress chart ───────────────────────────────────────────────
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        fig_sim_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=sim_flood_prob * 100,
            title={"text": "Flood Risk %", "font": {"size": 18}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar":  {"color": risk_color},
                "steps": [
                    {"range": [0,  35],  "color": "#d4edda"},
                    {"range": [35, 55],  "color": "#fff3cd"},
                    {"range": [55, 75],  "color": "#ffe5d0"},
                    {"range": [75, 100], "color": "#f8d7da"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 75
                }
            }
        ))
        fig_sim_gauge.update_layout(height=300, margin=dict(t=30, b=0))
        st.plotly_chart(fig_sim_gauge, use_container_width=True)

    with col_g2:
        contrib_data = pd.DataFrame({
            "Factor": ["Today's Rain", "7-Day Rain", "Reservoir Level", "Soil Moisture"],
            "Value":  [
                sim_rainfall / 150 * 100,
                sim_rolling  / 400 * 100,
                sim_dam,
                sim_soil     * 100
            ]
        })
        fig_contrib = px.bar(contrib_data, x="Factor", y="Value",
                             title="Parameter Stress Levels (%)",
                             color="Factor",
                             color_discrete_sequence=["#0077b6", "#023e8a", "#f77f00", "#8ecae6"])
        fig_contrib.update_layout(height=300, showlegend=False,
                                  margin=dict(t=40, b=0), yaxis_range=[0, 100])
        fig_contrib.add_hline(y=75, line_dash="dash", line_color="red",
                              annotation_text="⚠️ Danger Zone")
        st.plotly_chart(fig_contrib, use_container_width=True)

    # ── Recommended Actions ────────────────────────────────────────────────
    st.markdown("### 📋 Recommended Actions")
    if sim_flood_prob > 0.75:
        actions = [
            "🚨 Issue immediate flood evacuation orders for low-lying areas",
            "🚧 Deploy NDRF teams to flood-prone zones",
            "📻 Activate emergency broadcast on All India Radio",
            "🏥 Put district hospitals on emergency alert",
            "🚰 Pre-position drinking water tankers in safe zones",
        ]
    elif sim_flood_prob > 0.55:
        actions = [
            "⚠️ Issue flood watch advisory for vulnerable areas",
            "🏗 Inspect and reinforce river embankments",
            "📱 Send SMS alerts to residents in flood-prone zones",
            "🏫 Identify schools as temporary relief shelters",
            "🌊 Begin controlled release from reservoirs if >85% full",
        ]
    elif sim_flood_prob > 0.35:
        actions = [
            "👁 Increase monitoring frequency at river gauging stations",
            "📊 Brief district collector on current water levels",
            "🔧 Check pump stations and drainage infrastructure",
            "📞 Keep SDRF teams on standby",
        ]
    else:
        actions = [
            "✅ Continue routine monitoring",
            "📈 Log current readings for trend analysis",
            "🌱 Optimal conditions for irrigation scheduling",
            "💧 Consider groundwater recharge initiatives",
        ]
    for action in actions:
        st.markdown(f"- {action}")

    # ── Scenario Presets ───────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ⚡ Quick Scenario Presets")
    st.markdown("*Reference values for real-world conditions — adjust sliders to match:*")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown("**🌧 Heavy Monsoon**\n- Rainfall: 120 mm\n- 7-Day: 350 mm\n- Reservoir: 92%")
    with sc2:
        st.markdown("**☀️ Dry Summer**\n- Rainfall: 0 mm\n- 7-Day: 2 mm\n- Reservoir: 28%")
    with sc3:
        st.markdown("**⚡ Cyclone Scenario**\n- Rainfall: 145 mm\n- 7-Day: 380 mm\n- Reservoir: 95%")
    with sc4:
        st.markdown("**🌦 Normal Monsoon**\n- Rainfall: 25 mm\n- 7-Day: 95 mm\n- Reservoir: 65%")

    st.markdown("---")
    st.markdown("<p style='text-align:center; color:gray'>JalSaathi — Built for National Exhibition | Data: IMD, CGWB, India-WRIS</p>",
                unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# PAGE 3: MODEL ACCURACY 
# ══════════════════════════════════════════════════════════════════════════
elif page == "📊 Model Accuracy":

    st.markdown("""
    <div class="gov-banner" style="background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 55%, var(--mint) 100%); border-bottom-color: var(--amber);">
      <h1>📊 Model Performance</h1>
      <p>ML model accuracy, evaluation metrics & feature importance</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Re-run models to get metrics ───────────────────────────────────────
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import (accuracy_score, confusion_matrix,
                                 classification_report, r2_score,
                                 mean_absolute_error)

    @st.cache_data
    def compute_metrics():
        import pandas as pd
        import numpy as np

        # ── Flood model metrics ────────────────────────────────────────────
        df = pd.read_csv("data/flood_training.csv")
        features = ["rainfall_mm", "rolling_7d", "reservoir_level_pct"]
        X = df[features]
        y = df["flood"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)
        flood_preds = flood_model.predict(X_test)
        flood_acc   = float(accuracy_score(y_test, flood_preds))
        flood_cm    = confusion_matrix(y_test, flood_preds).tolist()
        flood_imp   = flood_model.feature_importances_.tolist()

        # ── Groundwater model metrics ──────────────────────────────────────
        gw_df = pd.read_csv("data/groundwater.csv")
        gw_df["month_sin"] = np.sin(2 * np.pi * gw_df["month"] / 12)
        gw_df["month_cos"] = np.cos(2 * np.pi * gw_df["month"] / 12)
        X_gw = gw_df[["month_sin", "month_cos", "extraction_rate"]]
        y_gw = gw_df["depth_meters"]
        _, X_gw_test, _, y_gw_test = train_test_split(
            X_gw, y_gw, test_size=0.2, random_state=42)
        gw_preds = gw_model.predict(X_gw_test)
        gw_r2    = float(r2_score(y_gw_test, gw_preds))
        gw_mae   = float(mean_absolute_error(y_gw_test, gw_preds))

        # ── Water quality model metrics ────────────────────────────────────
        wq_df = pd.read_csv("data/water_quality.csv")
        X_wq = wq_df[["ph", "tds_mg_l", "turbidity_ntu",
                       "nitrate_mg_l", "coliform_mpn"]]
        y_wq = wq_df["quality_label"]
        _, X_wq_test, _, y_wq_test = train_test_split(
            X_wq, y_wq, test_size=0.2, random_state=42)
        wq_preds = wq_model.predict(X_wq_test)
        wq_acc   = float(accuracy_score(y_wq_test, wq_preds))
        wq_imp   = wq_model.feature_importances_.tolist()

        return (flood_acc, flood_cm, flood_imp,
                gw_r2, gw_mae,
                wq_acc, wq_imp)

    (flood_acc, flood_cm, flood_imp,
     gw_r2, gw_mae,
     wq_acc, wq_imp) = compute_metrics()

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 1 — BIG SCORE CARDS
    # ══════════════════════════════════════════════════════════════════════
    st.markdown("### 🏅 Overall Model Scores")

    s1, s2, s3 = st.columns(3)

    s1.markdown(f"""
    <div class="score-card" style="background: linear-gradient(135deg, var(--amber) 0%, #d97706 100%);">
      <p class="label">🌊 Flood Prediction</p>
      <p class="value">{flood_acc*100:.1f}%</p>
      <p class="sub">Accuracy</p>
    </div>
    """, unsafe_allow_html=True)

    s2.markdown(f"""
    <div class="score-card" style="background: linear-gradient(135deg, var(--mint) 0%, var(--sky) 100%);">
      <p class="label">🪨 Groundwater Model</p>
      <p class="value">{gw_r2:.3f}</p>
      <p class="sub">R² Score (1.0 = perfect)</p>
    </div>
    """, unsafe_allow_html=True)

    s3.markdown(f"""
    <div class="score-card" style="background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%);">
      <p class="label">🧪 Water Quality</p>
      <p class="value">{wq_acc*100:.1f}%</p>
      <p class="sub">Accuracy</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 2 — FLOOD MODEL DEEP DIVE
    # ══════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 🌊 Flood Prediction Model — Deep Dive")

    col_cm, col_fi = st.columns(2)

    with col_cm:
        st.markdown("#### Confusion Matrix")
        cm = flood_cm
        cm_labels = ["No Flood", "Flood"]
        fig_cm = go.Figure(go.Heatmap(
            z=cm,
            x=cm_labels,
            y=cm_labels,
            colorscale="RdYlGn",
            text=[[str(v) for v in row] for row in cm],
            texttemplate="%{text}",
            textfont={"size": 22, "color": "white"},
            showscale=False
        ))
        fig_cm.update_layout(
            height=320,
            margin=dict(t=20, b=40),
            xaxis_title="Predicted",
            yaxis_title="Actual",
            xaxis=dict(side="bottom")
        )
        st.plotly_chart(fig_cm, use_container_width=True)
        st.caption("✅ Diagonal = correct predictions. Off-diagonal = errors.")

    with col_fi:
        st.markdown("#### Feature Importance")
        features      = ["Today's Rainfall", "7-Day Rainfall", "Reservoir Level"]
        importance_df = pd.DataFrame({
            "Feature":    features,
            "Importance": flood_imp
        }).sort_values("Importance", ascending=True)

        fig_fi = px.bar(importance_df,
                        x="Importance", y="Feature",
                        orientation="h",
                        color="Importance",
                        color_continuous_scale="Reds",
                        labels={"Importance": "Importance Score"})
        fig_fi.update_layout(height=320, margin=dict(t=20),
                              showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_fi, use_container_width=True)
        st.caption("Higher = more influential in predicting floods.")

    # ── XGBoost info box ───────────────────────────────────────────────────
    st.info(f"""
    **Algorithm:** XGBoost Classifier  |  
    **Training samples:** 2,920  |  
    **Test samples:** 730  |  
    **Accuracy: {flood_acc*100:.1f}%**  |  
    **Features used:** Rainfall (today), 7-day cumulative rainfall, Reservoir level %
    """)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 3 — GROUNDWATER MODEL
    # ══════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 🪨 Groundwater Depletion Model — Deep Dive")

    col_gw1, col_gw2 = st.columns(2)

    with col_gw1:
        st.markdown("#### Predicted vs Actual Depth")
        gw_df2 = pd.read_csv("data/groundwater.csv")
        gw_df2["month_sin"] = np.sin(2 * np.pi * gw_df2["month"] / 12)
        gw_df2["month_cos"] = np.cos(2 * np.pi * gw_df2["month"] / 12)
        X_gw2 = gw_df2[["month_sin", "month_cos", "extraction_rate"]]
        y_gw2 = gw_df2["depth_meters"]
        _, X_t, _, y_t = train_test_split(X_gw2, y_gw2,
                                           test_size=0.2, random_state=42)
        preds_gw = gw_model.predict(X_t)

        scatter_df = pd.DataFrame({
            "Actual":    y_t.values[:50],
            "Predicted": preds_gw[:50]
        })
        fig_scatter = px.scatter(scatter_df, x="Actual", y="Predicted",
                                  trendline="ols",
                                  color_discrete_sequence=["#0077b6"],
                                  labels={"Actual": "Actual Depth (m)",
                                          "Predicted": "Predicted Depth (m)"})
        fig_scatter.add_shape(type="line",
            x0=scatter_df["Actual"].min(), y0=scatter_df["Actual"].min(),
            x1=scatter_df["Actual"].max(), y1=scatter_df["Actual"].max(),
            line=dict(color="red", dash="dash"))
        fig_scatter.update_layout(height=320, margin=dict(t=20))
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("🔴 Red dashed line = perfect prediction. Blue dots = model output.")

    with col_gw2:
        st.markdown("#### Model Statistics")
        st.markdown("<br>", unsafe_allow_html=True)

        stat1, stat2 = st.columns(2)
        stat1.metric("R² Score",  f"{gw_r2:.4f}",
                     "Higher is better (max 1.0)")
        stat2.metric("Mean Abs Error", f"{gw_mae:.2f} m",
                     "Average prediction error")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        **What this model does:**
        - Predicts groundwater table depth 3 months ahead
        - Uses seasonal patterns + extraction rates
        - Identifies districts at risk of depletion
        - Suggests optimal recharge periods
        """)

    st.info(f"""
    **Algorithm:** Random Forest Regressor  |  
    **R² Score: {gw_r2:.3f}**  |  
    **MAE: {gw_mae:.2f} m**  |  
    **Features:** Month (sin/cos encoding), Extraction rate
    """)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 4 — WATER QUALITY MODEL
    # ══════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 🧪 Water Quality Classifier — Deep Dive")

    col_wq1, col_wq2 = st.columns(2)

    with col_wq1:
        st.markdown("#### Feature Importance")
        wq_features   = ["pH", "TDS", "Turbidity", "Nitrate", "Coliform"]
        wq_imp_df     = pd.DataFrame({
            "Feature":    wq_features,
            "Importance": wq_imp
        }).sort_values("Importance", ascending=True)

        fig_wq_fi = px.bar(wq_imp_df,
                           x="Importance", y="Feature",
                           orientation="h",
                           color="Importance",
                           color_continuous_scale="Greens",
                           labels={"Importance": "Importance Score"})
        fig_wq_fi.update_layout(height=320, margin=dict(t=20),
                                 showlegend=False,
                                 coloraxis_showscale=False)
        st.plotly_chart(fig_wq_fi, use_container_width=True)
        st.caption("Which water parameters most influence quality classification.")

    with col_wq2:
        st.markdown("#### Classification Labels")
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div class="quality-badge" style="background: linear-gradient(135deg, var(--mint) 0%, var(--sky) 100%);">
          <b>🟢 Safe</b> — pH 6.5–8.5, TDS &lt;500, Nitrate &lt;45 mg/L
        </div>
        <div class="quality-badge" style="background: linear-gradient(135deg, var(--amber) 0%, #fbbf24 100%);">
          <b>🟠 Moderate Risk</b> — TDS 500–800 or Turbidity &gt;5 NTU
        </div>
        <div class="quality-badge" style="background: linear-gradient(135deg, #ef4444 0%, #fb7185 100%);">
          <b>🔴 Contaminated</b> — pH out of range, TDS &gt;800, Nitrate &gt;45
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.metric("Classification Accuracy", f"{wq_acc*100:.1f}%",
                  "Across 3 quality classes")

    st.info(f"""
    **Algorithm:** Random Forest Classifier  |  
    **Accuracy: {wq_acc*100:.1f}%**  |  
    **Classes:** Safe, Moderate Risk, Contaminated  |  
    **Features:** pH, TDS, Turbidity, Nitrate, Coliform count
    """)

    # ══════════════════════════════════════════════════════════════════════
    # SECTION 5 — ARCHITECTURE SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 🏗 System Architecture Summary")

    a1, a2, a3, a4 = st.columns(4)
    a1.markdown("""
    <div class="arch-pill" style="background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%);">
      <h3>📡</h3>
      <b>Data Sources</b><br>
      <small>IMD · CGWB · WRIS<br>Satellites · Sensors</small>
    </div>
    """, unsafe_allow_html=True)

    a2.markdown("""
    <div class="arch-pill" style="background: linear-gradient(135deg, var(--mint) 0%, var(--sky) 100%);">
      <h3>⚙️</h3>
      <b>Processing</b><br>
      <small>Pandas · NumPy<br>Time-series cleaning</small>
    </div>
    """, unsafe_allow_html=True)

    a3.markdown("""
    <div class="arch-pill" style="background: linear-gradient(135deg, var(--amber) 0%, #d97706 100%);">
      <h3>🤖</h3>
      <b>AI Models</b><br>
      <small>XGBoost · Random Forest<br>Scikit-learn</small>
    </div>
    """, unsafe_allow_html=True)

    a4.markdown("""
    <div class="arch-pill" style="background: linear-gradient(135deg, var(--navy-mid) 0%, var(--mint) 100%);">
      <h3>📊</h3>
      <b>Dashboard</b><br>
      <small>Streamlit · Plotly<br>Folium GIS</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='text-align:center; color:gray'>JalSaathi — Built for National Exhibition | Data: IMD, CGWB, India-WRIS</p>",
                unsafe_allow_html=True)