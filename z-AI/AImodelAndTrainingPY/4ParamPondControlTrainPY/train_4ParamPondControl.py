from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier


INPUT_CSV = Path(__file__).resolve().parent / "withTimePondData_station1.csv"
OUTPUT_SCHEMA_CSV = Path(__file__).resolve().parent / "withTimePondData_station1_4params_training_schema.csv"
MODEL_OUT = Path(__file__).resolve().parent / "4ParamPondControl.pkl"
METRICS_OUT = Path(__file__).resolve().parent / "4ParamPondControl_metrics.json"
MODEL_COMPRESSION = ("xz", 3)

NUMERIC_FEATURES = ["pH", "Ammonia", "Temp", "Turbidity"]
STATUS_FEATURES = ["pH_Status", "Ammonia_Status", "Temp_Status", "Turbidity_Status"]
TARGETS = ["Water Pump", "Heater"]


def build_schema(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["pH"] = pd.to_numeric(df_raw["PH"], errors="coerce")
    df["Ammonia"] = pd.to_numeric(df_raw["AMMONIA"], errors="coerce")
    df["Temp"] = pd.to_numeric(df_raw["TEMP"], errors="coerce")
    df["Turbidity"] = pd.to_numeric(df_raw["TURBIDITY"], errors="coerce")

    df = df.dropna(subset=NUMERIC_FEATURES).copy().reset_index(drop=True)

    # Keep status encoding consistent with prior pipeline (High=1, Low=0).
    df["pH_Status"] = np.where((df["pH"] >= 6.5) & (df["pH"] <= 8.5), "High", "Low")
    df["Ammonia_Status"] = np.where(df["Ammonia"] <= 0.05, "High", "Low")
    df["Temp_Status"] = np.where(df["Temp"] >= 26.0, "High", "Low")
    df["Turbidity_Status"] = np.where(df["Turbidity"] <= 20.0, "High", "Low")

    # DO and Aerator are intentionally excluded in this 4-parameter model.
    df["Water Pump"] = np.where(
        (df["Ammonia_Status"] == "Low") | (df["Turbidity_Status"] == "Low"),
        "ON",
        "OFF",
    )
    df["Heater"] = np.where(df["Temp_Status"] == "Low", "ON", "OFF")

    ordered = [
        "pH",
        "Ammonia",
        "Temp",
        "Turbidity",
        "pH_Status",
        "Ammonia_Status",
        "Temp_Status",
        "Turbidity_Status",
        "Water Pump",
        "Heater",
    ]
    return df[ordered]


def encode_features_targets(df_schema: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = df_schema[NUMERIC_FEATURES].copy()
    for col in STATUS_FEATURES:
        x[col] = (df_schema[col] == "High").astype(np.int8)

    y = pd.DataFrame(index=df_schema.index)
    for target in TARGETS:
        y[target] = (df_schema[target] == "ON").astype(np.int8)

    return x, y


def apply_label_noise(y: pd.DataFrame, noise_rate: float, seed: int) -> tuple[pd.DataFrame, dict[str, int]]:
    if noise_rate <= 0:
        return y.copy(), {target: 0 for target in TARGETS}

    rng = np.random.default_rng(seed)
    y_noisy = y.copy()
    noise_counts: dict[str, int] = {}

    for target in TARGETS:
        mask = rng.random(len(y_noisy)) < noise_rate
        y_noisy.loc[mask, target] = 1 - y_noisy.loc[mask, target]
        noise_counts[target] = int(mask.sum())

    return y_noisy, noise_counts


def evaluate(y_true: pd.DataFrame, y_pred: np.ndarray) -> dict:
    subset_acc = float(accuracy_score(y_true, y_pred))
    per_acc = {}
    per_f1 = {}

    for i, t in enumerate(TARGETS):
        per_acc[t] = float(accuracy_score(y_true.iloc[:, i], y_pred[:, i]))
        per_f1[t] = float(f1_score(y_true.iloc[:, i], y_pred[:, i], average="binary", zero_division=0))

    return {
        "subset_accuracy": subset_acc,
        "macro_f1": float(np.mean(list(per_f1.values()))),
        "per_target_accuracy": per_acc,
        "per_target_f1": per_f1,
    }


def main() -> None:
    seed = 42
    test_size = 0.2
    noise_rate = 0.045

    raw = pd.read_csv(INPUT_CSV, low_memory=False)
    schema_df = build_schema(raw)
    schema_df.to_csv(OUTPUT_SCHEMA_CSV, index=False)

    x, y = encode_features_targets(schema_df)
    y_noisy, noise_counts = apply_label_noise(y, noise_rate=noise_rate, seed=seed)

    combo = y_noisy.astype(str).agg("_".join, axis=1)
    stratify_labels = combo if combo.value_counts().min() >= 2 else None

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y_noisy,
        test_size=test_size,
        random_state=seed,
        stratify=stratify_labels,
    )

    model = MultiOutputClassifier(
        ExtraTreesClassifier(
            n_estimators=300,
            random_state=seed,
            n_jobs=-1,
            class_weight="balanced_subsample",
        )
    )

    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    metrics = evaluate(y_test, pred)

    trained_at = datetime.now(UTC).isoformat()

    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    METRICS_OUT.parent.mkdir(parents=True, exist_ok=True)

    model_artifact = {
        "model": model,
        "model_name": "ExtraTrees",
        "wrapper": "MultiOutputClassifier",
        "feature_columns": NUMERIC_FEATURES + STATUS_FEATURES,
        "target_columns": TARGETS,
        "excluded_features": ["DO", "DO_Status"],
        "excluded_targets": ["Aerator"],
        "status_encoding": {"Low": 0, "High": 1},
        "actuator_encoding": {"OFF": 0, "ON": 1},
        "source_csv": str(INPUT_CSV),
        "schema_csv": str(OUTPUT_SCHEMA_CSV),
        "seed": seed,
        "test_size": test_size,
        "label_noise_rate": noise_rate,
        "label_noise_counts": noise_counts,
        "metrics": metrics,
        "trained_at": trained_at,
    }

    metrics_payload = {k: v for k, v in model_artifact.items() if k != "model"}

    joblib.dump(model_artifact, MODEL_OUT, compress=MODEL_COMPRESSION, protocol=5)
    with METRICS_OUT.open("w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    print("=" * 90)
    print("TRAINING 4-PARAMETER ACTUATOR MODEL (NO DO, NO AERATOR)")
    print("=" * 90)
    print(f"Source CSV: {INPUT_CSV}")
    print(f"Schema CSV: {OUTPUT_SCHEMA_CSV}")
    print(f"Rows used: {len(schema_df):,}")
    print(f"Train/Test: {len(x_train):,}/{len(x_test):,}")
    print(f"Algorithm: ExtraTreesClassifier + MultiOutputClassifier")
    print(f"Label noise rate: {noise_rate * 100:.2f}% per target")
    print(f"Label noise flips: Water Pump={noise_counts['Water Pump']}, Heater={noise_counts['Heater']}")
    print("-" * 90)
    print(f"Subset accuracy: {metrics['subset_accuracy'] * 100:.2f}%")
    print(f"Macro F1: {metrics['macro_f1'] * 100:.2f}%")
    print("Per-target accuracy:")
    for target, score in metrics["per_target_accuracy"].items():
        print(f"  - {target}: {score * 100:.2f}%")
    print("-" * 90)
    print(f"Model saved:   {MODEL_OUT}")
    print(f"Metrics saved: {METRICS_OUT}")


if __name__ == "__main__":
    main()
