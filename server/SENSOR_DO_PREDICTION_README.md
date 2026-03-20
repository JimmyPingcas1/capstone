# Sensor Data Processing & DO Prediction System

## Overview
This system processes sensor data from ESP32 devices, validates the readings, predicts dissolved oxygen (DO) levels using AI, and controls pond devices based on water quality analysis.

## Architecture

### Data Flow
```
ESP32 → AiSensorControlRoute → EspSendDataController → Database
                                        ↓
                              DO Prediction Service
                                        ↓
                              SensorDataValidator
                                        ↓
                              AiController (Device Control)
```

## Components

### 1. **ai_do_prediction_service.py**
**Purpose**: Predicts dissolved oxygen levels based on water quality parameters

**Key Features**:
- Uses trained ML model or empirical calculation
- Validates input parameters
- Calculates DO saturation based on temperature
- Adjusts for pH, ammonia, and turbidity effects
- Returns confidence score and risk level

**Main Function**:
```python
async def predict_dissolved_oxygen(
    temperature: float,
    ph: float,
    ammonia: float,
    turbidity: float,
    pond_id: Optional[str] = None
) -> Dict
```

**DO Calculation Formula** (when ML model not available):
```
Base DO = 14.652 - 0.41022*T + 0.007991*T² - 0.000077774*T³

Factors:
- pH Factor: Optimal 6.5-8.5
- Ammonia Factor: High ammonia reduces DO (decomposition)
- Turbidity Factor: High turbidity reduces DO (organic matter)

Predicted DO = Base DO × pH Factor × Ammonia Factor × Turbidity Factor
```

### 2. **EspSendDataController.py**
**Purpose**: Processes sensor data from ESP32 and orchestrates the prediction pipeline

**Main Function**:
```python
async def process_esp32_sensor_data(
    user_id: str,
    pond_id: str,
    temperature: float,
    turbidity: float,
    ph: float,
    ammonia: float
) -> Dict
```

**Processing Steps**:
1. **Validate** sensor readings (check for impossible values)
2. **Predict DO** using AI service
3. **Store** data in database with predicted DO
4. **Check AI mode** status
5. **Run** water quality prediction and device control

### 3. **SensorDataValidator.py**
**Purpose**: Validates sensor readings for impossible or unrealistic values

**Parameter Ranges**:
- **Temperature**: 20-35°C (critical: 0-45°C)
- **pH**: 5-10 (critical: 0-14)
- **Ammonia**: 0-0.5 ppm (critical: 0-5 ppm)
- **Turbidity**: 0-50 NTU (critical: 0-1000 NTU)
- **DO**: 3-12 mg/L (critical: 0-20 mg/L)

**Validation Types**:
- **Critical Errors**: Impossible values (sensor malfunction)
- **Warnings**: Unusual but possible values (fish health risk)
- **Pattern Detection**: Stuck sensors, sudden jumps

### 4. **SensorDoPredictionModel.py**
**Purpose**: Pydantic models for DO prediction and risk assessment

**Models**:
- `DOPredictionInput`: Validated input parameters
- `DOPredictionOutput`: Prediction results with confidence
- `DOThreshold`: Configurable DO thresholds

**Risk Levels**:
- **CRITICAL**: DO < 3.0 mg/L → Activate aerators NOW!
- **HIGH**: DO < 5.0 mg/L → Warning
- **MEDIUM**: DO < 6.0 mg/L or > 9.0 mg/L
- **OPTIMAL**: DO 6.0-9.0 mg/L → All good

## Database Schema Changes

### ✅ Updated: `sensors_collection`
```javascript
{
  "_id": ObjectId,
  "user_id": String,
  "pond_id": String,
  "temperature": Float,           // °C
  "turbidity": Float,            // NTU
  "predicted_dissolved_oxygen": Float,  // mg/L (CHANGED from dissolved_oxygen)
  "ph": Float,
  "ammonia": Float,              // ppm
  "do_confidence": Float,        // % (NEW)
  "do_risk_level": String,       // CRITICAL/HIGH/MEDIUM/LOW/OPTIMAL (NEW)
  "validation_warnings": Array,  // Warning messages (NEW)
  "created_at": DateTime
}
```

### Key Changes:
- **`dissolved_oxygen`** → **`predicted_dissolved_oxygen`**
- **Added**: `do_confidence` - AI confidence percentage
- **Added**: `do_risk_level` - Risk assessment
- **Added**: `validation_warnings` - Sensor validation warnings

## API Endpoints

### POST `/api/v1/sensor-ai`
**Purpose**: Receive sensor data from ESP32

**Request**:
```json
{
  "temperature": 28.5,
  "turbidity": 18.5,
  "ph": 7.2,
  "ammonia": 0.035
}
```

**Query Parameters**:
- `user_id`: User identifier
- `pond_id`: Pond identifier

**Response** (AI Mode ON):
```json
{
  "success": true,
  "predicted_dissolved_oxygen": 6.8,
  "do_confidence": 92.5,
  "do_risk_level": "OPTIMAL",
  "validation_warnings": [],
  "ai_mode": true,
  "danger": false,
  "devices_on": {},
  "devices_off": {},
  "detected_issues": [],
  "ai_id": "507f1f77bcf86cd799439011"
}
```

**Response** (Validation Error):
```json
{
  "success": false,
  "validation_errors": [
    "Temperature value 50.0°C exceeds critical maximum (45.0°C). Possible sensor malfunction."
  ],
  "validation_warnings": [],
  "message": "Sensor data validation failed - possible sensor malfunction"
}
```

## Usage Examples

### 1. Process ESP32 Sensor Data
```python
from app.controller.EspSendDataContoller import process_esp32_sensor_data

result = await process_esp32_sensor_data(
    user_id="user123",
    pond_id="pond456",
    temperature=28.5,
    turbidity=18.5,
    ph=7.2,
    ammonia=0.035
)

if result['success']:
    print(f"Predicted DO: {result['predicted_dissolved_oxygen']} mg/L")
    print(f"Risk Level: {result['do_risk_level']}")
```

### 2. Validate Sensor Data
```python
from app.models.SensorDataValidator import validate_sensor_data

is_valid, errors, warnings = validate_sensor_data({
    'temperature': 28.5,
    'ph': 7.2,
    'ammonia': 0.035,
    'turbidity': 18.5
})

if not is_valid:
    print("Sensor errors:", errors)
```

### 3. Predict DO Directly
```python
from app.services.ai_do_prediction_service import predict_dissolved_oxygen

result = await predict_dissolved_oxygen(
    temperature=28.5,
    ph=7.2,
    ammonia=0.035,
    turbidity=18.5
)

print(f"DO: {result['predicted_dissolved_oxygen']} mg/L")
print(f"Confidence: {result['confidence']}%")
```

## Benefits

### 1. **Data Validation**
- Catches sensor malfunctions early
- Prevents storing impossible values
- Warns about dangerous conditions

### 2. **AI-Powered DO Prediction**
- More accurate than direct sensor readings
- Considers multiple water quality factors
- Provides confidence scores

### 3. **Risk Assessment**
- Automatic risk level classification
- Actionable recommendations
- Temperature-aware suggestions

### 4. **Separation of Concerns**
- Sensor data storage separate from AI prediction
- Modular, maintainable code
- Easy to extend with new features

## Migration Notes

### For Existing Data
If you have existing sensor data with `dissolved_oxygen` field, you can migrate it:

```python
# Migration script (run once)
async def migrate_sensor_data():
    async for doc in sensors_collection.find({"dissolved_oxygen": {"$exists": True}}):
        await sensors_collection.update_one(
            {"_id": doc["_id"]},
            {
                "$rename": {"dissolved_oxygen": "predicted_dissolved_oxygen"},
                "$set": {
                    "do_confidence": 85.0,  # Default confidence
                    "do_risk_level": "UNKNOWN"
                }
            }
        )
```

### For ESP32 Code
No changes needed! ESP32 still sends the same parameters:
- temperature
- turbidity
- ph
- ammonia

The server now calculates DO instead of receiving it from sensors.

## Testing

Run the example script to test all features:

```bash
cd server
python -m app.models.example_usage
```

This will demonstrate:
- Single reading validation
- Batch validation
- Pattern detection
- DO prediction
- Risk assessment
- Custom thresholds
