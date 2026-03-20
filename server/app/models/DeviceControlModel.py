# app/core/ml.py
import os
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _candidate_model_paths():
    """Ordered model path candidates for device control."""
    return [
        # Preferred model requested by user
        os.path.join(BASE_DIR, "..", "ai", "4ParamPondControl.pkl"),
        # Project-level alternatives
        os.path.join(BASE_DIR, "..", "..", "..", "ZAImodelAndTrainingPY", "4ParamPondControl.pkl"),
        os.path.join(BASE_DIR, "..", "..", "..", "z-AI", "AImodelAndTrainingPY", "4ParamPondControl.pkl"),
        # Legacy fallbacks
        os.path.join(BASE_DIR, "trained_model.pkl"),
        os.path.join(BASE_DIR, "..", "core", "trained_model.pkl"),
    ]

def load_model():
    """Load trained AI model"""
    for path in _candidate_model_paths():
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            print(f"✅ DeviceControlModel loaded from: {abs_path}")
            return joblib.load(abs_path)

    raise FileNotFoundError(
        "Device control model not found. Expected one of: "
        + ", ".join(os.path.abspath(p) for p in _candidate_model_paths())
    )

# Load model once
model = load_model()

# Labels predicted by the AI model
LABELS = [
    'LOW_TEMP',
    'LOW_DO',
    'HIGH_AMMONIA',
    'PH_IMBALANCE',
    'HIGH_TURBIDITY'
]

# Map AI labels to physical devices
DEVICE_MAP = {
    'LOW_TEMP': 'Heater',
    'LOW_DO': 'Aerator',
    'HIGH_AMMONIA': 'Water Pump',
    'PH_IMBALANCE': 'Water Pump',
    'HIGH_TURBIDITY': 'Water Pump'
}