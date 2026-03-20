"""
Smart Notification Helper for Fishpond AI System

- Shows parameter name
- Shows actual sensor value
- Shows LOW / HIGH status
- Suggests device action
"""

from typing import Dict, List


# Mapping AI labels to readable names, units, and device actions
# Enhanced AI Label Mapping with Clear Operational Messages
PARAMETER_CONFIG = {
    "LOW_TEMP": {
        "name": "Temperature",
        "unit": "°C",
        "status": "LOW",
        "message": "Temperature has dropped below the safe threshold.",
        "action": "ACTIVATE HEATER TO RESTORE OPTIMAL TEMPERATURE"
    },
    "HIGH_TEMP": {
        "name": "Temperature",
        "unit": "°C",
        "status": "HIGH",
        "message": "Temperature has exceeded the safe operating range.",
        "action": "ACTIVATE WATER PUMP FOR COOLING AND STABILIZATION"
    },
    "LOW_DO": {
        "name": "Dissolved Oxygen",
        "unit": "mg/L",
        "status": "LOW",
        "message": "Dissolved oxygen levels are critically low.",
        "action": "START AERATOR TO INCREASE OXYGEN LEVELS"
    },
    "HIGH_AMMONIA": {
        "name": "Ammonia",
        "unit": "mg/L",
        "status": "HIGH",
        "message": "Ammonia concentration has exceeded safe limits.",
        "action": "ACTIVATE WATER PUMP TO REDUCE AMMONIA LEVELS"
    },
    "LOW_PH": {
        "name": "pH",
        "unit": "",
        "status": "LOW",
        "message": "Water acidity level is too high (low pH detected).",
        "action": "MONITOR POND CONDITIONS"
    },
    "HIGH_PH": {
        "name": "pH",
        "unit": "",
        "status": "HIGH",
        "message": "Water alkalinity level is too high (high pH detected).",
        "action": "ACTIVATE WATER PUMP TO RESTORE NEUTRAL pH"
    },
    "LOW_TURBIDITY": {
        "name": "Turbidity",
        "unit": "NTU",
        "status": "LOW",
        "message": "Water clarity is unusually high; continuous monitoring recommended.",
        "action": "MONITOR POND CONDITIONS"
    },
    "HIGH_TURBIDITY": {
        "name": "Turbidity",
        "unit": "NTU",
        "status": "HIGH",
        "message": "Water turbidity levels indicate potential contamination.",
        "action": "ACTIVATE WATER PUMP TO IMPROVE WATER QUALITY"
    },
}



def create_notifications(ai_results: Dict[str, float]) -> List[Dict]:
    """
    Convert AI output into structured notifications.
    """

    notifications = []

    for key, value in ai_results.items():

        if key in PARAMETER_CONFIG:
            config = PARAMETER_CONFIG[key]

            # Format value with unit
            if config["unit"]:
                formatted_value = f"{value} {config['unit']}"
            else:
                formatted_value = f"{value}"

            notifications.append({
                "parameter": config["name"],
                "value": value,
                "status": config["status"],
                "message": f"{config['name']}: {formatted_value} — {config['status']}",
                "action": config["action"]
            })

    return notifications
