"""
Pond Notification Controller
Handles rule-based and AI-based notification generation,
device recommendations, duplicate prevention, and auto-resolving.
"""

from typing import Dict, Any, List
from datetime import datetime
from ..db import pond_notifications_collection
from ..helpers.notificationHelper import PARAMETER_CONFIG, get_notification_message


# =========================================================
# SAVE NOTIFICATION (Prevent Duplicate Unresolved)
# =========================================================
async def save_pond_notification(notification: Dict[str, Any]):

    if pond_notifications_collection is None:
        raise Exception("pond_notifications_collection is not initialized")

    try:
        # Only create a new notification if any sensor value is different from the last notification for this pond (issue type does NOT matter)
        query = {
            "pond_id": notification.get("pond_id")
        }
        last_notif = await pond_notifications_collection.find_one(query, sort=[("created_at", -1)])
        # If no previous notification, always create one
        if last_notif is None:
            result = await pond_notifications_collection.insert_one(notification)
            return result.inserted_id
        # Compare only sensor values (not issues)
        def extract_normalized_param(doc, param):
            # Extracts the value from notification['parameters'][param]['value']
            try:
                val = doc.get("parameters", {}).get(param, {}).get("value")
                return round(float(val), 2) if val is not None else None
            except (TypeError, ValueError):
                return None

        compare_params = [
            "temperature",
            "turbidity",
            "ph",
            "ammonia",
            "predicted_dissolved_oxygen"
        ]
        is_same = True
        debug_compare = []
        for param in compare_params:
            curr = extract_normalized_param(notification, param)
            prev = extract_normalized_param(last_notif, param)
            debug_compare.append(f"{param}: prev={prev} curr={curr}")
            if curr != prev:
                # If both are None, treat as same (missing field)
                if curr is None and prev is None:
                    continue
                is_same = False
        print("[DEBUG] Notification value comparison (sensor values only):", "; ".join(debug_compare))
        if is_same:
            print("[DEBUG] All compared sensor values are the same. No new notification created.")
            return None
        print("[DEBUG] At least one sensor value is different. Creating new notification.")
        result = await pond_notifications_collection.insert_one(notification)
        return result.inserted_id
    except Exception as e:
        print(f"[ERROR] Failed to save notification: {e}")
        raise


# =========================================================
# RESOLVE SAFE NOTIFICATIONS
# =========================================================
async def resolve_safe_notifications(
    pond_id: str,
    sensor_id: str,
    safe_codes: List[str]
):

    # is_resolved logic removed; function is now a no-op
    return


# =========================================================
# DEVICE RULE ENGINE
# =========================================================
def update_devices(devices: Dict[str, bool], code: str):

    code = code.upper()

    if code == "LOW_DO":
        devices["aerator"] = True

    elif code == "LOW_TEMPERATURE":
        devices["heater"] = True

    elif code == "HIGH_TEMPERATURE":
        devices["water_pump"] = True

    elif code == "HIGH_PH":
        devices["water_pump"] = True

    elif code == "HIGH_AMMONIA":
        devices["water_pump"] = True

    elif code == "HIGH_TURBIDITY":
        devices["water_pump"] = True

    # No device suggestion for:
    # LOW_PH
    # LOW_AMMONIA
    # LOW_TURBIDITY


# =========================================================
# MAIN PROCESS FUNCTION
# =========================================================
async def process_and_save_notifications(
    data: Dict[str, Any],
    ai_mode: bool = False
) -> List[str]:

    notification, _ = generate_notification(data, ai_mode=ai_mode)

    inserted_ids = []

    if notification:
        inserted_id = await save_pond_notification(notification)
        if inserted_id:
            inserted_ids.append(str(inserted_id))

    return inserted_ids


# =========================================================
# GENERATE NOTIFICATIONS
# =========================================================
def generate_notification(data: Dict[str, Any], ai_mode: bool = False):


    safe_codes = []
    # Add predicted DO if available (robust extraction)
    def extract_predicted_do(data):
        # Try all possible keys in both root and nested 'data'
        keys = ["predicted_dissolved_oxygen", "predicted_do", "do"]
        # Check root
        for k in keys:
            if k in data and data[k] is not None:
                return data[k]
        # Check nested 'data'
        if "data" in data and isinstance(data["data"], dict):
            for k in keys:
                if k in data["data"] and data["data"][k] is not None:
                    return data["data"][k]
        return None
    predicted_do = extract_predicted_do(data)

    # Always set sensor_id: use data['sensor_id'] if present, else fallback to data['data']['sensor_id'], else generate fallback
    sensor_id = data.get("sensor_id")
    if not sensor_id and "data" in data and isinstance(data["data"], dict):
        sensor_id = data["data"].get("sensor_id")
    if not sensor_id:
        # Fallback: generate a unique sensor_id using timestamp (not ideal, but prevents null)
        sensor_id = f"auto_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"

    base_doc = {
        "pond_id": data.get("pond_id"),
        "sensor_id": sensor_id,
        "created_at": datetime.utcnow().isoformat(),
    }

    # Prepare parameter list and value extraction
    param_keys = [
        ("temperature", "temperature"),
        ("turbidity", "turbidity"),
        ("ph", "ph"),
        ("ammonia", "ammonia"),
        ("predicted_dissolved_oxygen", None)
    ]
    # Get values from data or data['data']
    def extract_val(key, alt_key=None):
        if key == "predicted_dissolved_oxygen":
            return predicted_do
        if key in data:
            return data[key]
        if "data" in data and isinstance(data["data"], dict):
            if key in data["data"]:
                return data["data"][key]
            if alt_key and alt_key in data["data"]:
                return data["data"][alt_key]
        if alt_key and alt_key in data:
            return data[alt_key]
        return None

    # Build parameter status dict
    parameters = {}
    # For each parameter, check if there is a problem, and attach issue/message if so
    # Map for quick lookup of issues/messages
    issue_map = {}
    message_map = {}
    # RULE MODE: build issue/message map
    sensor_data = data.get("data", {})
    rule_checks = [
        ("LOW_DO", "predicted_dissolved_oxygen", "low"),
        ("LOW_TEMPERATURE", "temperature", "low"),
        ("HIGH_TEMPERATURE", "temperature", "high"),
        ("LOW_PH", "ph", "low"),
        ("HIGH_PH", "ph", "high"),
        ("LOW_AMMONIA", "ammonia", "low"),
        ("HIGH_AMMONIA", "ammonia", "high"),
        ("LOW_TURBIDITY", "turbidity", "low"),
        ("HIGH_TURBIDITY", "turbidity", "high"),
    ]
    for code, param, bound in rule_checks:
        value = extract_val(param, "do" if param == "predicted_dissolved_oxygen" else None)
        if value is None:
            continue
        threshold = get_rule_threshold(param if param != "predicted_dissolved_oxygen" else "dissolved_oxygen", bound)
        triggered = False
        if bound == "low" and value < threshold:
            triggered = True
        if bound == "high" and value > threshold:
            triggered = True
        if triggered:
            issue_map[param] = code
            message_map[param] = get_notification_message(code)

    # Build the parameters dict
    for param, alt_key in param_keys:
        value = extract_val(param, alt_key)
        problem = param in issue_map
        parameters[param] = {
            "value": value,
            "problem": problem,
            "issue": issue_map[param] if problem else None,
            "message": message_map[param] if problem else None
        }

    notification_doc = {
        **base_doc,
        "parameters": parameters
    }
    # If at least one problem, return notification
    if any(p["problem"] for p in parameters.values()):
        return notification_doc, []
    else:
        return None, []


# =========================================================
# RULE THRESHOLDS
# =========================================================
def get_rule_threshold(param: str, bound: str) -> float:

    thresholds = {

        "dissolved_oxygen": {
            "low": 3.0,
            "high": 8.0
        },

        "temperature": {
            "low": 20.0,
            "high": 32.0
        },

        "ph": {
            "low": 6.5,
            "high": 8.5
        },

        "ammonia": {
            "low": 0.0,
            "high": 0.5
        },

        "turbidity": {
            "low": 0,
            "high": 10
        }
    }

    return thresholds.get(param, {"low": 0, "high": 9999}).get(bound, 0)