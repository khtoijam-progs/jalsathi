# gis_map.py - Fixed for Python 3.14 + NumPy float32 issue
import folium
import pandas as pd
import numpy as np
import pickle

DISTRICT_COORDS = {
    "Vijayawada":    (16.5062, 80.6480),
    "Guntur":        (16.3067, 80.4365),
    "Kurnool":       (15.8281, 78.0373),
    "Nellore":       (14.4426, 79.9865),
    "Visakhapatnam": (17.6868, 83.2185),
    "Rajahmundry":   (17.0005, 81.8040),
    "Tirupati":      (13.6288, 79.4192),
    "Kakinada":      (16.9891, 82.2475),
    "Ongole":        (15.5057, 80.0499),
    "Eluru":         (16.7107, 81.0952),
}

def to_float(val):
    """Force convert any numpy type to plain Python float"""
    return float(val)

def build_map():
    rain = pd.read_csv("data/rainfall.csv", parse_dates=["date"])
    dam  = pd.read_csv("data/dam_levels.csv", parse_dates=["date"])
    gw   = pd.read_csv("data/groundwater.csv")
    wq   = pd.read_csv("data/water_quality.csv")

    latest_rain = rain.sort_values("date").groupby("district").last().reset_index()
    latest_dam  = dam.sort_values("date").groupby("district").last().reset_index()
    latest_gw   = gw.groupby("district")["depth_meters"].mean().reset_index()
    wq_mode     = wq.groupby("district")["quality_label"].agg(
        lambda x: x.value_counts().index[0]
    ).reset_index()

    # Add rolling_7d if missing
    if "rolling_7d" not in latest_rain.columns:
        rain = rain.sort_values(["district", "date"])
        rain["rolling_7d"] = rain.groupby("district")["rainfall_mm"].transform(
            lambda x: x.rolling(7, min_periods=1).sum()
        )
        latest_rain = rain.sort_values("date").groupby("district").last().reset_index()

    with open("models/flood_model.pkl", "rb") as f:
        flood_model = pickle.load(f)

    m = folium.Map(location=[15.9129, 79.7400], zoom_start=7,
                   tiles="CartoDB positron")

    def flood_color(risk):
        if risk > 0.7: return "red"
        elif risk > 0.4: return "orange"
        else: return "green"

    def dam_color(pct):
        if pct > 85: return "red"
        elif pct > 60: return "orange"
        else: return "blue"

    quality_color = {"Safe": "green", "Moderate Risk": "orange", "Contaminated": "red"}

    for district, (lat, lon) in DISTRICT_COORDS.items():
        r_row  = latest_rain[latest_rain["district"] == district]
        d_row  = latest_dam[latest_dam["district"] == district]
        g_row  = latest_gw[latest_gw["district"] == district]
        wq_row = wq_mode[wq_mode["district"] == district]

        if r_row.empty or d_row.empty:
            continue

        # ✅ Force all values to plain Python float/str
        rainfall  = to_float(r_row["rainfall_mm"].values[0])
        rolling   = to_float(r_row["rolling_7d"].values[0]) if "rolling_7d" in r_row.columns else rainfall * 5
        dam_lvl   = to_float(d_row["reservoir_level_pct"].values[0])
        gw_depth  = to_float(g_row["depth_meters"].values[0]) if not g_row.empty else 15.0
        quality   = str(wq_row["quality_label"].values[0]) if not wq_row.empty else "Safe"

        # Predict flood risk
        X_pred = pd.DataFrame([[rainfall, rolling, dam_lvl]],
                               columns=["rainfall_mm", "rolling_7d", "reservoir_level_pct"])
        flood_prob = float(flood_model.predict_proba(X_pred)[0][1].item())

        # ✅ All values in popup are plain Python types
        popup_html = f"""
        <div style="font-family:Arial; width:220px">
          <h4 style="color:#1a73e8; margin:0">💧 {district}</h4>
          <hr style="margin:5px 0">
          <b>🌧 Rainfall (today):</b> {rainfall:.1f} mm<br>
          <b>🏞 Reservoir Level:</b> {dam_lvl:.1f}%<br>
          <b>🌊 Flood Risk:</b>
            <span style="color:{'red' if flood_prob>0.7 else 'orange' if flood_prob>0.4 else 'green'}">
              {flood_prob*100:.0f}%
            </span><br>
          <b>🪨 Groundwater Depth:</b> {gw_depth:.1f} m<br>
          <b>🧪 Water Quality:</b>
            <span style="color:{quality_color.get(quality,'gray')}">{quality}</span>
        </div>
        """

        # ✅ radius explicitly cast to float
        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=float((15 + flood_prob * 20).item()) if hasattr((15 + flood_prob * 20), 'item') else float(15 + flood_prob * 20),
            color=flood_color(flood_prob),
            fill=True,
            fill_opacity=0.6,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{district} — Flood Risk: {flood_prob*100:.0f}%"
        ).add_to(m)

        folium.Marker(
            location=[float(lat + 0.08), float(lon + 0.08)],
            icon=folium.Icon(color=dam_color(dam_lvl), icon="tint", prefix="fa"),
            tooltip=f"🏞 {district} Dam: {dam_lvl:.1f}%"
        ).add_to(m)

    legend_html = """
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                background:white; padding:12px; border-radius:8px;
                border:2px solid #ccc; font-family:Arial; font-size:13px">
      <b>🗺 JalSaathi Map Legend</b><br>
      <span style="color:red">● </span> High Flood Risk (&gt;70%)<br>
      <span style="color:orange">● </span> Medium Risk (40–70%)<br>
      <span style="color:green">● </span> Low Risk (&lt;40%)<br>
      <hr style="margin:5px 0">
      <span style="color:red">📍</span> Dam &gt;85% Full<br>
      <span style="color:orange">📍</span> Dam 60–85% Full<br>
      <span style="color:blue">📍</span> Dam &lt;60% Full
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save("gis/flood_map.html")
    print("✅ GIS map saved to gis/flood_map.html")

if __name__ == "__main__":
    build_map()