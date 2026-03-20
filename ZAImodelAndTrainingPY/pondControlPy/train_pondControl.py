from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from xgboost import XGBClassifier


FEATURE_COLUMNS = ["PH", "AMMONIA", "TEMP", "DO", "TURBIDITY"]
TARGET_COLUMNS = ["Aerator", "Water Pump", "Heater"]


def build_targets(df: pd.DataFrame) -> pd.DataFrame:
    y = pd.DataFrame(index=df.index)
    # Rule-based labels requested by user.
    y["Aerator"] = (df["DO"] < 5.0).astype(int)
    y["Water Pump"] = ((df["AMMONIA"] > 0.5) | (df["TURBIDITY"] < 20.0)).astype(int)
    y["Heater"] = (df["TEMP"] < 25.0).astype(int)
    return y


def evaluate_predictions(y_true: pd.DataFrame, y_pred: np.ndarray) -> dict:
    subset_acc = float(accuracy_score(y_true, y_pred))

    per_target_acc: dict[str, float] = {}
    per_target_f1: dict[str, float] = {}
    for idx, col in enumerate(TARGET_COLUMNS):
        target_true = y_true.iloc[:, idx]
        target_pred = y_pred[:, idx]
        per_target_acc[col] = float(accuracy_score(target_true, target_pred))
        per_target_f1[col] = float(f1_score(target_true, target_pred, average="binary", zero_division=0))

    macro_f1 = float(np.mean(list(per_target_f1.values())))
    return {
        "subset_accuracy": subset_acc,
        "macro_f1": macro_f1,
        "per_target_accuracy": per_target_acc,
        "per_target_f1": per_target_f1,
    }


def build_models(seed: int) -> dict[str, MultiOutputClassifier]:
    models: dict[str, MultiOutputClassifier] = {
        "RandomForest": MultiOutputClassifier(
            RandomForestClassifier(
                n_estimators=260,
                max_depth=14,
                min_samples_split=2,
                min_samples_leaf=1,
                class_weight="balanced_subsample",
                random_state=seed,
                n_jobs=-1,
            )
        ),
        "ExtraTrees": MultiOutputClassifier(
            ExtraTreesClassifier(
                n_estimators=320,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                class_weight="balanced_subsample",
                random_state=seed,
                n_jobs=-1,
            )
        ),
        "LightGBM": MultiOutputClassifier(
            LGBMClassifier(
                n_estimators=260,
                learning_rate=0.05,
                num_leaves=63,
                max_depth=-1,
                subsample=0.9,
                colsample_bytree=0.9,
                random_state=seed,
                n_jobs=-1,
                verbosity=-1,
            )
        ),
        "XGBoost": MultiOutputClassifier(
            XGBClassifier(
                n_estimators=260,
                max_depth=7,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                reg_lambda=1.0,
                objective="binary:logistic",
                eval_metric="logloss",
                tree_method="hist",
                random_state=seed,
                n_jobs=-1,
            )
        ),
    }
    return models


def train_and_select(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.DataFrame,
    y_test: pd.DataFrame,
    seed: int,
) -> tuple[str, MultiOutputClassifier, dict[str, dict]]:
    models = build_models(seed)
    results: dict[str, dict] = {}
    best_name = ""
    best_model: MultiOutputClassifier | None = None
    best_score = -1.0

    for name, model in models.items():
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        metrics = evaluate_predictions(y_test, y_pred)
        results[name] = metrics

        if metrics["subset_accuracy"] > best_score:
            best_score = metrics["subset_accuracy"]
            best_name = name
            best_model = model

    if best_model is None:
        raise RuntimeError("No model was trained successfully.")

    return best_name, best_model, results


def main() -> None:
    parser = argparse.ArgumentParser(description="Train actuator control model from station1 sensor dataset.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parent / "withTimePondData_station1.csv",
        help="Input CSV path with sensor readings.",
    )
    parser.add_argument(
        "--model-output",
        type=Path,
        default=Path(__file__).resolve().parent / "pondControl.pkl",
        help="Output path for best model artifact.",
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        default=Path(__file__).resolve().parent / "pondControl_metrics.json",
        help="Output path for training metrics json.",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = pd.read_csv(args.input, low_memory=False)

    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required feature columns: {missing}")

    for col in FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=FEATURE_COLUMNS).copy().reset_index(drop=True)
    x = df[FEATURE_COLUMNS].astype(np.float32)
    y = build_targets(df)

    combo = y.astype(str).agg("_".join, axis=1)
    stratify_labels = combo if combo.value_counts().min() >= 2 else None

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=stratify_labels,
    )

    best_name, best_model, results = train_and_select(x_train, x_test, y_train, y_test, args.seed)

    best_metrics = results[best_name]

    args.model_output.parent.mkdir(parents=True, exist_ok=True)
    args.metrics_output.parent.mkdir(parents=True, exist_ok=True)

    trained_at = datetime.now(UTC).isoformat()

    artifact = {
        "model": best_model,
        "model_name": best_name,
        "feature_columns": FEATURE_COLUMNS,
        "target_columns": TARGET_COLUMNS,
        "label_encoding": {"OFF": 0, "ON": 1},
        "rules_used_for_training_labels": {
            "Aerator": "ON if DO < 5.0 else OFF",
            "Water Pump": "ON if AMMONIA > 0.5 or TURBIDITY < 20.0 else OFF",
            "Heater": "ON if TEMP < 25.0 else OFF",
        },
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "seed": args.seed,
        "test_size": args.test_size,
        "best_metrics": best_metrics,
        "all_model_metrics": results,
        "trained_at": trained_at,
    }

    metrics_payload = {
        "model_name": best_name,
        "feature_columns": FEATURE_COLUMNS,
        "target_columns": TARGET_COLUMNS,
        "label_encoding": {"OFF": 0, "ON": 1},
        "rules_used_for_training_labels": artifact["rules_used_for_training_labels"],
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "seed": args.seed,
        "test_size": args.test_size,
        "best_metrics": best_metrics,
        "all_model_metrics": results,
        "trained_at": trained_at,
    }

    joblib.dump(artifact, args.model_output)

    with args.metrics_output.open("w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    print("=" * 90)
    print("ACTUATOR CONTROL TRAINING RESULTS")
    print("=" * 90)
    print(f"Input dataset: {args.input}")
    print(f"Rows used: {len(df):,}")
    print(f"Train/Test: {len(x_train):,}/{len(x_test):,}")
    print()

    for model_name, metrics in results.items():
        print(
            f"{model_name:<12} | Subset Acc: {metrics['subset_accuracy'] * 100:6.2f}% | "
            f"Macro F1: {metrics['macro_f1'] * 100:6.2f}%"
        )

    print("-" * 90)
    print(f"Best model: {best_name}")
    print(f"Best subset accuracy: {best_metrics['subset_accuracy'] * 100:.2f}%")
    print(f"Best macro F1: {best_metrics['macro_f1'] * 100:.2f}%")
    print("Per-target accuracy:")
    for k, v in best_metrics["per_target_accuracy"].items():
        print(f"  - {k}: {v * 100:.2f}%")

    print("-" * 90)
    print(f"Model artifact saved: {args.model_output}")
    print(f"Metrics json saved:   {args.metrics_output}")


if __name__ == "__main__":
    main()
