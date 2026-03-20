"""
AI Dissolved Oxygen Prediction Service
Predicts DO levels based on water quality parameters using AI model
"""

import numpy as np
import joblib
import os
from datetime import datetime, timezone
import math
import warnings as py_warnings
from typing import Dict, Tuple, Optional
from ..controller.notificationController import process_and_save_notifications
from ..models.SensorDataValidator import validate_sensor_data
from ..models.SensorDoPredictionModel import (
    get_do_risk_level,
    get_do_recommendations,
    DOThreshold
)


class DOPredictionService:
    """Service for predicting dissolved oxygen levels"""
    
    def __init__(self):
        """Initialize the DO prediction service"""
        self.model = None
        self.model_artifact = None
        self.model_path = self._get_model_path()
        self._load_model()
    
    def _get_model_path(self) -> str:
        """Get the path to the trained DO prediction model"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Look for DO prediction model
        model_paths = [
            # Preferred model requested by user
            os.path.join(base_dir, "ai", "predictPondDo.pkl"),
            os.path.join(base_dir, "..", "..", "ZAImodelAndTrainingPY", "predictPondDo.pkl"),
            os.path.join(base_dir, "..", "..", "z-AI", "AImodelAndTrainingPY", "predictPondDo.pkl"),
            # Existing fallbacks
            os.path.join(base_dir, "models", "do_prediction_model.pkl"),
            os.path.join(base_dir, "models", "trained_do_model.pkl"),
            os.path.join(base_dir, "trained_do_model.pkl"),
        ]
        
        for path in model_paths:
            if os.path.exists(path):
                return path
        
        # If no model found, use fallback calculation
        print("⚠️  No trained DO model found, using calculation-based prediction")
        return None
    
    def _load_model(self):
        """Load the trained model if available"""
        if self.model_path and os.path.exists(self.model_path):
            try:
                loaded = joblib.load(self.model_path)

                # Support wrapped artifacts: {'model': estimator, ...metadata}
                if isinstance(loaded, dict):
                    wrapped_model = loaded.get('model')
                    if wrapped_model is not None and hasattr(wrapped_model, 'predict'):
                        self.model_artifact = loaded
                        self.model = wrapped_model
                        print(f"✅ DO Prediction Artifact loaded from: {self.model_path}")
                        return

                    print("⚠️  DO model artifact missing usable 'model'. Using empirical calculation instead.")
                    self.model = None
                    self.model_artifact = None
                    return

                self.model = loaded
                self.model_artifact = None
                print(f"✅ DO Prediction Model loaded from: {self.model_path}")
            except Exception as e:
                print(f"⚠️  Failed to load DO model: {e}")
                self.model = None
                self.model_artifact = None
        else:
            self.model = None
            self.model_artifact = None

    def _build_do_features(
        self,
        temperature: float,
        ph: float,
        ammonia: float,
        turbidity: float,
    ) -> np.ndarray:
        """Build feature vector matching either wrapped artifact columns or legacy 4-column input."""
        # Wrapped artifact with engineered feature columns.
        if isinstance(self.model_artifact, dict):
            feature_columns = self.model_artifact.get('feature_columns')
            if isinstance(feature_columns, list) and len(feature_columns) > 0:
                now_hour = datetime.now(timezone.utc).hour
                feature_map = {
                    'ph': ph,
                    'ammonia': ammonia,
                    'temp': temperature,
                    'turbidity': turbidity,
                    'hour_sin': math.sin((2.0 * math.pi * now_hour) / 24.0),
                    'hour_cos': math.cos((2.0 * math.pi * now_hour) / 24.0),

                    # Lag and rolling features: single reading fallback approximates current value history.
                    'ph_lag1': ph,
                    'ph_lag2': ph,
                    'ph_lag3': ph,
                    'ph_diff1': 0.0,
                    'ph_roll3_mean': ph,
                    'ph_roll3_std': 0.0,
                    'ammonia_lag1': ammonia,
                    'ammonia_lag2': ammonia,
                    'ammonia_lag3': ammonia,
                    'ammonia_diff1': 0.0,
                    'ammonia_roll3_mean': ammonia,
                    'ammonia_roll3_std': 0.0,
                    'temp_lag1': temperature,
                    'temp_lag2': temperature,
                    'temp_lag3': temperature,
                    'temp_diff1': 0.0,
                    'temp_roll3_mean': temperature,
                    'temp_roll3_std': 0.0,
                    'turbidity_lag1': turbidity,
                    'turbidity_lag2': turbidity,
                    'turbidity_lag3': turbidity,
                    'turbidity_diff1': 0.0,
                    'turbidity_roll3_mean': turbidity,
                    'turbidity_roll3_std': 0.0,

                    # Interaction features
                    'ph_sq': ph ** 2,
                    'ammonia_sq': ammonia ** 2,
                    'temp_sq': temperature ** 2,
                    'ph_ammonia': ph * ammonia,
                    'temp_turbidity': temperature * turbidity,
                }

                row = [float(feature_map.get(column, 0.0)) for column in feature_columns]
                return np.array([row], dtype=float)

        # Legacy direct model input.
        return np.array([[temperature, ph, ammonia, turbidity]], dtype=float)
    
    def calculate_do_empirical(
        self,
        temperature: float,
        ph: float,
        ammonia: float,
        turbidity: float
    ) -> Tuple[float, float]:
        """
        Calculate DO using empirical formula based on water quality parameters
        
        This is a simplified model based on known relationships:
        - Temperature: Higher temp = Lower DO saturation
        - pH: Affects DO solubility
        - Ammonia: High ammonia indicates decomposition (consumes oxygen)
        - Turbidity: High turbidity can indicate organic matter (consumes oxygen)
        
        Returns:
            Tuple of (predicted_do, confidence)
        """
        
        # Base DO saturation at different temperatures (mg/L)
        # Simplified Henry's Law relationship
        do_saturation = 14.652 - 0.41022 * temperature + 0.007991 * (temperature ** 2) - 0.000077774 * (temperature ** 3)
        
        # Adjust for pH (optimal range 6.5-8.5)
        ph_factor = 1.0
        if ph < 6.5:
            ph_factor = 0.85 + (ph - 5.0) * 0.1  # Lower pH slightly reduces DO
        elif ph > 8.5:
            ph_factor = 0.95 - (ph - 8.5) * 0.05  # Higher pH slightly reduces DO
        
        # Adjust for ammonia (high ammonia = more decomposition = less DO)
        ammonia_factor = 1.0
        if ammonia > 0.05:
            ammonia_factor = max(0.6, 1.0 - (ammonia - 0.05) * 1.5)
        
        # Adjust for turbidity (high turbidity = more organic matter = less DO)
        turbidity_factor = 1.0
        if turbidity > 25:
            turbidity_factor = max(0.7, 1.0 - (turbidity - 25) * 0.008)
        
        # Calculate predicted DO
        predicted_do = do_saturation * ph_factor * ammonia_factor * turbidity_factor
        
        # Add some realistic variation
        predicted_do = max(0.0, min(predicted_do, 15.0))  # Clamp to realistic range
        
        # Calculate confidence based on parameter quality
        confidence = 85.0  # Base confidence
        
        # Reduce confidence for extreme values
        if temperature < 20 or temperature > 35:
            confidence -= 10
        if ph < 6.0 or ph > 9.0:
            confidence -= 10
        if ammonia > 0.5:
            confidence -= 10
        if turbidity > 50:
            confidence -= 10
        
        confidence = max(50.0, min(confidence, 95.0))
        
        return predicted_do, confidence
    
    async def predict_do(
        self,
        temperature: float,
        ph: float,
        ammonia: float,
        turbidity: float,
        pond_id: Optional[str] = None,
        thresholds: Optional[DOThreshold] = None,
        ai_mode: bool = True,
        user_id: Optional[str] = None,
        sensor_id: Optional[str] = None
    ) -> Dict:
        """
        Predict dissolved oxygen level
        
        Args:
            temperature: Water temperature in Celsius
            ph: pH level
            ammonia: Ammonia concentration in ppm
            turbidity: Turbidity in NTU
            pond_id: Optional pond identifier
            thresholds: Optional custom DO thresholds
            
        Returns:
            Dictionary with prediction results
        """
        
        # Validate input data first
        validation_data = {
            'temperature': temperature,
            'ph': ph,
            'ammonia': ammonia,
            'turbidity': turbidity
        }
        
        is_valid, errors, warnings = validate_sensor_data(validation_data)
        
        if not is_valid:
            return {
                'success': False,
                'errors': errors,
                'warnings': warnings,
                'predicted_do': None,
                'confidence': 0.0,
                'risk_level': 'UNKNOWN'
            }
        
        # Predict DO using model or calculation
        try:
            if self.model is not None and hasattr(self.model, 'predict'):
                X = self._build_do_features(temperature, ph, ammonia, turbidity)
                with py_warnings.catch_warnings():
                    py_warnings.simplefilter("ignore", category=UserWarning)
                    raw_prediction = self.model.predict(X)[0]

                # If artifact stores class-to-DO mapping, convert class label to mg/L.
                class_to_do = self.model_artifact.get('class_to_do') if isinstance(self.model_artifact, dict) else None
                if isinstance(class_to_do, dict):
                    mapped_do = class_to_do.get(raw_prediction)
                    if mapped_do is None:
                        mapped_do = class_to_do.get(str(raw_prediction))
                    if mapped_do is None:
                        predicted_do = float(raw_prediction)
                    else:
                        predicted_do = float(mapped_do)
                else:
                    predicted_do = float(raw_prediction)

                # Get confidence if model supports it
                if hasattr(self.model, 'predict_proba'):
                    with py_warnings.catch_warnings():
                        py_warnings.simplefilter("ignore", category=UserWarning)
                        proba = self.model.predict_proba(X)
                    if isinstance(proba, list) and len(proba) > 0:
                        confidence = float(np.max(proba[0]) * 100.0)
                    else:
                        confidence = float(np.max(proba) * 100.0)
                else:
                    confidence = 85.0
            else:
                # Use empirical calculation
                predicted_do, confidence = self.calculate_do_empirical(
                    temperature, ph, ammonia, turbidity
                )
        except Exception as e:
            print(f"❌ DO Prediction Error: {e}")
            # Fallback to calculation
            predicted_do, confidence = self.calculate_do_empirical(
                temperature, ph, ammonia, turbidity
            )

        # Get risk level and recommendations
        risk_level = get_do_risk_level(predicted_do, thresholds)
        recommendations = get_do_recommendations(predicted_do, temperature, thresholds)


        # Check AI mode from aiControl_collection
        send_notification = True
        use_ai_mode = ai_mode
        from ..db import aiControl_collection
        if aiControl_collection is not None and pond_id:
            ai_doc = await aiControl_collection.find_one({"pond_id": pond_id})
            if ai_doc and ai_doc.get("aiMode") is True:
                send_notification = False
            else:
                use_ai_mode = False  # If AI mode is off, use rule-based

        if send_notification:
            notification_data = {
                "user_id": user_id,
                "pond_id": pond_id,
                "sensor_id": sensor_id,
                "data": {
                    "temperature": temperature,
                    "ph": ph,
                    "ammonia": ammonia,
                    "turbidity": turbidity,
                    "do": predicted_do
                },
            }
            # Only add detected_issues if using AI mode and a risk is detected
            if use_ai_mode and risk_level and risk_level != "NORMAL":
                notification_data["detected_issues"] = [f"{risk_level}_DO"]

            try:
                await process_and_save_notifications(notification_data, ai_mode=use_ai_mode)
            except Exception as e:
                print(f"[WARN] Failed to save notification: {e}")

        return {
            'success': True,
            'predicted_dissolved_oxygen': round(predicted_do, 2),
            'confidence': round(confidence, 1),
            'risk_level': risk_level,
            'recommendations': recommendations,
            'warnings': warnings,
            'input_parameters': {
                'temperature': temperature,
                'ph': ph,
                'ammonia': ammonia,
                'turbidity': turbidity
            }
        }


# Singleton instance
_do_prediction_service = None


def get_do_prediction_service() -> DOPredictionService:
    """Get or create the DO prediction service singleton"""
    global _do_prediction_service
    if _do_prediction_service is None:
        _do_prediction_service = DOPredictionService()
    return _do_prediction_service


async def predict_dissolved_oxygen(
    temperature: float,
    ph: float,
    ammonia: float,
    turbidity: float,
    pond_id: Optional[str] = None,
    user_id: Optional[str] = None,
    sensor_id: Optional[str] = None,
    ai_mode: bool = True
) -> Dict:
    """
    Convenience function to predict DO
    
    Args:
        temperature: Water temperature in Celsius
        ph: pH level
        ammonia: Ammonia concentration in ppm
        turbidity: Turbidity in NTU
        pond_id: Optional pond identifier
        ai_mode: Whether to use AI mode (True) or rule-based (False)
    
    Returns:
        Dictionary with prediction results
    """
    service = get_do_prediction_service()
    return await service.predict_do(
        temperature, ph, ammonia, turbidity,
        pond_id,
        ai_mode=ai_mode,
        user_id=user_id,
        sensor_id=sensor_id
    )
