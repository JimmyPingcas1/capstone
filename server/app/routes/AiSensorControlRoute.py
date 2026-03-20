# app/routes/AiSensorControlRoute.py
from fastapi import APIRouter, WebSocket, Body, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from fastapi import HTTPException

from ..db import aiControl_collection
from ..controller.EspSendDataContoller import process_esp32_sensor_data
from ..controller.websocketController import (
    manager,
    handle_ai_control_websocket,
    handle_button_websocket
)

router = APIRouter()


# ----------------------------
# WebSocket for AI Control
# ----------------------------
@router.websocket("/ws/ai-control/{user_id}/{pond_id}")
async def websocket_ai_control(websocket: WebSocket, user_id: str, pond_id: str):
    await handle_ai_control_websocket(websocket, user_id, pond_id)


# ----------------------------
# WebSocket for Button/Device State (ESP32)
# ----------------------------
@router.websocket("/ws/buttons/{user_id}/{pond_id}")
async def websocket_button_control(websocket: WebSocket, user_id: str, pond_id: str):
    await handle_button_websocket(websocket, user_id, pond_id)



# ESP32 sensor data endpoint
# ----------------------------
@router.post("/api/v1/sensor-ai")
async def sensor_ai_controller(user_id: str = Query(...), pond_id: str = Query(...), data: dict = Body(...)):
    """
    Process sensor data from ESP32:
    - Validates sensor readings for impossible values
    - Predicts dissolved oxygen using AI
    - Stores data in database
    - Returns device control commands if AI mode is ON
    """
    try:
        # Extract sensor readings
        temp = float(data.get("temperature"))
        turbidity = float(data.get("turbidity"))
        ph = float(data.get("ph"))
        ammonia = float(data.get("ammonia"))
        
        # Process sensor data through new controller
        result = await process_esp32_sensor_data(
            user_id=user_id,
            pond_id=pond_id,
            temperature=temp,
            turbidity=turbidity,
            ph=ph,
            ammonia=ammonia
        )
        
        return JSONResponse(content=result)
    
    except ValueError as ve:
        return JSONResponse(
            content={
                "success": False,
                "error": "Invalid sensor data format",
                "details": str(ve)
            },
            status_code=400
        )
    except Exception as e:
        print(f"❌ Sensor AI Controller Error: {e}")
        return JSONResponse(
            content={
                "success": False,
                "error": str(e)
            },
            status_code=500
        )




# NOTE: /api/v1/parameter-fixed endpoint REMOVED
# AI now controls device ON/OFF continuously via sensor response
# No manual "fixed" reporting needed - AI handles state transitions automatically



# ----------------------------
# HTTP Endpoint: GET AI Control Status
# ----------------------------
@router.get("/api/v1/AIControl")
async def get_ai_control_status(user_id: str = Query(...), pond_id: str = Query(...)):
    try:
        doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
        
        if not doc:
            # Return default state
            return {
                "aiMode": False,
                "manualMode": True,
                "devices": {"aerator": False, "waterpump": False, "heater": False}
            }
        
        ai_mode = doc.get("aiMode", False)
        devices = doc.get("devices", {"aerator": False, "waterpump": False, "heater": False})
        
        return {
            "aiMode": ai_mode,
            "manualMode": not ai_mode,
            "devices": devices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# HTTP Endpoint: POST AI Control Toggle
# ----------------------------
@router.post("/api/v1/AIControl")
async def toggle_ai_control(
    user_id: str = Query(...),
    pond_id: str = Query(...),
    data: dict = Body(...)
):
    try:
        ai_mode = bool(data.get("aiMode", False))
        devices = {"aerator": False, "waterpump": False, "heater": False}
        
        print(f"\n🔀 HTTP AI MODE TOGGLE")
        print(f"   User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
        print(f"   Setting AI Mode: {ai_mode} {'✅' if ai_mode else '❌'}")
        
        doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
        
        if doc:
            devices = doc.get("devices", devices)
            await aiControl_collection.update_one(
                {"user_id": user_id, "pond_id": pond_id},
                {"$set": {
                    "aiMode": ai_mode,
                    "updated_at": datetime.now(timezone.utc)
                }}
            )
        else:
            await aiControl_collection.insert_one({
                "user_id": user_id,
                "pond_id": pond_id,
                "aiMode": ai_mode,
                "devices": devices,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
        
        print(f"   ✅ AI Mode Updated Successfully\n")
        
        # Broadcast to all connected WebSocket clients
        await manager.broadcast({
            "type": "ai_mode",
            "aiMode": ai_mode,
            "devices": devices,
            "status": "updated"
        })
        
        return {
            "status": "success",
            "aiMode": ai_mode,
            "manualMode": not ai_mode,
            "devices": devices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# HTTP Endpoint: POST Manual Device Control
# ----------------------------
@router.post("/api/v1/ManualDeviceControl")
async def manual_device_control(
    user_id: str = Query(...),
    pond_id: str = Query(...),
    device: str = Query(...),
    action: str = Query(...)
):
    try:
        device = device.lower()
        action = action.upper()
        
        valid_devices = ["aerator", "waterpump", "heater"]
        if device not in valid_devices or action not in ["ON", "OFF"]:
            raise HTTPException(status_code=400, detail="Invalid device or action")
        
        print(f"\n🎛️  HTTP MANUAL DEVICE CONTROL")
        print(f"   User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
        print(f"   Device: {device.upper()} → {action}")
        
        execution_time = datetime.now(timezone.utc)
        doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
        
        ai_mode = False
        devices = {"aerator": False, "waterpump": False, "heater": False}
        
        if doc:
            print(f"   📋 Found existing document")
            ai_mode = doc.get("aiMode", False)
            devices = doc.get("devices", devices)
            devices[device] = (action == "ON")
            
            result = await aiControl_collection.update_one(
                {"user_id": user_id, "pond_id": pond_id},
                {"$set": {
                    "devices": devices,
                    "updated_at": execution_time
                }}
            )
            print(f"   📝 Update result: matched={result.matched_count}, modified={result.modified_count}")
            
            if result.matched_count == 0:
                print(f"   ⚠️  WARNING: Query didn't match any documents!")
                print(f"      Query: user_id='{user_id}', pond_id='{pond_id}'")
                print(f"      Please verify these values exist in the database")
        else:
            print(f"   📋 No existing document, creating new one")
            devices[device] = (action == "ON")
            result = await aiControl_collection.insert_one({
                "user_id": user_id,
                "pond_id": pond_id,
                "aiMode": False,
                "devices": devices,
                "created_at": execution_time,
                "updated_at": execution_time
            })
            print(f"   ✅ Created new document with ID: {result.inserted_id}")
        
        print(f"   ✅ Device State Updated Successfully")
        print(f"   Active Mode: {'AI' if ai_mode else 'MANUAL'}")
        print(f"   All Devices: Aerator={devices['aerator']}, Waterpump={devices['waterpump']}, Heater={devices['heater']}")
        
        # Broadcast to all connected WebSocket clients
        await manager.broadcast({
            "type": "device_control",
            "device": device,
            "action": action,
            "devices": devices,
            "status": "updated"
        })
        print()
        
        return {
            "status": "success",
            "device": device,
            "action": action,
            "devices": devices,
            "timestamp": execution_time.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------
# HTTP Endpoint: GET Device States
# ----------------------------
@router.get("/api/v1/devices")
async def get_device_states(user_id: str = Query(...), pond_id: str = Query(...)):
    try:
        doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})

        if not doc:
            # Return default state if no document exists
            return {
                "aerator": False,
                "waterpump": False,
                "heater": False
            }

        devices = doc.get("devices", {"aerator": False, "waterpump": False, "heater": False})

        return {
            "aerator": devices.get("aerator", False),
            "waterpump": devices.get("waterpump", False),
            "heater": devices.get("heater", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
