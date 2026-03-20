"""
WebSocket Controller
Handles WebSocket connections for AI control and device state management
"""

from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
from typing import List

from ..db import aiControl_collection


# Keep track of connected clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("Client connected, total:", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print("Client disconnected, total:", len(self.active_connections))

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


async def handle_ai_control_websocket(websocket: WebSocket, user_id: str, pond_id: str):
    """
    WebSocket handler for AI Control
    Handles AI mode toggle and manual device control from frontend/mobile app
    """
    await manager.connect(websocket)
    current_mode = "UNKNOWN"
    try:
        init_doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
        init_ai_mode = bool(init_doc.get("aiMode", False)) if init_doc else False
        current_mode = "AI" if init_ai_mode else "MANUAL"
        print(f"\n🔌 AI CONTROL WS CONNECTED")
        print(f"   User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
        print(f"   Initial Mode: {current_mode}")
        print(f"   AI Enabled: {init_ai_mode} {'✅' if init_ai_mode else '❌'}")
        print(f"   Manual Enabled: {not init_ai_mode} {'✅' if not init_ai_mode else '❌'}\n")
    except Exception as init_err:
        print(f"⚠️  Failed to load initial mode for WS connect: {init_err}")

    try:
        while True:
            data = await websocket.receive_json()
            print(f"📩 WS PAYLOAD ({user_id[:8]}.../{pond_id[:8]}...): {data}")
            # Expected: {"aiMode": true/false} or {"device": "aerator", "action": "ON"} or {"type": "query"}
            
            if data.get("type") == "query":
                # Query for current state
                query_type = data.get("query", "state")
                request_id = data.get("requestId")
                if query_type == "state":
                    doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
                    if doc:
                        await manager.send_personal_message({
                            "type": "state_response",
                            "requestId": request_id,
                            "aiMode": doc.get("aiMode", False),
                            "devices": doc.get("devices", {"aerator": False, "waterpump": False, "heater": False}),
                        }, websocket)
                    else:
                        await manager.send_personal_message({
                            "type": "state_response",
                            "requestId": request_id,
                            "aiMode": False,
                            "devices": {"aerator": False, "waterpump": False, "heater": False},
                        }, websocket)
            
            elif "aiMode" in data:
                # AI Mode toggle
                ai_mode = bool(data.get("aiMode", False))
                devices = {"aerator": False, "waterpump": False, "heater": False}
                previous_mode = False

                doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
                if doc:
                    devices = doc.get("devices", devices)
                    previous_mode = bool(doc.get("aiMode", False))
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

                mode_before = "AI" if previous_mode else "MANUAL"
                mode_after = "AI" if ai_mode else "MANUAL"
                current_mode = mode_after
                print(f"\n🔀 MODE SWITCH")
                print(f"   User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
                print(f"   {mode_before} -> {mode_after}")
                print(f"   AI Enabled: {ai_mode} {'✅' if ai_mode else '❌'}")
                print(f"   Manual Enabled: {not ai_mode} {'✅' if not ai_mode else '❌'}\n")
                
                await manager.send_personal_message({
                    "type": "ai_mode",
                    "aiMode": ai_mode,
                    "devices": devices,
                    "status": "updated"
                }, websocket)
            
            elif "device" in data and "action" in data:
                # Device control
                device = data.get("device", "").lower()
                action = data.get("action", "").upper()
                
                print(f"\n🎛️  MANUAL DEVICE CONTROL (WebSocket)")
                print(f"   User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
                print(f"   Device: {device.upper()} → {action} {'✅' if action == 'ON' else '❌'}")

                valid_devices = ["aerator", "waterpump", "heater"]
                if device not in valid_devices or action not in ["ON", "OFF"]:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": "Invalid device or action"
                    }, websocket)
                    continue

                execution_time = datetime.now(timezone.utc)
                doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
                
                ai_mode = False
                devices = {"aerator": False, "waterpump": False, "heater": False}
                
                if doc:
                    ai_mode = doc.get("aiMode", False)
                    devices = doc.get("devices", devices)
                    devices[device] = (action == "ON")
                    
                    await aiControl_collection.update_one(
                        {"user_id": user_id, "pond_id": pond_id},
                        {"$set": {
                            "devices": devices,
                            "updated_at": execution_time
                        }}
                    )
                else:
                    devices[device] = (action == "ON")
                    await aiControl_collection.insert_one({
                        "user_id": user_id,
                        "pond_id": pond_id,
                        "aiMode": False,
                        "devices": devices,
                        "created_at": execution_time,
                        "updated_at": execution_time
                    })

                print(f"   ✅ Device State Saved to Database")
                print(f"   Active Mode: {'AI' if ai_mode else 'MANUAL'}")
                print(f"   All Devices: Aerator={devices['aerator']}, Waterpump={devices['waterpump']}, Heater={devices['heater']}\n")
                
                await manager.send_personal_message({
                    "type": "device_control",
                    "device": device,
                    "action": action,
                    "devices": devices,
                    "status": "updated"
                }, websocket)

    except WebSocketDisconnect:
        print(f"🔌 AI CONTROL WS DISCONNECTED | User: {user_id[:8]}... | Pond: {pond_id[:8]}... | Last Mode: {current_mode}")
        manager.disconnect(websocket)


async def handle_button_websocket(websocket: WebSocket, user_id: str, pond_id: str):
    """
    WebSocket handler for Button/Device State (ESP32)
    Handles device state requests from ESP32 hardware
    """
    await manager.connect(websocket)
    print(f"\n🔌 BUTTON WS CONNECTED | User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
    
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "unknown")
            
            # Handle handshake from ESP32
            if msg_type == "handshake":
                print(f"🔗 ESP32 Handshake Received | User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
                await manager.send_personal_message({
                    "status": "handshake_acknowledged"
                }, websocket)
            
            # Handle state request from ESP32
            elif msg_type == "state_request":
                print(f"📡 ESP32 State Request | User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
                
                # Fetch current device states from database
                doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
                
                if doc:
                    devices = doc.get("devices", {"aerator": False, "waterpump": False, "heater": False})
                    ai_mode = doc.get("aiMode", False)
                else:
                    devices = {"aerator": False, "waterpump": False, "heater": False}
                    ai_mode = False
                
                print(f"   📤 Sending States to ESP32")
                print(f"   AI Mode: {ai_mode}")
                if ai_mode:
                    print(f"   Mode: AI CONTROL (ESP32 awaiting AI commands via sensor endpoint)")
                    print(f"   Manual Devices: Aerator={devices['aerator']}, Waterpump={devices['waterpump']}, Heater={devices['heater']} (IGNORED - AI Mode ON)\n")
                else:
                    print(f"   Mode: MANUAL CONTROL")
                    print(f"   Manual Devices: Aerator={devices['aerator']}, Waterpump={devices['waterpump']}, Heater={devices['heater']}\n")
                
                # Send device states back to ESP32 in expected format
                await manager.send_personal_message({
                    "type": "state_response",
                    "devices": devices,
                    "aiMode": ai_mode
                }, websocket)
            
            # Fallback for old message format (backward compatibility)
            elif data.get("request_buttons"):
                print(f"📡 Old Format State Request | User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
                
                doc = await aiControl_collection.find_one({"user_id": user_id, "pond_id": pond_id})
                
                if doc:
                    devices = doc.get("devices", {"aerator": False, "waterpump": False, "heater": False})
                    ai_mode = doc.get("aiMode", False)
                else:
                    devices = {"aerator": False, "waterpump": False, "heater": False}
                    ai_mode = False
                
                await manager.send_personal_message({
                    "devices": devices,
                    "aiMode": ai_mode
                }, websocket)

    except WebSocketDisconnect:
        print(f"🔌 BUTTON WS DISCONNECTED | User: {user_id[:8]}... | Pond: {pond_id[:8]}...")
        manager.disconnect(websocket)
