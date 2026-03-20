from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from station1_random_classifier_improved import (
    apply_conservative_do_policy,
    build_features,
    do_band,
    load_station1,
)


def map_to_three_class(label: str) -> str:
    # Supports both old 4-class and new 5-class label sets.
    if label in {"Normal", "Good", "Excellent"}:
        return "Good"
    if label in {"Warning", "Fair"}:
        return "Warning"
    return "Danger"


def proba_to_dynamic_do(
    probabilities: np.ndarray,
    class_labels: list[str],
    class_to_do: dict[str, float],
    calibrator: object | None,
) -> np.ndarray:
    # Prefer calibrated dynamic DO when available in artifact.
    if calibrator is not None and hasattr(calibrator, "predict"):
        raw = np.asarray(calibrator.predict(probabilities), dtype=float)
        return apply_conservative_do_policy(raw)

    # Fallback: expected value using class anchors from artifact.
    anchors = np.array([float(class_to_do[c]) for c in class_labels], dtype=float)
    raw = probabilities @ anchors
    return apply_conservative_do_policy(raw)


def resolve_data_path(base: Path) -> Path:
    candidates = [
        base / "withTimePondData_station1.csv",
        base.parent / "DODO" / "model" / "station1Traing" / "withTimePondData_station1.csv",
        base.parent / "DODO" / "model" / "newTraining" / "withTimePondData_station1.csv",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("withTimePondData_station1.csv was not found in expected locations")


def format_table(df: pd.DataFrame) -> list[str]:
    lines = [
        "| No | PH | AMMONIA | TEMP | TURBIDITY | Actual DO | Actual Result | Predicted Result | Predicted Class (4-class) | Pred DO Dynamic | Match |",
        "|---:|---:|--------:|-----:|----------:|----------:|--------------|------------------|---------------------------|----------------:|:-----:|",
    ]

    for i, row in enumerate(df.itertuples(index=False), start=1):
        lines.append(
            "| "
            f"{i} | "
            f"{row.ph:.4f} | "
            f"{row.ammonia:.4f} | "
            f"{row.temp:.4f} | "
            f"{row.turbidity:.4f} | "
            f"{row.actual_do:.4f} | "
            f"{row.actual_result} | "
            f"{row.predicted_result} | "
            f"{row.predicted_class_4} | "
            f"{row.predicted_do_dynamic:.4f} | "
            f"{'Yes' if row.match else 'No'} |"
        )

    return lines


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 3-class sample markdown with dynamic predictions from compact classifier"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional base seed for reproducible output. Leave unset for dynamic output each run.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Holdout ratio for evaluation split.",
    )
    parser.add_argument(
        "--samples-per-group",
        type=int,
        default=20,
        help="Rows to include per Good/Warning/Danger group.",
    )
    parser.add_argument(
        "--temporal",
        action="store_true",
        help="Use temporal sampling (consecutive rows) for realistic slow-changing water parameters.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="MODEL_SAMPLE_RESULTS_3CLASS.md",
        help="Output markdown filename.",
    )
    args = parser.parse_args()

    if not (0.0 < args.test_size < 1.0):
        raise ValueError("--test-size must be between 0 and 1")
    if args.samples_per_group <= 0:
        raise ValueError("--samples-per-group must be positive")

    base = Path(__file__).resolve().parent
    model_path = base / "station1_random_classifier_compact.pkl"
    out_md = base / args.output

    rng = np.random.default_rng(args.seed)
    split_seed = int(rng.integers(0, 2_147_483_647))

    data_path = resolve_data_path(base)

    artifact = joblib.load(model_path)
    model = artifact["model"]
    feature_columns = artifact["feature_columns"]
    do_calibrator = artifact.get("do_calibrator")
    class_to_do = artifact.get("class_to_do", {
        "Critical": 4.5,
        "Low": 5.5,
        "Warning": 6.5,
        "Normal": 8.0,
    })

    df = load_station1(data_path)
    x, _ = build_features(df, improved=True)

    x = x[feature_columns].copy()
    do_true = df.loc[x.index, "do"].to_numpy(dtype=float)
    y_true_4 = do_band(pd.Series(do_true, index=x.index)).to_numpy(dtype=str)
    
    # Store original indices for temporal sampling
    original_idx = x.index.to_numpy()

    _, x_test, _, y_test_4, _, do_test, _, test_idx = train_test_split(
        x,
        y_true_4,
        do_true,
        original_idx,
        test_size=args.test_size,
        random_state=split_seed,
        shuffle=True,
        stratify=y_true_4,
    )

    pred_4 = np.asarray(model.predict(x_test), dtype=str)
    pred_proba = model.predict_proba(x_test)
    class_labels = [str(c) for c in model.classes_]
    pred_do_dynamic = proba_to_dynamic_do(pred_proba, class_labels, class_to_do, do_calibrator)

    actual_3 = np.array([map_to_three_class(v) for v in y_test_4], dtype=str)
    pred_3 = np.array([map_to_three_class(v) for v in pred_4], dtype=str)

    report_df = pd.DataFrame(
        {
            "original_idx": test_idx,
            "ph": x_test["ph"].to_numpy(dtype=float),
            "ammonia": x_test["ammonia"].to_numpy(dtype=float),
            "temp": x_test["temp"].to_numpy(dtype=float),
            "turbidity": x_test["turbidity"].to_numpy(dtype=float),
            "actual_do": do_test,
            "actual_result": actual_3,
            "predicted_result": pred_3,
            "predicted_class_4": pred_4,
            "predicted_do_dynamic": pred_do_dynamic,
            "match": actual_3 == pred_3,
        }
    )

    sections = ["Good", "Warning", "Danger"]
    sampled = {}
    for label in sections:
        subset = report_df[report_df["actual_result"] == label].copy()
        take_n = min(args.samples_per_group, len(subset))
        
        if args.temporal:
            # Sort by original index (time order) and take consecutive rows
            # This shows realistic slow-changing water parameters
            subset = subset.sort_values("original_idx")
            # Find a continuous segment if possible, or take the first consecutive rows
            if len(subset) >= take_n:
                # Take first consecutive block for realistic gradual changes
                sampled[label] = subset.head(take_n).reset_index(drop=True)
            else:
                sampled[label] = subset.reset_index(drop=True)
        else:
            # Random sampling (original behavior)
            sample_seed = int(rng.integers(0, 2_147_483_647))
            sampled[label] = subset.sample(n=take_n, random_state=sample_seed).reset_index(drop=True)

    lines: list[str] = []
    lines.append("# Sample Prediction Results (Good / Warning / Danger)")
    lines.append("")
    lines.append("- Source model: `station1_random_classifier_compact.pkl`")
    lines.append(f"- Source data: `{data_path}`")
    if args.seed is None:
        lines.append(f"- Split: dynamic holdout (test_size={args.test_size}, split_seed={split_seed})")
        if args.temporal:
            lines.append("- Sampling mode: **temporal (consecutive time-ordered rows for realistic gradual parameter changes)**")
        else:
            lines.append("- Sampling mode: dynamic (new random rows each run)")
    else:
        lines.append(
            f"- Split: reproducible holdout (--seed={args.seed}, test_size={args.test_size}, split_seed={split_seed})"
        )
        if args.temporal:
            lines.append("- Sampling mode: **temporal (consecutive time-ordered rows for realistic gradual parameter changes)**")
        else:
            lines.append("- Sampling mode: reproducible")
    lines.append("- Label mapping used in this report:")
    lines.append("  - Good: Normal")
    lines.append("  - Warning: Warning")
    lines.append("  - Danger: Critical + Low")
    if do_calibrator is not None:
        lines.append("- Pred DO Dynamic = calibrated DO from `do_calibrator` in model artifact")
    else:
        lines.append("- Pred DO Dynamic = expected DO from `predict_proba` using `class_to_do` inside model artifact")
    lines.append("- Predicted class/result comes directly from the classifier in the `.pkl` model")
    lines.append(f"- Requested rows per section: {args.samples_per_group}")
    lines.append("")

    for label in sections:
        chunk = sampled[label]
        group_acc = float(chunk["match"].mean() * 100.0)
        lines.append(f"## {label} ({len(chunk)} samples)")
        lines.append("")
        lines.append(f"- Group match rate (Predicted Result vs Actual Result): **{group_acc:.2f}%**")
        lines.append("")
        # Drop original_idx column before formatting table
        chunk_for_table = chunk.drop(columns=["original_idx"], errors="ignore")
        lines.extend(format_table(chunk_for_table))
        lines.append("")

    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Created: {out_md}")


if __name__ == "__main__":
    main()
