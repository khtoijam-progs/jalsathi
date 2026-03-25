# data_pipeline.py
import pandas as pd
import numpy as np
import os

np.random.seed(42)

# --- CONFIG ---
DISTRICTS = [
    "Vijayawada", "Guntur", "Kurnool", "Nellore", "Visakhapatnam",
    "Rajahmundry", "Tirupati", "Kakinada", "Ongole", "Eluru"
]
DAYS = 365  # one year of data

def generate_rainfall_data():
    rows = []
    for district in DISTRICTS:
        for day in range(DAYS):
            date = pd.Timestamp("2023-01-01") + pd.Timedelta(days=day)
            month = date.month
            # Monsoon season (June-September) gets higher rainfall
            if month in [6, 7, 8, 9]:
                rainfall = np.random.exponential(scale=20)
            else:
                rainfall = np.random.exponential(scale=3)
            rows.append({
                "date": date,
                "district": district,
                "rainfall_mm": round(rainfall, 2)
            })
    df = pd.DataFrame(rows)
    df.to_csv("data/rainfall.csv", index=False)
    print("✅ Rainfall data generated:", df.shape)
    return df

def generate_dam_data():
    rows = []
    for district in DISTRICTS:
        capacity = np.random.randint(500, 5000)  # million cubic feet
        level = np.random.uniform(30, 95)        # % full at start
        for day in range(DAYS):
            date = pd.Timestamp("2023-01-01") + pd.Timedelta(days=day)
            month = date.month
            if month in [6, 7, 8, 9]:
                level = min(100, level + np.random.uniform(0.5, 2.5))
            else:
                level = max(10, level - np.random.uniform(0.1, 0.8))
            rows.append({
                "date": date,
                "district": district,
                "reservoir_level_pct": round(level, 2),
                "capacity_mcft": capacity
            })
    df = pd.DataFrame(rows)
    df.to_csv("data/dam_levels.csv", index=False)
    print("✅ Dam data generated:", df.shape)
    return df

def generate_groundwater_data():
    rows = []
    for district in DISTRICTS:
        base_level = np.random.uniform(5, 30)  # meters below ground
        for month in range(1, 13):
            for year in [2022, 2023]:
                # Monsoon recharges groundwater
                if month in [8, 9, 10]:
                    level = base_level - np.random.uniform(1, 4)
                else:
                    level = base_level + np.random.uniform(0.2, 1.5)
                base_level = level
                rows.append({
                    "year": year,
                    "month": month,
                    "district": district,
                    "depth_meters": round(level, 2),
                    "extraction_rate": round(np.random.uniform(0.5, 3.5), 2)
                })
    df = pd.DataFrame(rows)
    df.to_csv("data/groundwater.csv", index=False)
    print("✅ Groundwater data generated:", df.shape)
    return df

def generate_water_quality_data():
    rows = []
    for district in DISTRICTS:
        for i in range(50):  # 50 test samples per district
            ph = np.random.normal(7.2, 0.8)
            tds = np.random.normal(400, 150)
            turbidity = np.random.exponential(3)
            nitrate = np.random.exponential(10)
            coliform = np.random.exponential(5)
            # Label based on thresholds
            if ph < 6.5 or ph > 8.5 or tds > 800 or nitrate > 45:
                quality = "Contaminated"
            elif tds > 500 or turbidity > 5:
                quality = "Moderate Risk"
            else:
                quality = "Safe"
            rows.append({
                "district": district,
                "ph": round(ph, 2),
                "tds_mg_l": round(tds, 2),
                "turbidity_ntu": round(turbidity, 2),
                "nitrate_mg_l": round(nitrate, 2),
                "coliform_mpn": round(coliform, 2),
                "quality_label": quality
            })
    df = pd.DataFrame(rows)
    df.to_csv("data/water_quality.csv", index=False)
    print("✅ Water quality data generated:", df.shape)
    return df

def generate_flood_labels(rainfall_df, dam_df):
    """Merge data and create flood labels for ML training"""
    # 7-day rolling rainfall
    rainfall_df = rainfall_df.sort_values(["district", "date"])
    rainfall_df["rolling_7d"] = rainfall_df.groupby("district")["rainfall_mm"].transform(
        lambda x: x.rolling(7, min_periods=1).sum()
    )
    merged = rainfall_df.merge(dam_df, on=["date", "district"])
    # Flood = heavy rain AND high reservoir
    merged["flood"] = (
        (merged["rolling_7d"] > 80) & (merged["reservoir_level_pct"] > 85)
    ).astype(int)
    merged.to_csv("data/flood_training.csv", index=False)
    print("✅ Flood training data generated:", merged.shape)
    print(f"   Flood events: {merged['flood'].sum()} / {len(merged)}")
    return merged

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    rain = generate_rainfall_data()
    dam  = generate_dam_data()
    generate_groundwater_data()
    generate_water_quality_data()
    generate_flood_labels(rain, dam)
    print("\n🎉 All data files ready in /data folder!")