# pondControl Model Training (5-Parameter Actuator Control)

This folder contains the training script for the 5-parameter actuator control model (Aerator, Water Pump, Heater).

## Files
- `train_pondControl.py` - Training script for full actuator control model
- `withTimePondData_station1.csv` - Training dataset
- `pondControl.pkl` - Output trained model (generated after training)
- `pondControl_metrics.json` - Training metrics (generated after training)

## Model Details
- **Purpose**: Predicts actuator states (ON/OFF) for Aerator, Water Pump, and Heater
- **Input features**: pH, Ammonia, Temp, DO, Turbidity (5 sensors)
- **Output targets**: Aerator, Water Pump, Heater (binary outputs)
- **Target metrics**: ~99.9% subset accuracy
- **Rule-based labels**:
  - Aerator ON when DO < 5.0
  - Water Pump ON when Ammonia > 0.5 OR Turbidity < 20.0
  - Heater ON when Temp < 25.0

## How to Train

### Basic usage (default settings):
```bash
python train_pondControl.py
```

### Custom parameters:
```bash
python train_pondControl.py --test-size 0.2 --seed 42
```

### Specify input/output paths:
```bash
python train_pondControl.py --input withTimePondData_station1.csv --model-output pondControl.pkl --metrics-output pondControl_metrics.json
```

## Available Models
The script trains and compares 4 models:
- RandomForest
- ExtraTrees
- LightGBM
- XGBoost

The best model (by subset accuracy) is automatically selected and saved.

## Output
- `pondControl.pkl` - Best model artifact
- `pondControl_metrics.json` - Training metrics for all models

## Usage in Production
```python
import joblib

artifact = joblib.load('pondControl.pkl')
model = artifact['model']

# Make predictions
predictions = model.predict(sensor_data)  # Returns [[aerator, pump, heater], ...]
```
