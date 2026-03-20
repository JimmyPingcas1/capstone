"""
AI Device Control Prediction Service
Determines which devices (heater, water pump) should be ON/OFF based on sensor data and safe levels
Uses trained ML model (.pkl) for predictions
"""

import numpy as np
import joblib
import os
from datetime import datetime, timezone
from typing import Dict, Optional, List
from ..db import DevicePredictions_collection
import pandas as pd

# Collection alias for readability
device_prediction_collection = DevicePredictions_collection

# ML Model
_device_control_model = None


def load_device_control_model():
    """Load the trained device control ML model"""
    global _device_control_model
    
    if _device_control_model is not None:
        return _device_control_model
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Directly check the ai folder for model file
    app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ai_dir = os.path.join(app_dir, "ai")
    model_path = os.path.join(ai_dir, "4ParamPondControl.pkl")
    if os.path.exists(model_path):
        try:
            artifact = joblib.load(model_path)
            # Extract model from artifact if it's a dictionary
            if isinstance(artifact, dict) and "model" in artifact:
                model = artifact["model"]
            else:
                model = artifact
            
            # Safety check: must have predict method
            if hasattr(model, "predict"):
                print(f"✅ Device Control Model loaded from: {model_path}")
                _device_control_model = model
                return model
            else:
                print(f"⚠️  Loaded object from {model_path} is not a valid model.")
        except Exception as e:
            print(f"⚠️  Failed to load model from {model_path}: {e}")
    else:
        print(f"⚠️  Model file not found at {model_path}")
    print("⚠️  No trained device control model found, using rule-based prediction")
    return None


# Hardcoded safe levels from training data
async def get_safe_levels(pond_id: str) -> Dict:
    """
    Return safe levels from training data for all ponds
    """
    return {
    "temperature": {"min": 26.0, "max": 30.0},
    "ammonia": {"min": 0.0, "max": 0.02},
    "ph": {"min": 6.5, "max": 8.5},
    "turbidity": {"min": 25.0, "max": 40.0},
}


# Hysteresis margins for device control
HYSTERESIS_MARGINS = {
    "temperature": 1.0,  # °C
    "ammonia": 0.01,     # mg/L
    "turbidity": 5.0,    # NTU
    "dissolved_oxygen": 1.0,  # mg/L
    "ph": 0.2,           # units (though not used for devices)
}


def get_hysteresis_thresholds(safe_levels: Dict, previous_devices: Dict) -> Dict:
    """
    Calculate hysteresis-adjusted thresholds based on previous device states
    
    Args:
        safe_levels: Dict with min/max for each parameter
        previous_devices: Dict with previous device states (heater: bool, waterpump: bool)
        
    Returns:
        Dict with hysteresis-adjusted thresholds for turning devices on/off
    """
    thresholds = {}
    
    # Temperature hysteresis
    temp_safe = safe_levels.get('temperature', {})
    temp_min = temp_safe.get('min', 26.0)
    temp_max = temp_safe.get('max', 30.0)
    temp_hyst = HYSTERESIS_MARGINS.get('temperature', 1.0)
    
    # If heater was ON, use higher threshold to turn OFF (safe + hysteresis)
    # If heater was OFF, use lower threshold to turn ON (safe - hysteresis)
    heater_was_on = previous_devices.get('heater', False)
    thresholds['temperature'] = {
        'turn_on_min': temp_min - temp_hyst if not heater_was_on else temp_min,
        'turn_off_min': temp_min + temp_hyst if heater_was_on else temp_min,
        'turn_on_max': temp_max + temp_hyst if not heater_was_on else temp_max,
        'turn_off_max': temp_max - temp_hyst if heater_was_on else temp_max,
    }
    
    # Ammonia hysteresis (only upper limit, for water pump)
    ammonia_safe = safe_levels.get('ammonia', {})
    ammonia_max = ammonia_safe.get('max', 0.02)
    ammonia_hyst = HYSTERESIS_MARGINS.get('ammonia', 0.01)
    
    pump_was_on = previous_devices.get('waterpump', False)
    thresholds['ammonia'] = {
        'turn_on_max': ammonia_max + ammonia_hyst if not pump_was_on else ammonia_max,
        'turn_off_max': ammonia_max - ammonia_hyst if pump_was_on else ammonia_max,
    }
    
    # Turbidity hysteresis (for water pump)
    turbidity_safe = safe_levels.get('turbidity', {})
    turbidity_min = turbidity_safe.get('min', 25.0)  # Match training data: 25-40 NTU
    turbidity_max = turbidity_safe.get('max', 40.0)  # Match training data: 25-40 NTU
    turbidity_hyst = HYSTERESIS_MARGINS.get('turbidity', 5.0)
    
    thresholds['turbidity'] = {
        'turn_on_min': turbidity_min - turbidity_hyst if not pump_was_on else turbidity_min,
        'turn_off_min': turbidity_min + turbidity_hyst if pump_was_on else turbidity_min,
        'turn_on_max': turbidity_max + turbidity_hyst if not pump_was_on else turbidity_max,
        'turn_off_max': turbidity_max - turbidity_hyst if pump_was_on else turbidity_max,
    }
    
    # Dissolved Oxygen hysteresis (for water pump, low DO)
    do_safe = safe_levels.get('dissolved_oxygen', {})
    do_min = do_safe.get('min', 5.0)
    do_hyst = HYSTERESIS_MARGINS.get('dissolved_oxygen', 1.0)
    
    thresholds['dissolved_oxygen'] = {
        'turn_on_min': do_min - do_hyst if not pump_was_on else do_min,
        'turn_off_min': do_min + do_hyst if pump_was_on else do_min,
    }
    
    return thresholds


async def get_last_device_states(pond_id: str) -> Dict:
    """
    Get the last recorded device states for a pond from the database
    
    Args:
        pond_id: Pond identifier
        
    Returns:
        Dict with last device states (heater: bool, waterpump: bool)
    """
    try:
        # Query the last prediction for this pond
        last_prediction = await device_prediction_collection.find_one(
            {"pond_id": pond_id},
            sort=[("created_at", -1)]
        )
        
        if last_prediction and "devices" in last_prediction:
            devices = last_prediction["devices"]
            return {
                "heater": "HEATER" in devices.get("on", []),
                "waterpump": "WATER_PUMP" in devices.get("on", [])
            }
    except Exception as e:
        print(f"⚠️  Failed to get last device states: {e}")
    
    # Default to devices OFF if no previous state
    return {"heater": False, "waterpump": False}




def predict_with_model(sensor_data: Dict, model, safe_levels: Dict = None) -> Dict:
    """
    Use ML model to predict device control
    
    Args:
        sensor_data: Dict with temperature, turbidity, ph, ammonia
        model: Trained ML model (expects 8 features, predicts 2 devices)
        safe_levels: Dict with enforced safe levels for parameters
        
    Returns:
        Dict with device predictions
    """
    try:
        # Get safe levels if not provided
        if safe_levels is None:
            # Import here to avoid circular import
            import asyncio
            safe_levels = asyncio.run(get_safe_levels("default"))
        
        # Extract sensor readings
        ph = sensor_data.get('ph', 7.0)
        ammonia = sensor_data.get('ammonia', 0.02)
        temp = sensor_data.get('temperature', 25.0)
        turbidity = sensor_data.get('turbidity', 25.0)
        
        # Get safe level thresholds
        temp_safe = safe_levels.get('temperature', {})
        temp_min = temp_safe.get('min', 26.0)
        temp_max = temp_safe.get('max', 30.0)
        
        ammonia_safe = safe_levels.get('ammonia', {})
        ammonia_max = ammonia_safe.get('max', 0.02)
        
        ph_safe = safe_levels.get('ph', {})
        ph_min = ph_safe.get('min', 6.5)
        ph_max = ph_safe.get('max', 8.5)
        
        turbidity_safe = safe_levels.get('turbidity', {})
        turbidity_min = turbidity_safe.get('min', 25.0)
        turbidity_max = turbidity_safe.get('max', 40.0)
        
        # Encode status features based on safe levels (High=1, Low=0)
        # Status = 1 means "within safe range", Status = 0 means "outside safe range"
        ph_status = 1 if ph_min <= ph <= ph_max else 0
        ammonia_status = 1 if ammonia <= ammonia_max else 0
        temp_status = 1 if temp_min <= temp <= temp_max else 0
        turbidity_status = 1 if turbidity_min <= turbidity <= turbidity_max else 0
        
        # Feature vector: [pH, Ammonia, Temp, Turbidity, pH_Status, Ammonia_Status, Temp_Status, Turbidity_Status]
        # Create pandas DataFrame with correct column names to match training data
        X = pd.DataFrame([{
            'pH': ph,
            'Ammonia': ammonia,
            'Temp': temp,
            'Turbidity': turbidity,
            'pH_Status': ph_status,
            'Ammonia_Status': ammonia_status,
            'Temp_Status': temp_status,
            'Turbidity_Status': turbidity_status
        }])
        
        # Get predictions (2 outputs: Water Pump, Heater)
        predictions = model.predict(X)
        pred_vector = predictions[0] if predictions.ndim > 1 else predictions
        
        # Try to get probabilities if available
        probas = None
        if hasattr(model, 'predict_proba'):
            try:
                probas = model.predict_proba(X)
                # probas is list of arrays: [array([[p_off, p_on]]), array([[p_off, p_on]])]
            except:
                probas = None
        
        # Map to device states (1=ON, 0=OFF)
        water_pump_on = bool(pred_vector[0])
        heater_on = bool(pred_vector[1])
        
        # Get probabilities for each device
        water_pump_prob_on = probas[0][0][1] if probas else (1.0 if water_pump_on else 0.0)
        heater_prob_on = probas[1][0][1] if probas else (1.0 if heater_on else 0.0)
        
        # Determine issues based on actual sensor violations (not just device states)
        issues = []
        
        # Check for actual violations of safe levels
        if temp < temp_min:
            issues.append("LOW_TEMP")
        elif temp > temp_max:
            issues.append("HIGH_TEMP")
            
        if ammonia > ammonia_max:
            issues.append("HIGH_AMMONIA")
            
        if ph < ph_min:
            issues.append("LOW_PH")
        elif ph > ph_max:
            issues.append("HIGH_PH")
            
        if turbidity > turbidity_max:
            issues.append("HIGH_TURBIDITY")
        elif turbidity < turbidity_min:
            issues.append("LOW_TURBIDITY")
        
        # Create labels based on actual violations and device states
        labels = {
            "LOW_TEMP": 1 if "LOW_TEMP" in issues else 0,
            "HIGH_TEMP": 1 if "HIGH_TEMP" in issues else 0,
            "LOW_DO": 0,  # Not predicted by this model
            "HIGH_AMMONIA": 1 if "HIGH_AMMONIA" in issues else 0,
            "LOW_PH": 1 if "LOW_PH" in issues else 0,
            "HIGH_PH": 1 if "HIGH_PH" in issues else 0,
            "HIGH_TURBIDITY": 1 if "HIGH_TURBIDITY" in issues else 0,
            "LOW_TURBIDITY": 1 if "LOW_TURBIDITY" in issues else 0
        }
        
        # Compute confidences dynamically
        confidences = {}
        for label in labels.keys():
            if labels[label] == 1:  # Issue detected
                if label == "LOW_TEMP":
                    # Confidence based on how far below minimum
                    if temp < temp_min:
                        deviation = temp_min - temp
                        confidence = min(95.0, 60.0 + (deviation * 10))
                    else:
                        confidence = heater_prob_on * 100.0
                elif label == "HIGH_TEMP":
                    # Confidence based on how far above maximum
                    if temp > temp_max:
                        deviation = temp - temp_max
                        confidence = min(95.0, 60.0 + (deviation * 10))
                    else:
                        confidence = water_pump_prob_on * 100.0
                elif label == "HIGH_AMMONIA":
                    # Confidence based on how far above maximum
                    if ammonia > ammonia_max:
                        deviation = ammonia - ammonia_max
                        confidence = min(95.0, 60.0 + (deviation * 100))
                    else:
                        confidence = water_pump_prob_on * 100.0
                elif label == "LOW_PH":
                    # Confidence based on how far below minimum
                    if ph < ph_min:
                        deviation = ph_min - ph
                        confidence = min(95.0, 60.0 + (deviation * 10))
                    else:
                        confidence = 50.0  # Default for pH issues not directly predicted
                elif label == "HIGH_PH":
                    # Confidence based on how far above maximum
                    if ph > ph_max:
                        deviation = ph - ph_max
                        confidence = min(95.0, 60.0 + (deviation * 10))
                    else:
                        confidence = 50.0  # Default for pH issues not directly predicted
                elif label == "HIGH_TURBIDITY":
                    # Confidence based on how far above maximum
                    if turbidity > turbidity_max:
                        deviation = turbidity - turbidity_max
                        confidence = min(95.0, 60.0 + (deviation * 0.5))
                    else:
                        confidence = water_pump_prob_on * 100.0
                elif label == "LOW_TURBIDITY":
                    # Confidence based on how far below minimum
                    if turbidity < turbidity_min:
                        deviation = turbidity_min - turbidity
                        confidence = min(95.0, 60.0 + (deviation * 0.5))
                    else:
                        confidence = 50.0  # Default
                else:
                    confidence = 50.0  # Default for LOW_DO
            else:  # No issue detected
                if label == "LOW_TEMP":
                    confidence = (1.0 - heater_prob_on) * 100.0
                elif label in ["HIGH_AMMONIA", "HIGH_TURBIDITY", "HIGH_TEMP"]:
                    confidence = (1.0 - water_pump_prob_on) * 100.0
                else:
                    confidence = 95.0  # High confidence when no issue detected
        
            confidences[label] = confidence
        
        return {
            "issues": issues,
            "labels": labels,
            "confidences": confidences,
            "method": "ml_model",
            "devices": {
                "water_pump": water_pump_on,
                "heater": heater_on
            }
        }
        
    except Exception as e:
        print(f"❌ Model prediction error: {e}")
        return None


def check_parameters(sensor_data: Dict, safe_levels: Dict) -> Dict:
    """
    Check sensor parameters against safe levels
    Returns: dict with issues, labels, confidences
    """
    issues = []
    labels = {
        "LOW_TEMP": 0,
        "HIGH_TEMP": 0,
        "LOW_DO": 0,
        "HIGH_AMMONIA": 0,
        "LOW_PH": 0,
        "HIGH_PH": 0,
        "HIGH_TURBIDITY": 0,
        "LOW_TURBIDITY": 0
    }
    confidences = {
        "LOW_TEMP": 0.0,
        "HIGH_TEMP": 0.0,
        "LOW_DO": 0.0,
        "HIGH_AMMONIA": 0.0,
        "LOW_PH": 0.0,
        "HIGH_PH": 0.0,
        "HIGH_TURBIDITY": 0.0,
        "LOW_TURBIDITY": 0.0
    }
    
    # Check Temperature
    temp = sensor_data.get('temperature')
    temp_safe = safe_levels.get('temperature', {})
    temp_min = temp_safe.get('min', 20)
    temp_max = temp_safe.get('max', 30)
    if temp < temp_min:
        labels["LOW_TEMP"] = 1
        diff = temp_min - temp
        confidences["LOW_TEMP"] = min(95.0, 60.0 + (diff * 10))
        issues.append("LOW_TEMP")
    elif temp > temp_max:
        labels["HIGH_TEMP"] = 1
        diff = temp - temp_max
        confidences["HIGH_TEMP"] = min(95.0, 60.0 + (diff * 10))
        issues.append("HIGH_TEMP")
    
    # Check Dissolved Oxygen
    do = sensor_data.get('predicted_dissolved_oxygen', sensor_data.get('dissolved_oxygen', 6.0))
    do_safe = safe_levels.get('dissolved_oxygen', {})
    do_min = do_safe.get('min', 5.0)
    if do < do_min:
        labels["LOW_DO"] = 1
        diff = do_min - do
        confidences["LOW_DO"] = min(95.0, 60.0 + (diff * 5))
        issues.append("LOW_DO")
    
    # Check Ammonia
    ammonia = sensor_data.get('ammonia')
    # Check PH
    ph = sensor_data.get('ph')
    ph_safe = safe_levels.get('ph', {})
    ph_min = ph_safe.get('min', 6.5)
    ph_max = ph_safe.get('max', 8.5)
    if ph is not None:
        if ph < ph_min:
            labels["LOW_PH"] = 1
            diff = ph_min - ph
            confidences["LOW_PH"] = min(95.0, 60.0 + (diff * 10))
            issues.append("LOW_PH")
        elif ph > ph_max:
            labels["HIGH_PH"] = 1
            diff = ph - ph_max
            confidences["HIGH_PH"] = min(95.0, 60.0 + (diff * 10))
            issues.append("HIGH_PH")
    ammonia_safe = safe_levels.get('ammonia', {})
    ammonia_max = ammonia_safe.get('max', 0.030)
    if ammonia > ammonia_max:
        labels["HIGH_AMMONIA"] = 1
        diff = ammonia - ammonia_max
        confidences["HIGH_AMMONIA"] = min(95.0, 60.0 + (diff * 100))
        issues.append("HIGH_AMMONIA")
    
    # Check pH
    ph = sensor_data.get('ph')
    ph_safe = safe_levels.get('ph', {})
    if ph < ph_safe.get('min', 5.2) or ph > ph_safe.get('max', 6.2):
        labels["PH_IMBALANCE"] = 1
        if ph < ph_safe['min']:
            diff = ph_safe['min'] - ph
        else:
            diff = ph - ph_safe['max']
        confidences["PH_IMBALANCE"] = min(95.0, 60.0 + (diff * 20))
        issues.append("PH_IMBALANCE")
    
    # Check Turbidity
    turbidity = sensor_data.get('turbidity')
    turbidity_safe = safe_levels.get('turbidity', {})
    turbidity_min = turbidity_safe.get('min', 30)
    turbidity_max = turbidity_safe.get('max', 50)
    if turbidity > turbidity_max:
        labels["HIGH_TURBIDITY"] = 1
        diff = turbidity - turbidity_max
        confidences["HIGH_TURBIDITY"] = min(95.0, 60.0 + (diff * 0.5))
        issues.append("HIGH_TURBIDITY")
    elif turbidity < turbidity_min:
        labels["LOW_TURBIDITY"] = 1
        diff = turbidity_min - turbidity
        confidences["LOW_TURBIDITY"] = min(95.0, 60.0 + (diff * 0.5))
        issues.append("LOW_TURBIDITY")
    
    return {
        "issues": issues,
        "labels": labels,
        "confidences": confidences
    }


def determine_devices(issues: List[str]) -> Dict:
    """
    Determine which devices should be ON based on detected issues
    Returns: dict with 'on' devices list
    """
    devices_on = []
    
    # HEATER: Turn on if temperature is low
    if "LOW_TEMP" in issues:
        devices_on.append("HEATER")
    
    # WATER_PUMP: Turn on for oxygen/ammonia/turbidity/overheat concerns
    if (
        "LOW_DO" in issues
        or "HIGH_AMMONIA" in issues
        or "HIGH_TURBIDITY" in issues
        or "HIGH_TEMP" in issues
    ):
        devices_on.append("WATER_PUMP")
    
    return {"on": devices_on}


def apply_hysteresis_control(
    sensor_data: Dict,
    thresholds: Dict,
    previous_devices: Dict
) -> Dict:
    """
    Apply improved hysteresis-based device control logic with overheating protection
    
    Devices turn ON when conditions exceed thresholds, stay ON until reaching 
    hysteresis-adjusted safe levels, then turn OFF. Without hysteresis crossing,
    devices maintain their previous state.
    
    Args:
        sensor_data: Current sensor readings
        thresholds: Hysteresis-adjusted thresholds for each parameter
        previous_devices: Previous device states (heater: bool, waterpump: bool)
        
    Returns:
        Dict with final device states: {"heater": bool, "water_pump": bool}
    """
    # Extract sensor values
    temp = sensor_data.get('temperature', 27.0)
    ammonia = sensor_data.get('ammonia', 0.01)
    turbidity = sensor_data.get('turbidity', 35.0)
    do = sensor_data.get('predicted_dissolved_oxygen', sensor_data.get('dissolved_oxygen', 6.0))
    
    # Get previous states
    heater_was_on = previous_devices.get('heater', False)
    pump_was_on = previous_devices.get('waterpump', False)
    
    # ============================================
    # HEATER CONTROL (Temperature with overheating protection)
    # ============================================
    temp_thresholds = thresholds.get('temperature', {})
    turn_on_min_temp = temp_thresholds.get('turn_on_min', 24.0)
    turn_off_min_temp = temp_thresholds.get('turn_off_min', 27.0)
    turn_off_max_temp = temp_thresholds.get('turn_off_max', 29.0)
    
    if temp < turn_on_min_temp:
        # Temperature is too low - TURN ON heater
        heater_on = True
    elif temp >= turn_off_min_temp or temp > turn_off_max_temp:
        # Temperature is safe (reached safe + hysteresis) OR overheating - TURN OFF heater
        heater_on = False
    else:
        # Temperature is in hysteresis band - MAINTAIN previous state
        heater_on = heater_was_on
    
    # ============================================
    # WATER PUMP CONTROL (Multi-condition with proper hysteresis)
    # ============================================
    ammonia_thresholds = thresholds.get('ammonia', {})
    turbidity_thresholds = thresholds.get('turbidity', {})
    do_thresholds = thresholds.get('dissolved_oxygen', {})
    
    # Turn ON conditions (ANY condition exceeds danger threshold = TURN ON)
    ammonia_turn_on_max = ammonia_thresholds.get('turn_on_max', 0.03)
    turbidity_turn_on_max = turbidity_thresholds.get('turn_on_max', 45.0)
    do_turn_on_min = do_thresholds.get('turn_on_min', 4.0)
    temp_turn_on_max = temp_thresholds.get('turn_on_max', 32.0)
    
    pump_turn_on = (
        ammonia > ammonia_turn_on_max or
        turbidity > turbidity_turn_on_max or
        do < do_turn_on_min or
        temp > temp_turn_on_max
    )
    
    # Turn OFF conditions (ALL conditions must return to safe levels = TURN OFF)
    ammonia_turn_off_max = ammonia_thresholds.get('turn_off_max', 0.01)
    turbidity_turn_off_max = turbidity_thresholds.get('turn_off_max', 35.0)
    do_turn_off_min = do_thresholds.get('turn_off_min', 6.0)
    temp_turn_off_max = temp_thresholds.get('turn_off_max', 30.0)
    
    pump_turn_off = (
        ammonia <= ammonia_turn_off_max and
        turbidity <= turbidity_turn_off_max and
        do >= do_turn_off_min and
        temp <= temp_turn_off_max
    )
    
    if pump_turn_on:
        # At least one condition exceeds danger threshold - TURN ON pump
        pump_on = True
    elif pump_turn_off:
        # All conditions have returned to safe levels - TURN OFF pump
        pump_on = False
    else:
        # In hysteresis band - MAINTAIN previous state
        pump_on = pump_was_on
    
    print(f"   🔄 Hysteresis Control Applied:")
    print(f"      Heater: {heater_was_on} → {heater_on} (temp={temp:.1f}°C)")
    print(f"      Pump:   {pump_was_on} → {pump_on} (NH₃={ammonia:.2f}, Turb={turbidity:.0f}, DO={do:.1f})")
    
    return {
        "heater": heater_on,
        "water_pump": pump_on
    }


async def predict_device_control(
    user_id: str,
    pond_id: str,
    sensor_id: str,
    sensor_data: Dict
) -> Dict:
    """
    Main function to predict device control based on sensor data with hysteresis
    
    Flow:
    1. Load ML model and safe levels
    2. Detect issues using ML (if available) or rule-based analysis
    3. Retrieve previous device states from database
    4. Calculate hysteresis-adjusted thresholds
    5. Apply hysteresis control logic to determine final device states
    6. Log prediction and return results
    
    Args:
        user_id: User identifier
        pond_id: Pond identifier
        sensor_id: Sensor document ID
        sensor_data: Current sensor readings (temperature, turbidity, ph, ammonia, predicted_dissolved_oxygen)
        
    Returns:
        Dict with device states, detected issues, confidences, and prediction info
    """
    
    print(f"\n🤖 AI DEVICE CONTROL PREDICTION (with Hysteresis)")
    print(f"   User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
    
    # ============================================
    # STEP 1: Load ML model
    # ============================================
    model = load_device_control_model()
    
    # ============================================
    # STEP 2: Get safe levels for this pond
    # ============================================
    safe_levels = await get_safe_levels(pond_id)
    print(f"   ✅ Safe Levels Loaded")
    
    # ============================================
    # STEP 3: Detect issues (ML or rule-based)
    # ============================================
    if model is not None:
        print(f"   🤖 Using ML Model for issue detection")
        ml_result = predict_with_model(sensor_data, model, safe_levels)
        
        if ml_result is not None:
            # Use ML for issue detection
            check_result = ml_result
            method = "ml_model"
        else:
            # ML failed, fallback to rule-based
            print(f"   ⚠️  ML prediction failed, using rule-based")
            check_result = check_parameters(sensor_data, safe_levels)
            method = "rule_based_fallback"
    else:
        print(f"   📋 Using rule-based issue detection")
        check_result = check_parameters(sensor_data, safe_levels)
        method = "rule_based"
    
    # Extract issue detection results
    issues = check_result['issues']
    labels = check_result['labels']
    confidences = check_result['confidences']
    
    # ============================================
    # STEP 4: Retrieve previous device states
    # ============================================
    previous_devices = await get_last_device_states(pond_id)
    print(f"   📋 Previous States - Heater: {previous_devices.get('heater')}, Pump: {previous_devices.get('waterpump')}")
    
    # ============================================
    # STEP 5: Calculate hysteresis thresholds
    # ============================================
    thresholds = get_hysteresis_thresholds(safe_levels, previous_devices)
    print(f"   📊 Hysteresis Thresholds Calculated")
    
    # ============================================
    # STEP 6: Apply hysteresis control logic
    # ============================================
    final_devices = apply_hysteresis_control(sensor_data, thresholds, previous_devices)
    
    # Build device response in standard format
    devices = {
        "on": [],
        "off": []
    }
    if final_devices.get('heater', False):
        devices["on"].append("HEATER")
    else:
        devices["off"].append("HEATER")
    
    if final_devices.get('water_pump', False):
        devices["on"].append("WATER_PUMP")
    else:
        devices["off"].append("WATER_PUMP")
    
    # ============================================
    # STEP 7: Determine danger/fixed status
    # ============================================
    # Danger = devices are ON (system is trying to fix something)
    # Fixed = no devices are ON (all parameters are within safe range + hysteresis)
    danger = len(devices.get('on', [])) > 0
    fixed = not danger
    reported_issues = issues
    

    # Only save the specified fields
    timestamp = datetime.now(timezone.utc).isoformat()
    prediction_doc = {
        "user_id": user_id,
        "pond_id": pond_id,
        "sensor_id": sensor_id,
        "labels": labels,
        "confidences": confidences,
        "devices": devices,
        "detected_issues": reported_issues,
        "final_devices": final_devices,
        "danger": danger,
        "created_at": timestamp,
        "prediction_method": method
    }

    result = await device_prediction_collection.insert_one(prediction_doc)
    print(f"   📝 Prediction Recorded: {result.inserted_id}")

    # ============================================
    # STEP 8: Create notification if AI is enabled
    # ============================================
    from ..controller.notificationController import process_and_save_notifications
    notification_data = {
        "pond_id": pond_id,
        "sensor_id": sensor_id,
        "data": {
            **sensor_data,
            # Ensure predicted_dissolved_oxygen is present for notification
            "predicted_dissolved_oxygen": sensor_data.get("predicted_dissolved_oxygen")
        }
    }
    # Only create notification if AI is on (model is not None)
    if model is not None:
        await process_and_save_notifications(notification_data, ai_mode=True)

    # ============================================
    # STEP 9: Build final response
    # ============================================
    devices_on = {
        "heater": "HEATER" in devices.get('on', []),
        "waterpump": "WATER_PUMP" in devices.get('on', []),
    }

    return {
        "success": True,
        "danger": danger,
        "fixed": fixed,
        "devices_on": devices_on,
        "devices_off": {
            "heater": "HEATER" not in devices.get('on', []),
            "waterpump": "WATER_PUMP" not in devices.get('on', [])
        },
        "detected_issues": reported_issues,
        "labels": labels,
        "confidences": confidences,
        "prediction_method": method,
        "previous_devices": previous_devices,
        "final_devices": final_devices,
        "prediction_id": str(result.inserted_id),
        "status": "new" if danger else "fixed"
    }
