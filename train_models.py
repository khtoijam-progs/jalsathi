# train_models.py
import pandas as pd
import numpy as np
import os
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

os.makedirs("models", exist_ok=True)

# ── MODEL 1: Flood Prediction ──────────────────────────────────────────────
print("🤖 Training Flood Prediction Model...")
df = pd.read_csv("data/flood_training.csv")

features = ["rainfall_mm", "rolling_7d", "reservoir_level_pct"]
X = df[features]
y = df["flood"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

flood_model = XGBClassifier(n_estimators=100, max_depth=6, random_state=42, eval_metric="logloss")
flood_model.fit(X_train, y_train)

preds = flood_model.predict(X_test)
acc = accuracy_score(y_test, preds)
print(f"   ✅ Flood Model Accuracy: {acc*100:.1f}%")
print(classification_report(y_test, preds, target_names=["No Flood", "Flood"]))

with open("models/flood_model.pkl", "wb") as f:
    pickle.dump(flood_model, f)

# ── MODEL 2: Groundwater Depletion ────────────────────────────────────────
print("🤖 Training Groundwater Model...")
gw = pd.read_csv("data/groundwater.csv")
gw["month_sin"] = np.sin(2 * np.pi * gw["month"] / 12)
gw["month_cos"] = np.cos(2 * np.pi * gw["month"] / 12)

X_gw = gw[["month_sin", "month_cos", "extraction_rate"]]
y_gw = gw["depth_meters"]

X_train_gw, X_test_gw, y_train_gw, y_test_gw = train_test_split(
    X_gw, y_gw, test_size=0.2, random_state=42
)
gw_model = RandomForestRegressor(n_estimators=100, random_state=42)
gw_model.fit(X_train_gw, y_train_gw)

score = gw_model.score(X_test_gw, y_test_gw)
print(f"   ✅ Groundwater Model R² Score: {score:.3f}")

with open("models/groundwater_model.pkl", "wb") as f:
    pickle.dump(gw_model, f)

# ── MODEL 3: Water Quality Classifier ─────────────────────────────────────
print("🤖 Training Water Quality Model...")
wq = pd.read_csv("data/water_quality.csv")

X_wq = wq[["ph", "tds_mg_l", "turbidity_ntu", "nitrate_mg_l", "coliform_mpn"]]
y_wq = wq["quality_label"]

X_train_wq, X_test_wq, y_train_wq, y_test_wq = train_test_split(
    X_wq, y_wq, test_size=0.2, random_state=42
)
wq_model = RandomForestClassifier(n_estimators=100, random_state=42)
wq_model.fit(X_train_wq, y_train_wq)

wq_acc = accuracy_score(y_test_wq, wq_model.predict(X_test_wq))
print(f"   ✅ Water Quality Model Accuracy: {wq_acc*100:.1f}%")

with open("models/water_quality_model.pkl", "wb") as f:
    pickle.dump(wq_model, f)

print("\n🎉 All models trained and saved to /models folder!")