# predictPondDo Model Training

This folder contains the training script for the DO (Dissolved Oxygen) prediction model.

## Files
- `train_predictPondDo.py` - Training script for DO classification model
- `withTimePondData_station1.csv` - Training dataset
- `predictPondDo.pkl` - Output trained model (generated after training)

## Model Details
- **Purpose**: Predicts DO level classification (Critical, Low, Warning, Normal)
- **Input features**: pH, Ammonia, Temp, Turbidity (35 engineered features total)
- **Output classes**: ['Critical', 'Low', 'Warning', 'Normal']
- **Target metrics**: ~75% accuracy, ~47% F1-macro, ~80% critical recall
- **Policy**: Includes DO output clamp (0-20 mg/L) and conservative warning shift

## How to Train

### Basic usage (5 runs, 20% test split):
```bash
python train_predictPondDo.py --runs 5 --test-size 0.2
```

### With fixed seed for reproducible results:
```bash
python train_predictPondDo.py --runs 5 --test-size 0.2 --fixed-seed 42
```

### Custom DO bounds:
```bash
python train_predictPondDo.py --runs 5 --do-min 0.0 --do-max 20.0
```

### Include detailed run history (larger file):
```bash
python train_predictPondDo.py --runs 5 --include-runs
```

## Output
- `predictPondDo.pkl` - Compact model artifact with clamp policy and validation rules
- File size: ~4.2 MB (compressed with joblib)

## Usage in Production
```python
import joblib

artifact = joblib.load('predictPondDo.pkl')
model = artifact['model']
feature_columns = artifact['feature_columns']

# Make predictions
predictions = model.predict(X[feature_columns])
```
