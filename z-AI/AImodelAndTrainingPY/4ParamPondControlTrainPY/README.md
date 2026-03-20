# 4ParamPondControl Model Training (4-Parameter Actuator Control)

This folder contains the training script for the 4-parameter actuator control model (Water Pump, Heater only - no Aerator).

## Files
- `train_4ParamPondControl.py` - Training script for 4-parameter model
- `withTimePondData_station1.csv` - Training dataset
- `4ParamPondControl.pkl` - Output trained model (generated after training)
- `4ParamPondControl_metrics.json` - Training metrics (generated after training)

## Model Details
- **Purpose**: Predicts actuator states for Water Pump and Heater only (excludes Aerator/DO)
- **Input features**: pH, Ammonia, Temp, Turbidity (4 sensors)
- **Output targets**: Water Pump, Heater (binary outputs)
- **Target metrics**: High subset accuracy (similar to 5-param model)
- **Rule-based labels**:
  - Water Pump ON when Ammonia status is Low OR Turbidity status is Low
  - Heater ON when Temp status is Low

## How to Train

### Basic usage:
```bash
python train_4ParamPondControl.py
```

The script automatically:
1. Loads data from `withTimePondData_station1.csv`
2. Builds 4-parameter feature schema
3. Trains ExtraTrees model
4. Saves model to `4ParamPondControl.pkl`
5. Saves metrics to `4ParamPondControl_metrics.json`

## Model Configuration
- **Estimator**: ExtraTreesClassifier with MultiOutputClassifier wrapper
- **n_estimators**: 320
- **Compression**: XZ level 3 (compact file size)
- **Test split**: 20%
- **Random seed**: 42

## Output
- `4ParamPondControl.pkl` - Trained model artifact (compressed)
- `4ParamPondControl_metrics.json` - Training metrics including subset accuracy and per-target F1

## Usage in Production
```python
import joblib

artifact = joblib.load('4ParamPondControl.pkl')
model = artifact['model']

# Make predictions (4 features: pH, Ammonia, Temp, Turbidity)
predictions = model.predict(sensor_data)  # Returns [[pump, heater], ...]
```

## Note
This model intentionally excludes DO and Aerator control for scenarios where DO sensor is unavailable or aerator control is managed separately.
