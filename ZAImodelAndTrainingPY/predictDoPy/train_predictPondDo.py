from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split


CLASS_ORDER = ["Critical", "Low", "Warning", "Normal"]
CLASS_TO_DO = {
    "Critical": 4.5,
    "Low": 5.5,
    "Warning": 6.5,
    "Normal": 8.0,
}

CRITICAL_THRESHOLD = 5.0
CAUTION_LOW = 6.0
CAUTION_HIGH = 7.0
CAUTION_SHIFT = -1.0

SENSOR_BOUNDS = {
    "ph": (0.0, 14.0),
    "ammonia": (0.0, 5.0),
    "temp": (-5.0, 45.0),
    "turbidity": (0.0, 500.0),
    "do": (0.0, 20.0),
}
DO_BOUNDS_DEFAULT = SENSOR_BOUNDS["do"]


def _as_finite_float(name: str, value: object) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric, got {value!r}") from exc

    if not np.isfinite(out):
        raise ValueError(f"{name} must be a finite number, got {value!r}")

    return out


def validate_sensor_values(
    *,
    ph: object,
    ammonia: object,
    temp: object,
    turbidity: object,
    do: object | None = None,
    bounds: dict[str, tuple[float, float]] | None = None,
) -> dict[str, float]:
    """Validate and normalize one sensor payload for inference use."""
    active_bounds = bounds or SENSOR_BOUNDS

    values: dict[str, float] = {
        "ph": _as_finite_float("ph", ph),
        "ammonia": _as_finite_float("ammonia", ammonia),
        "temp": _as_finite_float("temp", temp),
        "turbidity": _as_finite_float("turbidity", turbidity),
    }
    if do is not None:
        values["do"] = _as_finite_float("do", do)

    for key, val in values.items():
        if key not in active_bounds:
            continue

        min_v, max_v = active_bounds[key]
        if val < min_v or val > max_v:
            raise ValueError(
                f"{key} out of allowed range [{min_v}, {max_v}] (got {val})"
            )

    return values


def clamp_do_predictions(pred_do: np.ndarray, do_bounds: tuple[float, float]) -> np.ndarray:
    lo, hi = float(do_bounds[0]), float(do_bounds[1])
    if hi < lo:
        raise ValueError(f"Invalid DO bounds: min={lo}, max={hi}")

    return np.clip(np.asarray(pred_do, dtype=float), lo, hi)


def summarize_observed_ranges(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    cols = ["ph", "ammonia", "temp", "turbidity", "do"]
    summary: dict[str, dict[str, float]] = {}
    for col in cols:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if series.empty:
            continue
        summary[col] = {
            "min": float(series.min()),
            "p01": float(series.quantile(0.01)),
            "p99": float(series.quantile(0.99)),
            "max": float(series.max()),
        }
    return summary


def do_band(values: pd.Series) -> pd.Series:
    # User rule: DO < 5 is Critical.
    return pd.cut(
        values,
        bins=[-np.inf, 5.0, 6.0, 7.0, np.inf],
        labels=CLASS_ORDER,
        right=False,
    ).astype(str)


def apply_conservative_do_policy(
    pred_do: np.ndarray,
    do_bounds: tuple[float, float] = DO_BOUNDS_DEFAULT,
) -> np.ndarray:
    # User rule: if DO is in [6, 7), subtract 1 for a conservative alert policy.
    out = np.asarray(pred_do, dtype=float).copy()
    mask = (out >= CAUTION_LOW) & (out < CAUTION_HIGH)
    out[mask] = out[mask] + CAUTION_SHIFT
    return clamp_do_predictions(out, do_bounds)


def labels_to_do(
    labels: np.ndarray,
    do_bounds: tuple[float, float] = DO_BOUNDS_DEFAULT,
) -> np.ndarray:
    raw = np.array([CLASS_TO_DO[str(label)] for label in labels], dtype=float)
    return apply_conservative_do_policy(raw, do_bounds=do_bounds)


def load_station1(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)

    required = ["PH", "AMMONIA(mg/l)", "TEMP", "TURBIDITY", "DO"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if "Date" in df.columns and "Time" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["Date"].astype(str) + " " + df["Time"].astype(str),
            dayfirst=True,
            errors="coerce",
        )
    else:
        df["timestamp"] = pd.NaT

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=required).copy()
    df = df.rename(
        columns={
            "PH": "ph",
            "AMMONIA(mg/l)": "ammonia",
            "TEMP": "temp",
            "TURBIDITY": "turbidity",
            "DO": "do",
        }
    )

    if df["timestamp"].notna().any():
        df = df.sort_values("timestamp").reset_index(drop=True)

    q_low, q_high = df["do"].quantile([0.01, 0.99])
    df = df[(df["do"] >= q_low) & (df["do"] <= q_high)].copy().reset_index(drop=True)

    return df


def build_features(df: pd.DataFrame, improved: bool) -> tuple[pd.DataFrame, pd.Series]:
    sensors = ["ph", "ammonia", "temp", "turbidity"]
    lag_steps = [1] if not improved else [1, 2, 3]
    rolling_windows = [] if not improved else [3]

    out = pd.DataFrame(index=df.index)
    for col in sensors:
        out[col] = df[col].astype(np.float32)

    if df["timestamp"].notna().any():
        hour = df["timestamp"].dt.hour.astype(float)
        out["hour_sin"] = np.sin(2.0 * np.pi * hour / 24.0).astype(np.float32)
        out["hour_cos"] = np.cos(2.0 * np.pi * hour / 24.0).astype(np.float32)

    for col in sensors:
        for lag in lag_steps:
            out[f"{col}_lag{lag}"] = df[col].shift(lag).astype(np.float32)

        if improved:
            out[f"{col}_diff1"] = (df[col] - df[col].shift(1)).astype(np.float32)

        shifted = df[col].shift(1)
        for win in rolling_windows:
            out[f"{col}_roll{win}_mean"] = shifted.rolling(win).mean().astype(np.float32)
            out[f"{col}_roll{win}_std"] = shifted.rolling(win).std().astype(np.float32)

    if improved:
        out["ph_sq"] = (out["ph"] ** 2).astype(np.float32)
        out["ammonia_sq"] = (out["ammonia"] ** 2).astype(np.float32)
        out["temp_sq"] = (out["temp"] ** 2).astype(np.float32)
        out["ph_ammonia"] = (out["ph"] * out["ammonia"]).astype(np.float32)
        out["temp_turbidity"] = (out["temp"] * out["turbidity"]).astype(np.float32)

    valid_mask = out.notna().all(axis=1)
    x = out.loc[valid_mask].copy()
    y = do_band(df.loc[valid_mask, "do"]).copy()

    return x, y


def baseline_model(seed: int | None) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=70,
        max_depth=10,
        min_samples_split=6,
        min_samples_leaf=3,
        max_features="sqrt",
        max_leaf_nodes=256,
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=seed,
    )


def improved_model(seed: int | None) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=120,
        max_depth=14,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features="sqrt",
        max_leaf_nodes=512,
        class_weight="balanced_subsample",
        n_jobs=-1,
        random_state=seed,
    )


def run_experiment(
    x: pd.DataFrame,
    y: pd.Series,
    model_factory: Callable[[int | None], RandomForestClassifier],
    runs: int,
    test_size: float,
    fixed_seed: int | None,
    do_bounds: tuple[float, float],
) -> dict[str, object]:
    rng = np.random.default_rng(fixed_seed)

    rows: list[dict[str, object]] = []
    best: dict[str, object] | None = None

    for i in range(1, runs + 1):
        split_seed = int(rng.integers(0, 2_147_483_647))
        model_seed = int(rng.integers(0, 2_147_483_647))

        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            test_size=test_size,
            stratify=y,
            shuffle=True,
            random_state=split_seed,
        )

        model = model_factory(model_seed)
        model.fit(x_train, y_train)
        pred = model.predict(x_test)

        acc = float(accuracy_score(y_test, pred))
        f1_macro = float(f1_score(y_test, pred, average="macro", zero_division=0))
        pred_unique = sorted(pd.Series(pred).unique().tolist())

        y_test_arr = y_test.to_numpy(dtype=str)
        pred_arr = np.asarray(pred, dtype=str)

        critical_mask = y_test_arr == "Critical"
        if np.any(critical_mask):
            critical_recall = float(np.mean(pred_arr[critical_mask] == "Critical"))
        else:
            critical_recall = 0.0

        pred_do = labels_to_do(pred_arr, do_bounds=do_bounds)
        predicted_critical_rate = float(np.mean(pred_do < CRITICAL_THRESHOLD))

        result = {
            "run": i,
            "split_seed": split_seed,
            "model_seed": model_seed,
            "accuracy": acc,
            "f1_macro": f1_macro,
            "critical_recall": critical_recall,
            "predicted_critical_rate": predicted_critical_rate,
            "unique_pred_classes": pred_unique,
            "unique_pred_count": len(pred_unique),
        }
        rows.append(result)

        if best is None or f1_macro > float(best["f1_macro"]):
            report = classification_report(
                y_test_arr,
                pred_arr,
                labels=CLASS_ORDER,
                zero_division=0,
                digits=4,
            )
            pred_dist = pd.Series(pred_arr).value_counts(normalize=True).to_dict()
            best = {
                **result,
                "model": model,
                "report": report,
                "pred_distribution": pred_dist,
                "feature_columns": x.columns.tolist(),
            }

    if best is None:
        raise RuntimeError("No experiment runs were completed")

    acc_values = np.array([float(r["accuracy"]) for r in rows], dtype=float)
    f1_values = np.array([float(r["f1_macro"]) for r in rows], dtype=float)
    crit_values = np.array([float(r["critical_recall"]) for r in rows], dtype=float)

    return {
        "runs": rows,
        "summary": {
            "accuracy_mean": float(np.mean(acc_values)),
            "accuracy_std": float(np.std(acc_values)),
            "f1_macro_mean": float(np.mean(f1_values)),
            "f1_macro_std": float(np.std(f1_values)),
            "critical_recall_mean": float(np.mean(crit_values)),
            "critical_recall_std": float(np.std(crit_values)),
            "n_runs": runs,
        },
        "best": best,
    }


def print_run_table(title: str, info: dict[str, object]) -> None:
    summary = info["summary"]
    runs = info["runs"]

    print("\n" + "=" * 104)
    print(title)
    print("=" * 104)
    print("Run | Accuracy | F1-macro | Critical recall | Pred critical rate | Pred classes")
    print("-" * 104)
    for row in runs:
        print(
            f"{int(row['run']):>3} | "
            f"{float(row['accuracy']) * 100:7.2f}% | "
            f"{float(row['f1_macro']) * 100:8.2f}% | "
            f"{float(row['critical_recall']) * 100:14.2f}% | "
            f"{float(row['predicted_critical_rate']) * 100:18.2f}% | "
            f"{int(row['unique_pred_count'])}"
        )

    print("-" * 104)
    print(
        "Mean: "
        f"Acc={float(summary['accuracy_mean']) * 100:.2f}% +/- {float(summary['accuracy_std']) * 100:.2f} | "
        f"F1={float(summary['f1_macro_mean']) * 100:.2f}% +/- {float(summary['f1_macro_std']) * 100:.2f} | "
        f"CriticalRecall={float(summary['critical_recall_mean']) * 100:.2f}% +/- {float(summary['critical_recall_std']) * 100:.2f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Station1 compact RandomForest classifier")
    parser.add_argument("--runs", type=int, default=3, help="Number of random train/test runs")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test split ratio")
    parser.add_argument(
        "--fixed-seed",
        type=int,
        default=None,
        help="Optional fixed seed for repeatable runs. Leave unset for dynamic non-fixed results.",
    )
    parser.add_argument(
        "--include-runs",
        action="store_true",
        help="Include per-run history inside the artifact (slightly larger file)",
    )
    parser.add_argument(
        "--do-min",
        type=float,
        default=DO_BOUNDS_DEFAULT[0],
        help="Lower clamp bound for predicted DO values",
    )
    parser.add_argument(
        "--do-max",
        type=float,
        default=DO_BOUNDS_DEFAULT[1],
        help="Upper clamp bound for predicted DO values",
    )
    args = parser.parse_args()

    if args.do_max <= args.do_min:
        raise ValueError(f"Invalid DO bounds: do-min={args.do_min}, do-max={args.do_max}")

    do_bounds = (float(args.do_min), float(args.do_max))

    script_dir = Path(__file__).resolve().parent
    data_path = script_dir / "withTimePondData_station1.csv"
    out_path = script_dir / "predictPondDo.pkl"

    print("=" * 104)
    print("STATION1 RANDOM FOREST CLASSIFIER - RANGE POLICY + COMPACT ARTIFACT")
    print("=" * 104)
    print(f"Data: {data_path}")
    print(f"Runs: {args.runs} | Test size: {args.test_size}")
    print("Ranges: Critical <5, Low 5-6, Warning 6-7, Normal >=7")
    print("Policy: predicted DO in [6, 7) is shifted by -1.0 for conservative safety")
    print(f"DO clamp: [{do_bounds[0]:.2f}, {do_bounds[1]:.2f}] mg/L")
    if args.fixed_seed is None:
        print("Seed mode: dynamic (results are not fixed)")
    else:
        print(f"Seed mode: fixed ({args.fixed_seed})")

    df = load_station1(data_path)
    observed_ranges = summarize_observed_ranges(df)
    print(f"Rows after cleaning: {len(df):,}")

    y_band = do_band(df["do"])
    print("DO class distribution (%):")
    print((y_band.value_counts(normalize=True) * 100.0).round(2).sort_index())

    x_base, y_base = build_features(df, improved=False)
    x_improved, y_improved = build_features(df, improved=True)

    print(f"\nBaseline features: {x_base.shape[1]} | Rows used: {x_base.shape[0]:,}")
    print(f"Improved features: {x_improved.shape[1]} | Rows used: {x_improved.shape[0]:,}")

    base_info = run_experiment(
        x=x_base,
        y=y_base,
        model_factory=baseline_model,
        runs=args.runs,
        test_size=args.test_size,
        fixed_seed=args.fixed_seed,
        do_bounds=do_bounds,
    )

    improved_info = run_experiment(
        x=x_improved,
        y=y_improved,
        model_factory=improved_model,
        runs=args.runs,
        test_size=args.test_size,
        fixed_seed=args.fixed_seed,
        do_bounds=do_bounds,
    )

    print_run_table("BASELINE RANDOM FOREST", base_info)
    print_run_table("IMPROVED RANDOM FOREST", improved_info)

    base_summary = base_info["summary"]
    improved_summary = improved_info["summary"]

    acc_gain = float(improved_summary["accuracy_mean"]) - float(base_summary["accuracy_mean"])
    f1_gain = float(improved_summary["f1_macro_mean"]) - float(base_summary["f1_macro_mean"])

    best_improved = improved_info["best"]

    print("\n" + "=" * 104)
    print("COMPARISON")
    print("=" * 104)
    print(f"Accuracy gain (mean): {acc_gain * 100:.2f}%")
    print(f"F1-macro gain (mean): {f1_gain * 100:.2f}%")
    print(f"Best improved run F1-macro: {float(best_improved['f1_macro']) * 100:.2f}%")
    print(f"Best improved run critical recall: {float(best_improved['critical_recall']) * 100:.2f}%")
    print(f"Best improved run predicted classes: {best_improved['unique_pred_classes']}")

    if float(improved_summary["accuracy_mean"]) >= 0.70:
        print("Status: Target reached (>=70% classification accuracy).")
    else:
        print("Status: Below 70% accuracy; more data/features are required.")

    print("\nBest improved run classification report:")
    print(best_improved["report"])

    artifact = {
        "model": best_improved["model"],
        "feature_columns": best_improved["feature_columns"],
        "class_order": CLASS_ORDER,
        "class_to_do": CLASS_TO_DO,
        "range_policy": {
            "critical_threshold": CRITICAL_THRESHOLD,
            "warning_range": [CAUTION_LOW, CAUTION_HIGH],
            "warning_shift": CAUTION_SHIFT,
            "do_output_bounds": {
                "min": do_bounds[0],
                "max": do_bounds[1],
                "unit": "mg/L",
                "reason": "Clamp model output to realistic physical DO range",
            },
        },
        "input_validation": {
            "required_fields": ["ph", "ammonia", "temp", "turbidity"],
            "optional_fields": ["do"],
            "bounds": {
                k: {"min": float(v[0]), "max": float(v[1])}
                for k, v in SENSOR_BOUNDS.items()
            },
            "reject_rule": "Reject non-numeric, non-finite, or out-of-range sensor values before inference",
        },
        "observed_training_ranges": observed_ranges,
        "data_file": str(data_path),
        "mode": {
            "dynamic_results": args.fixed_seed is None,
            "runs": args.runs,
            "test_size": args.test_size,
            "fixed_seed": args.fixed_seed,
        },
        "baseline": {
            "summary": base_summary,
        },
        "improved": {
            "summary": improved_summary,
            "best": {
                "run": best_improved["run"],
                "split_seed": best_improved["split_seed"],
                "model_seed": best_improved["model_seed"],
                "accuracy": best_improved["accuracy"],
                "f1_macro": best_improved["f1_macro"],
                "critical_recall": best_improved["critical_recall"],
                "pred_distribution": best_improved["pred_distribution"],
                "report": best_improved["report"],
            },
        },
    }

    if args.include_runs:
        artifact["baseline"]["runs"] = base_info["runs"]
        artifact["improved"]["runs"] = improved_info["runs"]

    joblib.dump(artifact, out_path, compress=9)

    size_mb = out_path.stat().st_size / (1024.0 * 1024.0)
    print(f"\nSaved compact classifier artifact: {out_path}")
    print(f"Artifact size: {size_mb:.2f} MB")
    if size_mb <= 20.0:
        print("Docker note: artifact size is compact and suitable for lightweight container images.")
    else:
        print("Docker note: artifact is still large; lower n_estimators/max_depth further if needed.")


if __name__ == "__main__":
    main()
