from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from fastapi.exceptions import WebSocketException
import jwt
import os
from ..db import sensors_collection
import asyncio

router = APIRouter()

# JWT settings (should match authRoute.py)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

def get_user_id_from_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise ValueError("user_id missing in token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Token expired")
    except jwt.InvalidTokenError:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")

@router.websocket("/ws/sensor-data/{pond_id}")
async def websocket_sensor_data(websocket: WebSocket, pond_id: str):
    # Expect token as query param: ws://.../ws/sensor-data/{pond_id}?token=...
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        user_id = get_user_id_from_token(token)
    except WebSocketException as e:
        await websocket.close(code=e.code, reason=e.reason)
        return
    await websocket.accept()
    last_sent_id = None
    try:
        while True:
            # Fetch the latest sensor data for the pond and user
            doc = await sensors_collection.find_one(
                {"pond_id": pond_id, "user_id": user_id}, sort=[("created_at", -1)]
            )
            if doc:
                # Only send if new
                if str(doc.get("_id")) != last_sent_id:
                    created_at = doc.get("created_at")
                    if created_at is not None:
                        try:
                            created_at = created_at.isoformat()
                        except Exception:
                            created_at = str(created_at)
                    await websocket.send_json({
                        "_id": str(doc.get("_id")),
                        "user_id": doc.get("user_id"),
                        "pond_id": doc.get("pond_id"),
                        "temperature": doc.get("temperature"),
                        "turbidity": doc.get("turbidity"),
                        "ph": doc.get("ph"),
                        "ammonia": doc.get("ammonia"),
                        "predicted_dissolved_oxygen": doc.get("predicted_dissolved_oxygen"),
                        "do_confidence": doc.get("do_confidence"),
                        "do_risk_level": doc.get("do_risk_level"),
                        "aerator_state": doc.get("aerator_state"),
                        "validation_warnings": doc.get("validation_warnings", []),
                        "created_at": created_at,
                    })
                    last_sent_id = str(doc.get("_id"))
            await asyncio.sleep(2)  # Poll every 2 seconds
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close()
        print(f"[WebSocket Error] {e}")
