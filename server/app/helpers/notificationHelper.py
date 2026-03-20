


PARAMETER_CONFIG = {

    "LOW_TEMP": {
        "parameter": "Temperature",
        "status": "LOW",
        "message": "Temperature is below the safe threshold.",
        "action": "ACTIVATE HEATER TO RESTORE OPTIMAL TEMPERATURE"
    },

    "HIGH_TEMP": {
        "parameter": "Temperature",
        "status": "HIGH",
        "message": "Temperature has exceeded the safe operating range.",
        "action": "ACTIVATE WATER PUMP FOR COOLING AND STABILIZATION"
    },

    "LOW_DO": {
        "parameter": "Dissolved Oxygen",
        "status": "LOW",
        "message": "Dissolved oxygen levels are critically low.",
        "action": "START AERATOR TO INCREASE OXYGEN LEVELS"
    },

    "HIGH_AMMONIA": {
        "parameter": "Ammonia",
        "status": "HIGH",
        "message": "Ammonia concentration has exceeded safe limits.",
        "action": "ACTIVATE WATER PUMP TO REDUCE AMMONIA LEVELS"
    },

    "LOW_PH": {
        "parameter": "pH",
        "status": "LOW",
        "message": "Water acidity level is too high (low pH detected).",
        "action": "MONITOR POND CONDITIONS"
    },

    "HIGH_PH": {
        "parameter": "pH",
        "status": "HIGH",
        "message": "Water alkalinity level is too high (high pH detected).",
        "action": "ACTIVATE WATER PUMP TO RESTORE NEUTRAL pH"
    },

    "LOW_TURBIDITY": {
        "parameter": "Turbidity",
        "status": "LOW",
        "message": "Water clarity is unusually high.",
        "action": "MONITOR POND CONDITIONS"
    },

    "HIGH_TURBIDITY": {
        "parameter": "Turbidity",
        "status": "HIGH",
        "message": "Water turbidity levels indicate potential contamination.",
        "action": "ACTIVATE WATER PUMP TO IMPROVE WATER QUALITY"
    }
}


def get_notification_message(issue_code: str) -> str:

    config = PARAMETER_CONFIG.get(issue_code)

    if not config:
        return "Unknown issue."

    return config["message"]

