import json
import math
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

BASE = Path(r"C:/Users/USER/Desktop/capstone/z-AI/AforProduction")
DATA = Path(r"C:/Users/USER/Desktop/capstone/z-AI/DODO/AforDeviceControlModel/withTimePondData_station1.csv")

FILES = {
    "5params": BASE / "pondContol.pkl",
    "4params": BASE / "4ParametersPkl.pkl",
    "do_model": BASE / "station1_random_classifier_compact.pkl",
}


def add_status_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["pH_Status"] = out["PH"].between(6.5, 8.5).astype(int)
    out["Ammonia_Status"] = (out["AMMONIA"] <= 0.05).astype(int)
    out["Temp_Status"] = (out["TEMP"] >= 26.0).astype(int)
    out["DO_Status"] = out["DO"].between(6.0, 8.5).astype(int)
    out["Turbidity_Status"] = (out["TURBIDITY"] <= 20.0).astype(int)
    return out


def build_do_features(df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    feat = pd.DataFrame(index=df.index)
    feat["ph"] = df["PH"].astype(float)
    feat["ammonia"] = df["AMMONIA"].astype(float)
    feat["temp"] = df["TEMP"].astype(float)
    feat["turbidity"] = df["TURBIDITY"].astype(float)

    hours = (np.arange(len(df)) % 24).astype(float)
    feat["hour_sin"] = np.sin(2.0 * math.pi * hours / 24.0)
    feat["hour_cos"] = np.cos(2.0 * math.pi * hours / 24.0)

    for sensor in ["ph", "ammonia", "temp", "turbidity"]:
        feat[f"{sensor}_lag1"] = feat[sensor].shift(1)
        feat[f"{sensor}_lag2"] = feat[sensor].shift(2)
        feat[f"{sensor}_lag3"] = feat[sensor].shift(3)

        feat[f"{sensor}_lag1"] = feat[f"{sensor}_lag1"].fillna(feat[sensor])
        feat[f"{sensor}_lag2"] = feat[f"{sensor}_lag2"].fillna(feat[sensor])
        feat[f"{sensor}_lag3"] = feat[f"{sensor}_lag3"].fillna(feat[sensor])

        feat[f"{sensor}_diff1"] = feat[sensor] - feat[f"{sensor}_lag1"]

        roll = feat[sensor].rolling(window=3, min_periods=1)
        feat[f"{sensor}_roll3_mean"] = roll.mean()
        feat[f"{sensor}_roll3_std"] = roll.std().fillna(0.0)

    feat["ph_sq"] = feat["ph"] ** 2
    feat["ammonia_sq"] = feat["ammonia"] ** 2
    feat["temp_sq"] = feat["temp"] ** 2
    feat["ph_ammonia"] = feat["ph"] * feat["ammonia"]
    feat["temp_turbidity"] = feat["temp"] * feat["turbidity"]

    return feat[feature_columns]


def ms(dt):
    return round(dt * 1000.0, 3)


def main():
    print("=== PKL Production Smoke Check ===")
    print(f"Data file exists: {DATA.exists()} | rows={sum(1 for _ in open(DATA, 'r', encoding='utf-8')) - 1 if DATA.exists() else 0}")

    for name, p in FILES.items():
        print(f"{name}: exists={p.exists()} size_bytes={p.stat().st_size if p.exists() else -1}")

    df = pd.read_csv(DATA)
    sample = df.head(1000).copy()
    sample_status = add_status_columns(sample)

    # 5params
    m5 = joblib.load(FILES["5params"])
    model5 = m5["model"]
    x5 = sample_status[[
        "PH", "AMMONIA", "TEMP", "DO", "TURBIDITY",
        "pH_Status", "Ammonia_Status", "Temp_Status", "DO_Status", "Turbidity_Status",
    ]].copy()
    x5.columns = [
        "pH", "Ammonia", "Temp", "DO", "Turbidity",
        "pH_Status", "Ammonia_Status", "Temp_Status", "DO_Status", "Turbidity_Status",
    ]
    t0 = time.perf_counter()
    y5 = model5.predict(x5)
    t1 = time.perf_counter()
    print(f"5params: predict_ok rows={len(y5)} latency_ms={ms(t1-t0)}")
    print(f"5params targets={m5.get('target_columns')}")
    print(f"5params best_metrics={m5.get('best_metrics')}")

    # 4params
    m4 = joblib.load(FILES["4params"])
    model4 = m4["model"]
    x4 = sample_status[[
        "PH", "AMMONIA", "TEMP", "TURBIDITY",
        "pH_Status", "Ammonia_Status", "Temp_Status", "Turbidity_Status",
    ]].copy()
    x4.columns = [
        "pH", "Ammonia", "Temp", "Turbidity",
        "pH_Status", "Ammonia_Status", "Temp_Status", "Turbidity_Status",
    ]
    t0 = time.perf_counter()
    y4 = model4.predict(x4)
    t1 = time.perf_counter()
    print(f"4params: predict_ok rows={len(y4)} latency_ms={ms(t1-t0)}")
    print(f"4params targets={m4.get('target_columns')}")
    print(f"4params metrics={m4.get('metrics')}")

    # DO model
    mdo = joblib.load(FILES["do_model"])
    clf = mdo["model"]
    calibrator = mdo["do_calibrator"]
    feat_cols = mdo["feature_columns"]

    xdo = build_do_features(sample, feat_cols)
    t0 = time.perf_counter()
    c = clf.predict(xdo)
    p = clf.predict_proba(xdo)
    do_pred = calibrator.predict(p)
    t1 = time.perf_counter()

    print(f"do_model: predict_ok rows={len(c)} latency_ms={ms(t1-t0)}")
    print(f"do_model class_order={mdo.get('class_order')}")
    print(f"do_model do_pred_min={float(np.min(do_pred)):.3f} do_pred_max={float(np.max(do_pred)):.3f}")
    print("do_model class counts (first 1000 rows):")
    vals, counts = np.unique(c, return_counts=True)
    print(dict(zip(vals.tolist(), counts.tolist())))

    summary = {
        "files": {k: str(v) for k, v in FILES.items()},
        "checks": {
            "5params_predict_rows": int(len(y5)),
            "4params_predict_rows": int(len(y4)),
            "do_predict_rows": int(len(c)),
            "do_pred_min": float(np.min(do_pred)),
            "do_pred_max": float(np.max(do_pred)),
        },
        "metrics": {
            "5params_best_metrics": m5.get("best_metrics"),
            "4params_metrics": m4.get("metrics"),
        },
        "metadata": {
            "5params_targets": m5.get("target_columns"),
            "4params_targets": m4.get("target_columns"),
            "do_class_order": mdo.get("class_order"),
            "do_feature_count": len(mdo.get("feature_columns", [])),
        },
    }
    out = BASE / "pkl_production_check_summary.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"summary written: {out}")


if __name__ == "__main__":
    main()
