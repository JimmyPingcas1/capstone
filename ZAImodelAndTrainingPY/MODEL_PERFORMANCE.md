# Model Performance Metrics

This document summarizes the performance metrics for all trained models in this project.

---

## 1. predictPondDo.pkl
**Dissolved Oxygen (DO) Classification Model**

### Overview
- **Location**: `predictDoPy/predictPondDo.pkl`
- **Purpose**: Predicts DO level classification to monitor water quality
- **File Size**: 4.23 MB
- **Model Type**: RandomForest Classifier
- **Classes**: 4 categories
  - `Critical` (DO < 5.0 mg/L)
  - `Low` (5.0 ≤ DO < 6.0 mg/L)
  - `Warning` (6.0 ≤ DO < 7.0 mg/L)
  - `Normal` (DO ≥ 7.0 mg/L)

### Input Features
- **Sensors**: pH, Ammonia, Temp, Turbidity (4 sensors)
- **Total Features**: 35 (includes lag features, rolling statistics, and interactions)
- **Feature Engineering**: 
  - Lag features (1, 2, 3 steps)
  - Rolling means and standard deviations (window=3)
  - Squared terms and interaction terms
  - Time-based features (hour sin/cos)

### Performance Metrics

| Metric | Mean (5 runs) | Std Dev | Best Run |
|--------|---------------|---------|----------|
| **Accuracy** | **75.12%** | ±0.61% | **75.18%** |
| **F1-Macro** | **47.06%** | ±0.59% | **47.72%** |
| **Critical Recall** | **80.12%** | ±3.55% | **84.19%** |

### Classification Report (Best Run)
```
              precision    recall  f1-score   support
    Critical     0.5347    0.8419    0.6541       329
         Low     0.3333    0.1333    0.1905       405
     Warning     0.2365    0.1441    0.1791       576
      Normal     0.8512    0.9221    0.8853      3351
```

### Safety Features
- **DO Output Clamp**: [0.0, 20.0] mg/L
- **Conservative Policy**: DO values in [6.0, 7.0) are shifted by -1.0 for early warning
- **Critical Threshold**: DO < 5.0 mg/L triggers critical alert
- **Input Validation**: Rejects out-of-range sensor values

### Training Configuration
- **Runs**: 5 random splits
- **Test Size**: 20%
- **Mode**: Dynamic (non-fixed seeds)
- **Data Source**: `withTimePondData_station1.csv`
- **Rows Used**: 23,304 (after feature engineering)

---

## 2. pondControl.pkl
**5-Parameter Actuator Control Model**

### Overview
- **Location**: `pondControlPy/pondControl.pkl`
- **Purpose**: Controls 3 actuators based on 5 sensor readings
- **File Size**: 55.23 MB
- **Model Type**: ExtraTrees MultiOutput Classifier
- **Targets**: 3 actuators (binary ON/OFF for each)
  - `Aerator` (ON when DO < 5.0)
  - `Water Pump` (ON when Ammonia > 0.5 OR Turbidity < 20.0)
  - `Heater` (ON when Temp < 25.0)

### Input Features
- **Sensors**: pH, Ammonia, Temp, DO, Turbidity (5 sensors)
- **Status Features**: pH_Status, Ammonia_Status, Temp_Status, DO_Status, Turbidity_Status
- **Total Features**: 10 (5 numeric + 5 status encodings)

### Performance Metrics

| Metric | Performance |
|--------|-------------|
| **Subset Accuracy** | **90.90%** |
| **Macro F1** | **91.61%** |

### Per-Target Performance

| Target | Accuracy | F1-Score |
|--------|----------|----------|
| **Aerator** | 96.70% | 81.68% |
| **Water Pump** | 97.12% | 95.58% |
| **Heater** | 96.83% | 97.57% |

### Model Comparison (All Models Tested)
| Model | Subset Accuracy | Macro F1 |
|-------|----------------|----------|
| RandomForest | 90.84% | 91.50% |
| **ExtraTrees** | **90.90%** | **91.61%** ✓ |
| LightGBM | 90.90% | 91.61% |
| XGBoost | 90.90% | 91.61% |

*Note: ExtraTrees selected as best model*

### Training Configuration
- **Test Size**: 20%
- **Random Seed**: 42
- **Label Noise**: 3% (for realistic training)
  - Aerator: 714 noisy labels
  - Water Pump: 716 noisy labels
  - Heater: 710 noisy labels
- **Data Source**: `withTimePondData_station1.csv`
- **Encoding**: 
  - Status: `Low=0, High=1`
  - Actuator: `OFF=0, ON=1`

---

## 3. 4ParamPondControl.pkl
**4-Parameter Actuator Control Model (No DO/Aerator)**

### Overview
- **Location**: `4ParamPondControlTrainPY/4ParamPondControl.pkl`
- **Purpose**: Controls 2 actuators (excludes Aerator) for systems without DO sensor
- **File Size**: 50.50 MB
- **Model Type**: ExtraTrees MultiOutput Classifier
- **Targets**: 2 actuators (binary ON/OFF for each)
  - `Water Pump` (ON when Ammonia low OR Turbidity low)
  - `Heater` (ON when Temp low)

### Input Features
- **Sensors**: pH, Ammonia, Temp, Turbidity (4 sensors, **excludes DO**)
- **Status Features**: pH_Status, Ammonia_Status, Temp_Status, Turbidity_Status
- **Total Features**: 8 (4 numeric + 4 status encodings)

### Performance Metrics

| Metric | Performance |
|--------|-------------|
| **Subset Accuracy** | **90.65%** |
| **Macro F1** | **96.21%** |

### Per-Target Performance

| Target | Accuracy | F1-Score |
|--------|----------|----------|
| **Water Pump** | 95.25% | 97.16% |
| **Heater** | 95.17% | 95.26% |

### Training Configuration
- **Test Size**: 20%
- **Random Seed**: 42
- **Compression**: XZ level 3
- **Data Source**: `withTimePondData_station1.csv`

---

## Model Comparison Summary

### Best For Each Metric

| Metric | Best Model | Score |
|--------|------------|-------|
| **Highest Subset Accuracy** | pondControl (5-param) | 90.90% |
| **Highest Macro F1** | 4ParamPondControl | 96.21% |
| **Critical DO Detection** | predictPondDo | 80.12% recall |
| **Smallest File Size** | predictPondDo | 4.23 MB |

### Use Case Recommendations

#### Use **predictPondDo.pkl** when:
- ✅ You need to predict DO levels without direct DO sensor reading
- ✅ Early warning for critical oxygen depletion is required
- ✅ File size constraints (deployment to edge devices)
- ✅ You want probabilistic DO classification
- ✅ Conservative safety margins are important

#### Use **pondControl.pkl** when:
- ✅ You have all 5 sensors (including DO)
- ✅ You need full actuator control (Aerator + Pump + Heater)
- ✅ Highest overall accuracy is required
- ✅ You need rule-based actuator decisions with high reliability

#### Use **4ParamPondControl.pkl** when:
- ✅ DO sensor is unavailable or unreliable
- ✅ Aerator control is managed separately
- ✅ You only need Water Pump and Heater control
- ✅ Highest F1 score for 2-actuator system is required

---

## Training Scripts

All models can be retrained using the provided scripts:

### predictPondDo Training
```bash
cd predictDoPy
python train_predictPondDo.py --runs 5 --test-size 0.2
```

### pondControl Training
```bash
cd pondControlPy
python train_pondControl.py --test-size 0.2 --seed 42
```

### 4ParamPondControl Training
```bash
cd 4ParamPondControlTrainPY
python train_4ParamPondControl.py
```

See individual `README.md` files in each folder for detailed training options.

---

## Notes

### Data Quality
- All models trained on `withTimePondData_station1.csv`
- Data cleaning includes:
  - Removing extreme outliers (1st and 99th percentile filtering for DO)
  - Dropping rows with missing sensor values
  - Type conversion and validation

### Model Artifacts
Each `.pkl` file contains:
- Trained model object
- Feature column names (for proper input alignment)
- Training metadata (seed, test size, date)
- Performance metrics
- Input validation rules (for predictPondDo)
- Label encodings (for actuator models)

### Loading Models
```python
import joblib

# Load any model
artifact = joblib.load('path/to/model.pkl')

# Access components
model = artifact['model']
feature_columns = artifact['feature_columns']

# Make predictions
predictions = model.predict(X[feature_columns])
```

---

**Last Updated**: March 8, 2026  
**Training Framework**: scikit-learn, XGBoost, LightGBM  
**Python Version**: 3.14.3
