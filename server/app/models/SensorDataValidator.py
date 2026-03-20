"""
Sensor Data Validator
Validates sensor readings for impossible or unrealistic values in fishpond environments
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ParameterRange:
    """Define realistic ranges for fishpond water quality parameters"""
    min_value: float
    max_value: float
    critical_min: float  # Values below this are impossible/sensor error
    critical_max: float  # Values above this are impossible/sensor error
    name: str
    unit: str


# asdadasasd
# check the parameter ranges for each sensor reading and return any errors or warnings
class SensorDataValidator:
    """Validates sensor readings against realistic fishpond ranges"""
    
    # Define realistic and critical ranges for each parameter
    PARAMETER_RANGES = {
        'temperature': ParameterRange(
            min_value=20.0,      # Minimum realistic for warm-water fish
            max_value=35.0,      # Maximum realistic for warm-water fish
            critical_min=0.0,    # Below freezing impossible in fishponds
            critical_max=45.0,   # Above this would be fatal/impossible
            name='Temperature',
            unit='°C'
        ),
        'ph': ParameterRange(
            min_value=5.0,       # Minimum realistic for fish survival
            max_value=10.0,      # Maximum realistic for fish survival
            critical_min=0.0,    # pH cannot be negative
            critical_max=14.0,   # pH cannot exceed 14
            name='pH Level',
            unit=''
        ),
        'ammonia': ParameterRange(
            min_value=0.0,       # Minimum (ideal)
            max_value=0.5,       # Maximum safe level
            critical_min=0.0,    # Cannot be negative
            critical_max=5.0,    # Extremely toxic, likely sensor error
            name='Ammonia',
            unit='ppm'
        ),
        'turbidity': ParameterRange(
            min_value=0.0,       # Clear water
            max_value=50.0,      # Very turbid
            critical_min=0.0,    # Cannot be negative
            critical_max=1000.0, # Extremely turbid, likely sensor error
            name='Turbidity',
            unit='NTU'
        ),
        'dissolved_oxygen': ParameterRange(
            min_value=3.0,       # Minimum for fish survival
            max_value=12.0,      # Maximum realistic at normal temps
            critical_min=0.0,    # Cannot be negative
            critical_max=20.0,   # Above saturation, likely sensor error
            name='Dissolved Oxygen',
            unit='mg/L'
        )
    }
    
    @classmethod
    def validate_reading(cls, data: Dict[str, float]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate sensor reading data
        
        Args:
            data: Dictionary with sensor readings (temperature, ph, ammonia, turbidity, dissolved_oxygen)
            
        Returns:
            Tuple of (is_valid, errors, warnings)
            - is_valid: True if data passes critical checks
            - errors: List of critical error messages (impossible values)
            - warnings: List of warning messages (unusual but possible values)
        """
        errors = []
        warnings = []
        
        # Map common parameter names
        param_mapping = {
            'temp': 'temperature',
            'do': 'dissolved_oxygen',
            'turbidity': 'turbidity',
            'ph': 'ph',
            'ammonia': 'ammonia'
        }
        
        for key, value in data.items():
            # Normalize parameter name
            param_key = param_mapping.get(key, key)
            
            if param_key not in cls.PARAMETER_RANGES:
                continue
                
            param_range = cls.PARAMETER_RANGES[param_key]
            
            # Check for impossible values (critical errors)
            if value < param_range.critical_min:
                errors.append(
                    f"{param_range.name} value {value}{param_range.unit} is below critical minimum "
                    f"({param_range.critical_min}{param_range.unit}). Possible sensor malfunction."
                )
            elif value > param_range.critical_max:
                errors.append(
                    f"{param_range.name} value {value}{param_range.unit} exceeds critical maximum "
                    f"({param_range.critical_max}{param_range.unit}). Possible sensor malfunction."
                )
            # Check for unusual but possible values (warnings)
            elif value < param_range.min_value:
                warnings.append(
                    f"{param_range.name} value {value}{param_range.unit} is below recommended range "
                    f"({param_range.min_value}-{param_range.max_value}{param_range.unit}). Fish health may be at risk."
                )
            elif value > param_range.max_value:
                warnings.append(
                    f"{param_range.name} value {value}{param_range.unit} exceeds recommended range "
                    f"({param_range.min_value}-{param_range.max_value}{param_range.unit}). Fish health may be at risk."
                )
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    @classmethod
    def validate_batch(cls, readings: List[Dict[str, float]]) -> Dict:
        """
        Validate a batch of sensor readings
        
        Args:
            readings: List of sensor reading dictionaries
            
        Returns:
            Dictionary with validation results including:
            - total_readings: Total number of readings
            - valid_readings: Number of valid readings
            - invalid_readings: Number of invalid readings
            - results: List of validation results for each reading
        """
        results = []
        valid_count = 0
        invalid_count = 0
        
        for idx, reading in enumerate(readings):
            is_valid, errors, warnings = cls.validate_reading(reading)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                
            results.append({
                'reading_index': idx,
                'is_valid': is_valid,
                'errors': errors,
                'warnings': warnings,
                'data': reading
            })
        
        return {
            'total_readings': len(readings),
            'valid_readings': valid_count,
            'invalid_readings': invalid_count,
            'results': results
        }
    
    @classmethod
    def check_abnormal_patterns(cls, readings: List[Dict[str, float]]) -> List[str]:
        """
        Check for abnormal patterns in sequential readings
        (e.g., sudden jumps, constant values that suggest sensor failure)
        
        Args:
            readings: List of sequential sensor readings
            
        Returns:
            List of pattern warnings
        """
        if len(readings) < 2:
            return []
        
        warnings = []
        
        # Check each parameter across readings
        for param_key in ['temperature', 'ph', 'ammonia', 'turbidity', 'dissolved_oxygen']:
            values = []
            for reading in readings:
                # Handle different key names
                value = reading.get(param_key)
                if value is None:
                    value = reading.get({'temperature': 'temp', 'dissolved_oxygen': 'do'}.get(param_key, param_key))
                if value is not None:
                    values.append(value)
            
            if len(values) < 2:
                continue
            
            param_range = cls.PARAMETER_RANGES.get(param_key)
            if not param_range:
                continue
            
            # Check for constant values (possible sensor stuck)
            if len(set(values)) == 1 and len(values) >= 3:
                warnings.append(
                    f"{param_range.name} has been constant at {values[0]}{param_range.unit} "
                    f"for {len(values)} consecutive readings. Check sensor."
                )
            
            # Check for sudden jumps
            for i in range(1, len(values)):
                change = abs(values[i] - values[i-1])
                
                # Define reasonable change thresholds per parameter
                thresholds = {
                    'temperature': 5.0,     # 5°C jump is suspicious
                    'ph': 2.0,              # 2 pH units is suspicious
                    'ammonia': 0.2,         # 0.2 ppm jump is suspicious
                    'turbidity': 30.0,      # 30 NTU jump is suspicious
                    'dissolved_oxygen': 4.0 # 4 mg/L jump is suspicious
                }
                
                threshold = thresholds.get(param_key, float('inf'))
                if change > threshold:
                    warnings.append(
                        f"{param_range.name} jumped from {values[i-1]}{param_range.unit} to "
                        f"{values[i]}{param_range.unit} (change: {change:.2f}). "
                        f"Sudden change detected - verify sensor accuracy."
                    )
        
        return warnings


# Quick validation functions for easy import
def validate_sensor_data(data: Dict[str, float]) -> Tuple[bool, List[str], List[str]]:
    """Quick validation function"""
    return SensorDataValidator.validate_reading(data)


def is_sensor_data_valid(data: Dict[str, float]) -> bool:
    """Check if sensor data is valid (no critical errors)"""
    is_valid, _, _ = SensorDataValidator.validate_reading(data)
    return is_valid
