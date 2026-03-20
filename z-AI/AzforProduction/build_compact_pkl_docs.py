import math
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

BASE = Path(r"C:/Users/USER/Desktop/capstone/z-AI/AforProduction")
DATA_PATH = Path(r"C:/Users/USER/Desktop/capstone/z-AI/DODO/AforDeviceControlModel/withTimePondData_station1.csv")

OUT_4 = BASE / "4ParametersPkl_EXAMPLE_PREDICTION_RESULTS.md"
OUT_5 = BASE / "STATION1_ACTUATOR_CONTROL_AI_MODEL.md"
OUT_DO = BASE / "STATION1_WATER_QUALITY_PREDICT_DO_MODEL.md"


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


def to_on_off(value) -> str:
    if isinstance(value, str):
        upper = value.strip().upper()
        if upper in {"ON", "OFF"}:
            return upper
    return "ON" if int(value) == 1 else "OFF"


def make_state_subsets(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    bad_count = (
        (~df["PH"].between(6.5, 8.5)).astype(int)
        + (df["AMMONIA"] > 0.05).astype(int)
        + (df["TEMP"] < 26.0).astype(int)
        + (df["TURBIDITY"] > 20.0).astype(int)
        + (~df["DO"].between(6.0, 8.5)).astype(int)
    )

    safe = df[bad_count == 0].head(20)
    warning = df[(bad_count >= 1) & (bad_count <= 2)].head(20)
    danger = df[bad_count >= 3].head(20)

    return {"SAFE": safe, "WARNING": warning, "DANGER": danger}


def build_5params_doc(state_rows: dict[str, pd.DataFrame], pred_map: dict[str, np.ndarray]) -> str:
    lines: list[str] = ["# 5params", ""]

    for state in ["SAFE", "WARNING", "DANGER"]:
        rows = state_rows[state]
        preds = pred_map[state]

        lines.append(f"## {state} (20)")
        lines.append("")
        lines.append("| pH | Ammonia | Temp | DO | Turbidity | Aerator | Water_Pump | Heater |")
        lines.append("|---:|---:|---:|---:|---:|---|---|---|")

        for i, (_, row) in enumerate(rows.iterrows()):
            aerator = to_on_off(preds[i][0])
            pump = to_on_off(preds[i][1])
            heater = to_on_off(preds[i][2])
            lines.append(
                f"| {row['PH']:.1f} | {row['AMMONIA']:.4f} | {row['TEMP']:.1f} | {row['DO']:.1f} | {row['TURBIDITY']:.0f} | {aerator} | {pump} | {heater} |"
            )

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_4params_doc(state_rows: dict[str, pd.DataFrame], pred_map: dict[str, np.ndarray]) -> str:
    lines: list[str] = ["# 4params", ""]

    for state in ["SAFE", "WARNING", "DANGER"]:
        rows = state_rows[state]
        preds = pred_map[state]

        lines.append(f"## {state} (20)")
        lines.append("")
        lines.append("| pH | Ammonia | Temp | Turbidity | pH_Status | Ammonia_Status | Temp_Status | Turbidity_Status | Water_Pump | Heater |")
        lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")

        for i, (_, row) in enumerate(rows.iterrows()):
            p_h = int(6.5 <= row["PH"] <= 8.5)
            amm = int(row["AMMONIA"] <= 0.05)
            tmp = int(row["TEMP"] >= 26.0)
            turb = int(row["TURBIDITY"] <= 20.0)
            pump = to_on_off(preds[i][0])
            heater = to_on_off(preds[i][1])
            lines.append(
                f"| {row['PH']:.1f} | {row['AMMONIA']:.4f} | {row['TEMP']:.1f} | {row['TURBIDITY']:.0f} | {p_h} | {amm} | {tmp} | {turb} | {pump} | {heater} |"
            )

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_do_doc(
    state_rows: dict[str, pd.DataFrame],
    class_map: dict[str, np.ndarray],
    do_map: dict[str, np.ndarray],
) -> str:
    lines: list[str] = ["# DOprediction", ""]

    for state in ["SAFE", "WARNING", "DANGER"]:
        rows = state_rows[state]
        classes = class_map[state]
        pred_do = do_map[state]

        lines.append(f"## {state} (20)")
        lines.append("")
        lines.append("| pH | Ammonia | Temp | Turbidity | DO | Water_Class | Pred_DO |")
        lines.append("|---:|---:|---:|---:|---:|---|---:|")

        for i, (_, row) in enumerate(rows.iterrows()):
            lines.append(
                f"| {row['PH']:.1f} | {row['AMMONIA']:.4f} | {row['TEMP']:.1f} | {row['TURBIDITY']:.0f} | {row['DO']:.1f} | {classes[i]} | {pred_do[i]:.2f} |"
            )

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    state_rows = make_state_subsets(df)

    model_5 = joblib.load(BASE / "pondContol.pkl")
    model_4 = joblib.load(BASE / "4ParametersPkl.pkl")
    model_do = joblib.load(BASE / "station1_random_classifier_compact.pkl")

    model5 = model_5["model"]
    model4 = model_4["model"]
    model_do_clf = model_do["model"]
    do_calibrator = model_do["do_calibrator"]
    do_feature_columns = model_do["feature_columns"]

    df_with_status = add_status_columns(df)
    do_features_all = build_do_features(df, do_feature_columns)

    pred5: dict[str, np.ndarray] = {}
    pred4: dict[str, np.ndarray] = {}
    class_map: dict[str, np.ndarray] = {}
    do_map: dict[str, np.ndarray] = {}

    for state in ["SAFE", "WARNING", "DANGER"]:
        idx = state_rows[state].index

        x5 = df_with_status.loc[idx, [
            "PH",
            "AMMONIA",
            "TEMP",
            "DO",
            "TURBIDITY",
            "pH_Status",
            "Ammonia_Status",
            "Temp_Status",
            "DO_Status",
            "Turbidity_Status",
        ]].copy()
        x5.columns = [
            "pH",
            "Ammonia",
            "Temp",
            "DO",
            "Turbidity",
            "pH_Status",
            "Ammonia_Status",
            "Temp_Status",
            "DO_Status",
            "Turbidity_Status",
        ]
        pred5[state] = model5.predict(x5)

        x4 = df_with_status.loc[idx, [
            "PH",
            "AMMONIA",
            "TEMP",
            "TURBIDITY",
            "pH_Status",
            "Ammonia_Status",
            "Temp_Status",
            "Turbidity_Status",
        ]].copy()
        x4.columns = [
            "pH",
            "Ammonia",
            "Temp",
            "Turbidity",
            "pH_Status",
            "Ammonia_Status",
            "Temp_Status",
            "Turbidity_Status",
        ]
        pred4[state] = model4.predict(x4)

        xdo = do_features_all.loc[idx, do_feature_columns]
        pred_class = model_do_clf.predict(xdo)
        pred_prob = model_do_clf.predict_proba(xdo)
        pred_do = do_calibrator.predict(pred_prob)

        class_map[state] = pred_class
        do_map[state] = pred_do

    OUT_5.write_text(build_5params_doc(state_rows, pred5), encoding="utf-8")
    OUT_4.write_text(build_4params_doc(state_rows, pred4), encoding="utf-8")
    OUT_DO.write_text(build_do_doc(state_rows, class_map, do_map), encoding="utf-8")

    safe_preds = pred5["SAFE"]
    safe_on_ratio = {
        "Aerator_ON": float((safe_preds[:, 0] == 1).mean()),
        "Water_Pump_ON": float((safe_preds[:, 1] == 1).mean()),
        "Heater_ON": float((safe_preds[:, 2] == 1).mean()),
    }
    print("Wrote compact docs:")
    print(str(OUT_4))
    print(str(OUT_5))
    print(str(OUT_DO))
    print("SAFE 5params ON ratios:", safe_on_ratio)


if __name__ == "__main__":
    main()
