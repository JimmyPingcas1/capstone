from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from ..db import DevicePredictions_collection, pond_collection, sensors_collection, user_collection


router = APIRouter()

# New endpoint: Get true device predictions from DevicePrediction collection
@router.get("/api/v1/admin/device-predictions")
async def get_admin_device_predictions(
    limit: int = Query(default=300, ge=1, le=2000),
    pond_id: str | None = Query(default=None),
):
    _ensure_collections_ready()

    query: dict[str, Any] = {}
    if pond_id:
        query["pond_id"] = pond_id

    prediction_docs = (
        await DevicePredictions_collection.find(
            query,
            {
                "_id": 1,
                "pond_id": 1,
                "sensor_id": 1,
                "devices": 1,
                "detected_issues": 1,
                "final_devices": 1,
                "danger": 1,
                "created_at": 1,
            },
        )
        .sort("created_at", -1)
        .limit(limit)
        .to_list(length=limit)
    )

    results = []
    for doc in prediction_docs:
        ts = doc.get("created_at")
        if isinstance(ts, datetime):
            date_str = ts.date().isoformat()
            time_str = ts.strftime("%H:%M:%S")
        else:
            date_str = ""
            time_str = ""

        results.append({
            "id": str(doc.get("_id")),
            "pondId": doc.get("pond_id", ""),
            "sensorId": doc.get("sensor_id", ""),
            "date": date_str,
            "time": time_str,
            "final_devices": doc.get("final_devices", {}),
            "devices": doc.get("devices", {}),
            "detectedIssues": doc.get("detected_issues", []),
            "danger": doc.get("danger", False),
        })

    return {"devicePredictions": results, "count": len(results)}


def _ensure_collections_ready() -> None:
    if user_collection is None or pond_collection is None or sensors_collection is None:
        raise HTTPException(status_code=500, detail="Database collections are not initialized")


def _to_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _to_optional_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "on", "yes"}:
            return True
        if normalized in {"false", "0", "off", "no"}:
            return False
    return None


def _format_time_label(dt: datetime | None) -> str:
    if dt is None:
        return "--"

    # Ensure UTC-like display consistency
    hour = dt.hour
    if hour == 0:
        return "12am"
    if hour == 12:
        return "12pm"
    if hour > 12:
        return f"{hour - 12}pm"
    return f"{hour}am"


def _infer_prediction(do_value: float, risk_level: str | None) -> str:
    if risk_level == "CRITICAL_LOW":
        return "Danger"
    if risk_level == "LOW":
        return "Warning"
    if risk_level == "OPTIMAL":
        return "Good"
    if risk_level == "HIGH":
        return "Excellent"
    if risk_level == "VERY_HIGH":
        return "Excellent"

    if do_value < 4.5:
        return "Danger"
    if do_value < 6.0:
        return "Warning"
    if do_value < 8.0:
        return "Good"
    return "Excellent"


@router.get("/api/v1/admin/dashboard")
async def get_dashboard_data():
    _ensure_collections_ready()

    total_ponds = await pond_collection.count_documents({})
    total_users = await user_collection.count_documents({})

    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    active_pond_ids = await sensors_collection.distinct("pond_id", {"created_at": {"$gte": start_of_day}})
    active_pond_today = len([pid for pid in active_pond_ids if pid])

    recent_docs = (
        await sensors_collection.find(
            {},
            {
                "temperature": 1,
                "ph": 1,
                "ammonia": 1,
                "turbidity": 1,
                "predicted_dissolved_oxygen": 1,
                "created_at": 1,
            },
        )
        .sort("created_at", -1)
        .limit(24)
        .to_list(length=24)
    )

    recent_docs.reverse()
    recent_readings = []
    for doc in recent_docs:
        ts = doc.get("created_at")
        recent_readings.append(
            {
                "time": _format_time_label(ts),
                "temp": _to_float(doc.get("temperature")),
                "ph": _to_float(doc.get("ph")),
                "ammonia": _to_float(doc.get("ammonia")),
                "turbidity": _to_float(doc.get("turbidity")),
                "do": _to_float(doc.get("predicted_dissolved_oxygen")),
            }
        )

    return {
        "totalPonds": total_ponds,
        "totalUsers": total_users,
        "activePondToday": active_pond_today,
        "recentReadings": recent_readings,
    }


@router.get("/api/v1/admin/users")
async def get_admin_users():
    _ensure_collections_ready()

    docs = await user_collection.find({}).sort("created_at", -1).to_list(length=2000)

    users = []
    for doc in docs:
        users.append(
            {
                "id": str(doc.get("_id")),
                "user_id": doc.get("user_id", ""),
                "name": doc.get("name", "Unknown User"),
                "email": doc.get("email", ""),
                "pondId": doc.get("pond_id", ""),
                "status": doc.get("status", "Active"),
            }
        )

    return {"users": users, "count": len(users)}


@router.get("/api/v1/admin/ponds")
async def get_admin_ponds():
    _ensure_collections_ready()

    docs = await pond_collection.find({}).sort("created_at", -1).to_list(length=2000)

    ponds = []
    for doc in docs:
        ponds.append(
            {
                "id": str(doc.get("_id")),
                "pond_id": doc.get("pond_id", ""),
                "name": doc.get("name", "Unnamed Pond"),
                "location": doc.get("location", "Unknown Location"),
                "user_id": doc.get("user_id", ""),
                "user_name": doc.get("user_name", "Unassigned"),
                "devices": int(doc.get("devices_count", 0)),
                "status": doc.get("status", "Active"),
            }
        )

    return {"ponds": ponds, "count": len(ponds)}


@router.get("/api/v1/admin/records")
async def get_admin_records(
    limit: int = Query(default=300, ge=1, le=2000),
    pond_id: str | None = Query(default=None),
):
    _ensure_collections_ready()

    query: dict[str, Any] = {}
    if pond_id:
        query["pond_id"] = pond_id

    sensor_docs = (
        await sensors_collection.find(
            query,
            {
                "pond_id": 1,
                "temperature": 1,
                "ph": 1,
                "ammonia": 1,
                "turbidity": 1,
                "predicted_dissolved_oxygen": 1,
                "water_quality_prediction": 1,
                "do_risk_level": 1,
                "aerator_state": 1,
                "waterpump_state": 1,
                "heater_state": 1,
                "device_state_snapshot": 1,
                "created_at": 1,
            },
        )
        .sort("created_at", -1)
        .limit(limit)
        .to_list(length=limit)
    )

    pond_docs = await pond_collection.find({}, {"pond_id": 1, "name": 1}).to_list(length=2000)
    pond_by_business_id: dict[str, dict[str, Any]] = {}
    pond_by_object_id: dict[str, dict[str, Any]] = {}
    for pond_doc in pond_docs:
        business_id = pond_doc.get("pond_id")
        if business_id is not None:
            pond_by_business_id[str(business_id)] = pond_doc
        pond_doc_id = pond_doc.get("_id")
        if pond_doc_id is not None:
            pond_by_object_id[str(pond_doc_id)] = pond_doc

    prediction_by_sensor_id: dict[str, dict[str, Any]] = {}
    sensor_ids = [str(doc.get("_id")) for doc in sensor_docs if doc.get("_id") is not None]
    if DevicePredictions_collection is not None and sensor_ids:
        prediction_docs = await DevicePredictions_collection.find(
            {"sensor_id": {"$in": sensor_ids}},
            {
                "sensor_id": 1,
                "devices": 1,
                "detected_issues": 1,
            },
        ).to_list(length=len(sensor_ids) * 2)
        for prediction_doc in prediction_docs:
            sensor_id_value = prediction_doc.get("sensor_id")
            if sensor_id_value is not None:
                prediction_by_sensor_id[str(sensor_id_value)] = prediction_doc

    records = []
    for doc in sensor_docs:
        ts = doc.get("created_at")
        if isinstance(ts, datetime):
            date_str = ts.date().isoformat()
            time_str = ts.strftime("%H:%M:%S")
        else:
            date_str = ""
            time_str = ""

        pond_id_value = doc.get("pond_id", "")
        pond_key = str(pond_id_value) if pond_id_value is not None else ""
        pond_doc = pond_by_business_id.get(pond_key) or pond_by_object_id.get(pond_key)
        pond_business_id = str(pond_doc.get("pond_id")) if pond_doc and pond_doc.get("pond_id") is not None else pond_key
        pond_name = pond_doc.get("name", "Unknown Pond") if pond_doc else (pond_key or "Unknown Pond")

        prediction_doc = prediction_by_sensor_id.get(str(doc.get("_id")))
        has_prediction_doc = prediction_doc is not None
        devices_payload = prediction_doc.get("devices") if prediction_doc else {}
        devices_on_raw = devices_payload.get("on", []) if isinstance(devices_payload, dict) else []
        devices_on = {str(device).upper() for device in devices_on_raw}

        sensor_snapshot = doc.get("device_state_snapshot")
        snapshot_aerator = _to_optional_bool(sensor_snapshot.get("aerator")) if isinstance(sensor_snapshot, dict) else None
        snapshot_waterpump = _to_optional_bool(sensor_snapshot.get("waterpump")) if isinstance(sensor_snapshot, dict) else None
        snapshot_heater = _to_optional_bool(sensor_snapshot.get("heater")) if isinstance(sensor_snapshot, dict) else None

        aerator_from_sensor = _to_optional_bool(doc.get("aerator_state"))
        if aerator_from_sensor is None:
            aerator_from_sensor = snapshot_aerator

        waterpump_from_sensor = _to_optional_bool(doc.get("waterpump_state"))
        if waterpump_from_sensor is None:
            waterpump_from_sensor = snapshot_waterpump

        heater_from_sensor = _to_optional_bool(doc.get("heater_state"))
        if heater_from_sensor is None:
            heater_from_sensor = snapshot_heater

        aerator_from_prediction = ("AERATOR" in devices_on) if has_prediction_doc else None
        waterpump_from_prediction = ("WATER_PUMP" in devices_on) if has_prediction_doc else None
        heater_from_prediction = ("HEATER" in devices_on) if has_prediction_doc else None

        aerator_on = aerator_from_sensor if aerator_from_sensor is not None else aerator_from_prediction
        waterpump_on = waterpump_from_sensor if waterpump_from_sensor is not None else waterpump_from_prediction
        heater_on = heater_from_sensor if heater_from_sensor is not None else heater_from_prediction

        detected_issues = prediction_doc.get("detected_issues") if prediction_doc else None
        if detected_issues is not None and not isinstance(detected_issues, list):
            detected_issues = []
        do_value = _to_float(doc.get("predicted_dissolved_oxygen"))
        prediction = doc.get("water_quality_prediction") or _infer_prediction(do_value, doc.get("do_risk_level"))

        records.append(
            {
                "id": str(doc.get("_id")),
                "date": date_str,
                "time": time_str,
                "pondId": pond_business_id,
                "pondName": pond_name,
                "temperature": round(_to_float(doc.get("temperature")), 2),
                "ph": round(_to_float(doc.get("ph")), 2),
                "ammonia": round(_to_float(doc.get("ammonia")), 3),
                "turbidity": round(_to_float(doc.get("turbidity")), 2),
                "do": round(do_value, 2),
                "predicted_dissolved_oxygen": doc.get("predicted_dissolved_oxygen"),
                "prediction": prediction,
                "aeratorOn": aerator_on,
                "waterPumpOn": waterpump_on,
                "heaterOn": heater_on,
                "detectedIssues": [str(issue) for issue in detected_issues] if detected_issues is not None else None,
            }
        )

    return {"records": records, "count": len(records)}
