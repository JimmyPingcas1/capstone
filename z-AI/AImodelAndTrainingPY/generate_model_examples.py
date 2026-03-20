"""
Generate example prediction files using actual model predictions for SAFE/WARNING/DANGER scenarios.
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

# Paths
MODEL_4PARAM = Path(r"c:\Users\USER\Desktop\capstone\z-AI\AzforProductionFinal\4ParametersPkl.pkl")
MODEL_5PARAM = Path(r"c:\Users\USER\Desktop\capstone\z-AI\AzforProductionFinal\pondContol.pkl")
MODEL_DO = Path(r"c:\Users\USER\Desktop\capstone\z-AI\DODO\model\station1Traing\predictPondDo.pkl")
OUTPUT_DIR = Path(__file__).resolve().parent / "example"

# Load models
print("Loading models...")
model_4param = joblib.load(MODEL_4PARAM)
model_5param = joblib.load(MODEL_5PARAM)
model_do = joblib.load(MODEL_DO)
print("Models loaded successfully.\n")

# Status computation functions
def compute_status(df):
    """Compute status columns from sensor values."""
    df = df.copy()
    df["pH_Status"] = np.where((df["pH"] >= 6.5) & (df["pH"] <= 8.5), 1, 0)  # High=1, Low=0
    df["Ammonia_Status"] = np.where(df["Ammonia"] <= 0.05, 1, 0)
    df["Temp_Status"] = np.where(df["Temp"] >= 26.0, 1, 0)
    df["Turbidity_Status"] = np.where(df["Turbidity"] <= 20.0, 1, 0)
    if "DO" in df.columns:
        df["DO_Status"] = np.where(df["DO"] >= 6.0, 1, 0)
    return df

def decode_actuators(predictions, col_name):
    """Decode actuator predictions from 0/1 to OFF/ON."""
    return ["OFF" if p == 0 else "ON" for p in predictions[col_name].values]


def _format_cell(value, decimals=None):
    """Format values compactly for readable markdown source tables."""
    if isinstance(value, (np.integer, int)):
        return str(int(value))
    if isinstance(value, (np.floating, float)):
        if decimals is None:
            text = f"{float(value):.6f}"
        else:
            text = f"{float(value):.{decimals}f}"
        return text.rstrip("0").rstrip(".")
    return str(value)


def to_aligned_markdown(df, decimals_by_col=None):
    """Build markdown table with perfectly aligned pipes in source code."""
    decimals_by_col = decimals_by_col or {}
    cols = list(df.columns)
    
    # Format all cells
    formatted_rows = []
    for row in df.itertuples(index=False, name=None):
        formatted_rows.append(
            [_format_cell(val, decimals_by_col.get(col)) for col, val in zip(cols, row)]
        )
    
    # Calculate column widths from header AND data
    widths = []
    for c_idx, col in enumerate(cols):
        header_width = len(col)
        data_widths = [len(r[c_idx]) for r in formatted_rows]
        max_data_width = max(data_widths) if data_widths else 0
        width = max(header_width, max_data_width)
        widths.append(width)
    
    # Determine if columns are numeric for alignment
    numeric_cols = [pd.api.types.is_numeric_dtype(df[col]) for col in cols]
    
    # Build fully padded rows
    lines = []
    
    # Header row - left align all header text
    header_cells = [f"{col:<{widths[i]}}" for i, col in enumerate(cols)]
    lines.append("|" + "|".join(header_cells) + "|")
    
    # Divider row - use dashes matching the width
    divider_cells = ["-" * widths[i] for i in range(len(cols))]
    lines.append("|" + "|".join(divider_cells) + "|")
    
    # Data rows - numeric right-aligned, text left-aligned
    for row in formatted_rows:
        cells = []
        for i, cell in enumerate(row):
            if numeric_cols[i]:
                cells.append(f"{cell:>{widths[i]}}")
            else:
                cells.append(f"{cell:<{widths[i]}}")
        lines.append("|" + "|".join(cells) + "|")
    return "\n".join(lines)

# Feature engineering for DO model
def build_features_for_do_model(df):
    """Build engineered features required by DO model."""
    df = df.copy()
    df = df.rename(columns={"pH": "ph", "Ammonia": "ammonia", "Temp": "temp", "Turbidity": "turbidity"})
    
    # For simplicity, assume hour = 12 (noon)
    hour = 12
    df['hour_sin'] = np.sin(2 * np.pi * hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * hour / 24)
    
    # Lag features - use current value for all lags (no history)
    for var in ['ph', 'ammonia', 'temp', 'turbidity']:
        df[f'{var}_lag1'] = df[var]
        df[f'{var}_lag2'] = df[var]
        df[f'{var}_lag3'] = df[var]
        df[f'{var}_diff1'] = 0.0  # No change
        df[f'{var}_roll3_mean'] = df[var]
        df[f'{var}_roll3_std'] = 0.0  # No variation
    
    # Interaction features
    df['ph_sq'] = df['ph'] ** 2
    df['ammonia_sq'] = df['ammonia'] ** 2
    df['temp_sq'] = df['temp'] ** 2
    df['ph_ammonia'] = df['ph'] * df['ammonia']
    df['temp_turbidity'] = df['temp'] * df['turbidity']
    
    # Select features in correct order
    feature_cols = model_do['feature_columns']
    return df[feature_cols]

def predict_do_class(df):
    """Predict DO value using probability-weighted predictions for dynamic output."""
    X = build_features_for_do_model(df)
    
    # Get probability distribution across all classes
    probabilities = model_do['model'].predict_proba(X)
    
    # Get class order and DO values
    class_order = model_do['class_order']
    class_to_do = model_do['class_to_do']
    do_class_values = [class_to_do[cls] for cls in class_order]
    
    # Calculate weighted average DO based on probabilities
    do_values = []
    for prob in probabilities:
        weighted_do = sum(p * v for p, v in zip(prob, do_class_values))
        do_values.append(round(weighted_do, 2))
    
    # Map to water quality class based on continuous prediction
    water_class = []
    for val in do_values:
        if val >= 7.5:
            water_class.append("Excellent")
        elif val >= 6.5:
            water_class.append("Good")
        elif val >= 5.0:
            water_class.append("Fair")
        else:
            water_class.append("Poor")
    
    return water_class, do_values

# ========================================
# Generate scenarios
# ========================================

# SAFE scenarios (20 samples) - all parameters within optimal range
np.random.seed(42)
safe_ph = np.random.uniform(6.5, 8.5, 20).round(1)
safe_ammonia = np.random.uniform(0.015, 0.045, 20).round(4)
safe_temp = np.random.uniform(26.0, 33.0, 20).round(1)
safe_turbidity = np.random.randint(15, 21, 20)
safe_do = np.random.uniform(6.0, 8.5, 20).round(1)

# WARNING scenarios (20 samples) - some parameters out of range
warning_ph = np.concatenate([
    np.random.uniform(5.0, 6.0, 15).round(1),  # Low pH
    np.random.uniform(6.5, 7.5, 5).round(1)     # Normal pH but with other issues
])
warning_ammonia = np.concatenate([
    np.random.uniform(0.010, 0.045, 15).round(4),
    np.random.uniform(0.015, 0.045, 5).round(4)
])
warning_temp = np.concatenate([
    np.random.uniform(21.0, 26.0, 19).round(1),  # Low temp
    np.random.uniform(23.0, 26.0, 1).round(1)
])
warning_turbidity = np.concatenate([
    np.random.randint(18, 21, 15),
    np.random.randint(28, 35, 5)  # High turbidity
])
warning_do = np.concatenate([
    np.random.uniform(6.0, 8.5, 15).round(1),
    np.random.uniform(5.0, 6.0, 5).round(1)  # Low DO
])

# DANGER scenarios (20 samples) - multiple critical parameters
danger_ph = np.random.uniform(5.0, 5.8, 20).round(1)
danger_ammonia = np.concatenate([
    np.random.uniform(0.010, 0.020, 10).round(4),
    np.random.uniform(0.060, 0.095, 10).round(4)  # High ammonia
])
danger_temp = np.random.uniform(21.0, 25.0, 20).round(1)
danger_turbidity = np.concatenate([
    np.random.randint(18, 24, 10),
    np.random.randint(27, 35, 10)  # High turbidity
])
danger_do = np.concatenate([
    np.random.uniform(9.5, 12.0, 10).round(1),  # High DO (supersaturated)
    np.random.uniform(4.0, 5.5, 10).round(1)   # Low DO
])

# ========================================
# Generate 4-param predictions
# ========================================
print("Generating 4-param predictions...")

def generate_4param_predictions(ph, ammonia, temp, turbidity, scenario_name):
    df = pd.DataFrame({
        'pH': ph,
        'Ammonia': ammonia,
        'Temp': temp,
        'Turbidity': turbidity
    })
    
    # Compute status columns
    df = compute_status(df)
    
    # Prepare features in correct order
    X = df[model_4param['feature_columns']]
    
    # Predict
    pred = model_4param['model'].predict(X)
    pred_df = pd.DataFrame(pred, columns=model_4param['target_columns'])
    
    # Decode actuators
    water_pump = decode_actuators(pred_df, 'Water Pump')
    heater = decode_actuators(pred_df, 'Heater')
    
    # Build output table with proper formatting
    result = pd.DataFrame({
        'pH': df['pH'].round(1),
        'N': df['Ammonia'].round(4),
        'T': df['Temp'].round(1),
        'Tb': df['Turbidity'].astype(int),
        'pS': df['pH_Status'].values,
        'nS': df['Ammonia_Status'].values,
        'tS': df['Temp_Status'].values,
        'tbS': df['Turbidity_Status'].values,
        'P': water_pump,
        'H': heater
    })
    
    return result

safe_4param = generate_4param_predictions(safe_ph, safe_ammonia, safe_temp, safe_turbidity, "SAFE")
warning_4param = generate_4param_predictions(warning_ph, warning_ammonia, warning_temp, warning_turbidity, "WARNING")
danger_4param = generate_4param_predictions(danger_ph, danger_ammonia, danger_temp, danger_turbidity, "DANGER")

# Write to markdown
output_4param = OUTPUT_DIR / "4params.md"
with open(output_4param, 'w') as f:
    f.write("# 4params\n\n")
    f.write("Legend: N=Ammonia, Tb=Turbidity, pS/nS/tS/tbS=Status flags, P=Pump, H=Heater\n\n")
    
    f.write("## SAFE (20)\n\n")
    f.write(
        to_aligned_markdown(
            safe_4param,
            {
                "pH": 1,
                "N": 4,
                "T": 1,
                "Tb": 0,
            },
        )
    )
    f.write("\n\n")
    
    f.write("## WARNING (20)\n\n")
    f.write(
        to_aligned_markdown(
            warning_4param,
            {
                "pH": 1,
                "N": 4,
                "T": 1,
                "Tb": 0,
            },
        )
    )
    f.write("\n\n")
    
    f.write("## DANGER (20)\n\n")
    f.write(
        to_aligned_markdown(
            danger_4param,
            {
                "pH": 1,
                "N": 4,
                "T": 1,
                "Tb": 0,
            },
        )
    )
    f.write("\n")

print(f"Written: {output_4param}")

# ========================================
# Generate 5-param predictions
# ========================================
print("Generating 5-param predictions...")

def generate_5param_predictions(ph, ammonia, temp, do, turbidity, scenario_name):
    df = pd.DataFrame({
        'pH': ph,
        'Ammonia': ammonia,
        'Temp': temp,
        'DO': do,
        'Turbidity': turbidity
    })
    
    # Compute status columns
    df = compute_status(df)
    
    # Prepare features in correct order
    X = df[model_5param['feature_columns']]
    
    # Predict
    pred = model_5param['model'].predict(X)
    pred_df = pd.DataFrame(pred, columns=model_5param['target_columns'])
    
    # Decode actuators
    aerator = decode_actuators(pred_df, 'Aerator')
    water_pump = decode_actuators(pred_df, 'Water Pump')
    heater = decode_actuators(pred_df, 'Heater')
    
    # Build output table with proper formatting
    result = pd.DataFrame({
        'pH': df['pH'].round(1),
        'N': df['Ammonia'].round(2),
        'T': df['Temp'].round(1),
        'DO': df['DO'].round(1),
        'Tb': df['Turbidity'].astype(int),
        'A': aerator,
        'P': water_pump,
        'H': heater
    })
    
    return result

safe_5param = generate_5param_predictions(safe_ph, safe_ammonia, safe_temp, safe_do, safe_turbidity, "SAFE")
warning_5param = generate_5param_predictions(warning_ph, warning_ammonia, warning_temp, warning_do, warning_turbidity, "WARNING")
danger_5param = generate_5param_predictions(danger_ph, danger_ammonia, danger_temp, danger_do, danger_turbidity, "DANGER")

# Write to markdown
output_5param = OUTPUT_DIR / "5params.md"
with open(output_5param, 'w') as f:
    f.write("# 5params\n\n")
    f.write("Legend: N=Ammonia, Tb=Turbidity, A=Aerator, P=Pump, H=Heater\n\n")
    
    f.write("## SAFE (20)\n\n")
    f.write(
        to_aligned_markdown(
            safe_5param,
            {
                "pH": 1,
                "N": 2,
                "T": 1,
                "DO": 1,
                "Tb": 0,
            },
        )
    )
    f.write("\n\n")
    
    f.write("## WARNING (20)\n\n")
    f.write(
        to_aligned_markdown(
            warning_5param,
            {
                "pH": 1,
                "N": 2,
                "T": 1,
                "DO": 1,
                "Tb": 0,
            },
        )
    )
    f.write("\n\n")
    
    f.write("## DANGER (20)\n\n")
    f.write(
        to_aligned_markdown(
            danger_5param,
            {
                "pH": 1,
                "N": 2,
                "T": 1,
                "DO": 1,
                "Tb": 0,
            },
        )
    )
    f.write("\n")

print(f"Written: {output_5param}")

# ========================================
# Generate DO predictions
# ========================================
print("Generating DO predictions...")

def generate_do_predictions(ph, ammonia, temp, turbidity, do_actual, scenario_name):
    df = pd.DataFrame({
        'pH': ph,
        'Ammonia': ammonia,
        'Temp': temp,
        'Turbidity': turbidity
    })
    
    # Predict DO class and value
    water_class, pred_do = predict_do_class(df)
    
    # Build output table with proper formatting
    result = pd.DataFrame({
        'pH': df['pH'].round(1),
        'N': df['Ammonia'].round(2),
        'T': df['Temp'].round(1),
        'Tb': df['Turbidity'].astype(int),
        'DO': [round(d, 1) for d in do_actual],
        'C': water_class,
        'pDO': [round(p, 2) for p in pred_do]
    })
    
    return result

safe_do_pred = generate_do_predictions(safe_ph, safe_ammonia, safe_temp, safe_turbidity, safe_do, "SAFE")
warning_do_pred = generate_do_predictions(warning_ph, warning_ammonia, warning_temp, warning_turbidity, warning_do, "WARNING")
danger_do_pred = generate_do_predictions(danger_ph, danger_ammonia, danger_temp, danger_turbidity, danger_do, "DANGER")

# Write to markdown
output_do = OUTPUT_DIR / "DOprediction.md"
with open(output_do, 'w') as f:
    f.write("# DOprediction\n\n")
    f.write("Legend: N=Ammonia, Tb=Turbidity, C=Class, pDO=Predicted DO\n\n")
    
    f.write("## SAFE (20)\n\n")
    f.write(
        to_aligned_markdown(
            safe_do_pred,
            {
                "pH": 1,
                "N": 2,
                "T": 1,
                "Tb": 0,
                "DO": 1,
                "pDO": 2,
            },
        )
    )
    f.write("\n\n")
    
    f.write("## WARNING (20)\n\n")
    f.write(
        to_aligned_markdown(
            warning_do_pred,
            {
                "pH": 1,
                "N": 2,
                "T": 1,
                "Tb": 0,
                "DO": 1,
                "pDO": 2,
            },
        )
    )
    f.write("\n\n")
    
    f.write("## DANGER (20)\n\n")
    f.write(
        to_aligned_markdown(
            danger_do_pred,
            {
                "pH": 1,
                "N": 2,
                "T": 1,
                "Tb": 0,
                "DO": 1,
                "pDO": 2,
            },
        )
    )
    f.write("\n")

print(f"Written: {output_do}")

print("\n=== All example files generated successfully! ===")
