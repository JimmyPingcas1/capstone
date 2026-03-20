
"""
ESP32 Sensor Data Controller
Handles sensor data from ESP32, predicts DO, validates data, and saves to database
"""

from datetime import datetime, timezone
from typing import Dict, Optional
from ..db import sensors_collection, aiControl_collection
from ..services.ai_do_prediction_service import predict_dissolved_oxygen
from ..services.ai_device_control_prediction import predict_device_control
from ..models.SensorDataValidator import validate_sensor_data


def _extract_aerator_state(control_doc: Optional[Dict]) -> bool:
    """Extract aerator state from AiButton payload as a strict boolean."""
    if not isinstance(control_doc, dict):
        return False

    raw_devices = control_doc.get("devices")
    if not isinstance(raw_devices, dict):
        return False

    value = raw_devices.get("aerator", False)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"on", "true", "1", "yes"}
    if isinstance(value, (int, float)):
        return bool(value)
    return False


async def process_esp32_sensor_data(
    user_id: str,
    pond_id: str,
    temperature: float,
    turbidity: float,
    ph: float,
    ammonia: float
) -> Dict:
    """
    Process sensor data from ESP32:
    1. Validate sensor readings
    2. Predict dissolved oxygen using AI
    3. Store data in database
    
    Args:
        user_id: User identifier
        pond_id: Pond identifier
        temperature: Water temperature in Celsius
        turbidity: Turbidity in NTU
        ph: pH level
        ammonia: Ammonia concentration in ppm
        
    Returns:
        Dictionary with validation results and DO prediction
    """
    
    timestamp = datetime.now(timezone.utc)
    
    print(f"\n🌡️  SENSOR DATA FROM ESP32")
    print(f"   User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
    print(f"   Temp: {temperature}°C | pH: {ph}")
    print(f"   Turbidity: {turbidity} | Ammonia: {ammonia}")
    
    # Step 1: Validate sensor data
    validation_data = {
        'temperature': temperature,
        'ph': ph,
        'ammonia': ammonia,
        'turbidity': turbidity
    }
    
    is_valid, errors, warnings = validate_sensor_data(validation_data)
    
    if not is_valid:
        print(f"   ❌ SENSOR VALIDATION FAILED")
        for error in errors:
            print(f"      • {error}")
        
        return {
            "success": False,
            "validation_errors": errors,
            "validation_warnings": warnings,
            "message": "Sensor data validation failed - possible sensor malfunction"
        }
    
    if warnings:
        print(f"   ⚠️  SENSOR WARNINGS:")
        for warning in warnings:
            print(f"      • {warning}")
    
    # Step 2: Predict dissolved oxygen using AI
    print(f"   🤖 Predicting Dissolved Oxygen...")
    
    # Predict DO first without sensor_id (since we don't have it yet)
    do_prediction = await predict_dissolved_oxygen(
        temperature=temperature,
        ph=ph,
        ammonia=ammonia,
        turbidity=turbidity,
        pond_id=pond_id,
        user_id=user_id
    )
    
    if not do_prediction.get('success'):
        print(f"   ❌ DO Prediction Failed")
        return {
            "success": False,
            "message": "DO prediction failed",
            "errors": do_prediction.get('errors', [])
        }
    
    predicted_do = do_prediction.get('predicted_dissolved_oxygen')
    do_confidence = do_prediction.get('confidence')
    do_risk_level = do_prediction.get('risk_level')
    
    print(f"   ✅ Predicted DO: {predicted_do} mg/L (confidence: {do_confidence}%)")
    print(f"   📊 Risk Level: {do_risk_level}")

    # Snapshot current AiButton state so each sensor row keeps the real user/device state at send time.
    try:
        control_doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
    except Exception as control_error:
        print(f"   ⚠️  Failed to read AiButton state: {control_error}")
        control_doc = None

    ai_mode = bool(control_doc.get("aiMode", False)) if control_doc else False
    aerator_state = _extract_aerator_state(control_doc)

    print(f"   🎛️  Aerator Snapshot: {aerator_state}")
    
    # Step 3: Store sensor data with predicted DO in database
    sensor_document = {
        "user_id": user_id,
        "pond_id": pond_id,
        "temperature": float(temperature),
        "turbidity": float(turbidity),
        "ph": float(ph),
        "ammonia": float(ammonia),
        "predicted_dissolved_oxygen": float(predicted_do),
        "do_confidence": float(do_confidence),
        "do_risk_level": do_risk_level,
        "aerator_state": aerator_state,
        "validation_warnings": warnings,
        "created_at": timestamp
    }
    
    try:
        sensor_result = await sensors_collection.insert_one(sensor_document)
        sensor_id = sensor_result.inserted_id
        print(f"   ✅ Sensor Data Saved to Database (ID: {sensor_id})")

        # Now, call predict_dissolved_oxygen again with sensor_id to trigger notification logic
        # Only if AI mode is OFF and risk is not NORMAL
        if not ai_mode and do_risk_level != 'NORMAL':
            await predict_dissolved_oxygen(
                temperature=temperature,
                ph=ph,
                ammonia=ammonia,
                turbidity=turbidity,
                pond_id=pond_id,
                user_id=user_id,
                sensor_id=str(sensor_id)
            )
    except Exception as db_error:
        print(f"   ❌ Database Error: {db_error}")
        return {
            "success": False,
            "message": "Failed to save sensor data",
            "error": str(db_error)
        }
    
    # Step 4: Check AI mode and return device control if enabled
    
    print(f"   AI Mode: {'ON ✅' if ai_mode else 'OFF ❌'}")
    
    if ai_mode:
        # Run AI device control prediction
        sensor_data_for_ai = {
            "temperature": temperature,
            "turbidity": turbidity,
            "ph": ph,
            "ammonia": ammonia,
            "predicted_dissolved_oxygen": predicted_do
        }
        
        device_result = await predict_device_control(
            user_id=user_id,
            pond_id=pond_id,
            sensor_id=str(sensor_id),
            sensor_data=sensor_data_for_ai
        )
        
        # Add DO prediction info to result
        device_result.update({
            "predicted_dissolved_oxygen": predicted_do,
            "do_confidence": do_confidence,
            "do_risk_level": do_risk_level,
            "validation_warnings": warnings,
            "sensor_id": str(sensor_id),
            "aerator_state": aerator_state,
        })
        
        print()
        return device_result
    else:
        # AI mode OFF - just return prediction data
        print(f"   ✅ Process Complete (AI Mode OFF)\n")
        
        return {
            "success": True,
            "ai_mode": False,
            "predicted_dissolved_oxygen": predicted_do,
            "do_confidence": do_confidence,
            "do_risk_level": do_risk_level,
            "validation_warnings": warnings,
            "aerator_state": aerator_state,
            "message": "Sensor data processed and saved successfully.",
            "sensor_id": str(sensor_id)
        }
