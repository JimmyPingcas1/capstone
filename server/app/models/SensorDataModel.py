from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class SensorReading(BaseModel):
    """Model for individual sensor reading data"""
    temperature: float = Field(..., description="Water temperature in Celsius")
    ph: float = Field(..., description="pH level of water")
    ammonia: float = Field(..., description="Ammonia concentration in ppm")
    turbidity: float = Field(..., description="Water turbidity in NTU")
    predicted_dissolved_oxygen: float = Field(..., description="AI-predicted dissolved oxygen in mg/L")
    do_confidence: Optional[float] = Field(None, description="DO prediction confidence percentage")
    do_risk_level: Optional[str] = Field(None, description="DO risk level (OPTIMAL/MEDIUM/HIGH/CRITICAL)")
    validation_warnings: Optional[list[str]] = Field(default_factory=list, description="Sensor validation warnings")
    pond_id: Optional[str] = Field(None, description="Pond identifier")
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now, description="Reading timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 28.5,
                "ph": 7.2,
                "ammonia": 0.035,
                "turbidity": 18.5,
                "predicted_dissolved_oxygen": 6.8,
                "do_confidence": 92.5,
                "do_risk_level": "OPTIMAL",
                "validation_warnings": [],
                "pond_id": "P001",
                "user_id": "USER_001",
                "timestamp": "2026-03-09T14:30:00"
            }
        }


class SensorDataBatch(BaseModel):
    """Model for batch sensor readings"""
    readings: list[SensorReading]
    batch_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "readings": [
                    {
                        "temperature": 28.5,
                        "ph": 7.2,
                        "ammonia": 0.035,
                        "turbidity": 18.5,
                        "predicted_dissolved_oxygen": 6.8,
                        "do_confidence": 92.5,
                        "do_risk_level": "OPTIMAL",
                        "pond_id": "P001"
                    }
                ],
                "batch_id": "BATCH_001"
            }
        }


class PredictionRequest(BaseModel):
    """Model for AI prediction request"""
    temperature: float = Field(..., ge=0, le=50, description="Temperature (0-50°C)")
    ph: float = Field(..., ge=0, le=14, description="pH level (0-14)")
    ammonia: float = Field(..., ge=0, description="Ammonia in ppm")
    turbidity: float = Field(..., ge=0, description="Turbidity in NTU")
    predicted_dissolved_oxygen: float = Field(..., ge=0, le=20, description="Predicted DO (0-20 mg/L)")
    pond_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 28.5,
                "ph": 7.2,
                "ammonia": 0.035,
                "turbidity": 18.5,
                "predicted_dissolved_oxygen": 6.8,
                "pond_id": "P001"
            }
        }


class PredictionResponse(BaseModel):
    """Model for AI prediction response"""
    sensor_id: Optional[str]
    prediction_id: Optional[str]
    labels: dict[str, int]
    confidences: dict[str, float]
    devices: list[str]
    is_safe: bool = Field(..., description="Overall safety status")
    warnings: Optional[list[str]] = Field(default_factory=list, description="Warning messages")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sensor_id": "SENSOR_001",
                "prediction_id": "PRED_001",
                "labels": {
                    "LOW_TEMP": 0,
                    "LOW_DO": 0,
                    "HIGH_AMMONIA": 1,
                    "PH_IMBALANCE": 0,
                    "HIGH_TURBIDITY": 0
                },
                "confidences": {
                    "LOW_TEMP": 5.2,
                    "LOW_DO": 12.3,
                    "HIGH_AMMONIA": 87.5,
                    "PH_IMBALANCE": 8.1,
                    "HIGH_TURBIDITY": 15.6
                },
                "devices": ["Water Pump"],
                "is_safe": False,
                "warnings": ["High ammonia detected"]
            }
        }
