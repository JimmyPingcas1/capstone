from datetime import datetime, timezone
import json

from bson import ObjectId
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "fishpond"

# IDs provided for ESP32 testing
USER_ID = "69a39acc56b522b28deec4a9"
POND_ID = "69a39f9cbb28dfc1b9a307fb"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


client = MongoClient(MONGO_URI)
db = client[DB_NAME]
now = utc_now()

user_oid = ObjectId(USER_ID)
pond_oid = ObjectId(POND_ID)

# 1) Ensure one admin account exists
admin_payload = {
    "username": "admin",
    "email": "admin",
    "password": "admin123",
    "name": "System Administrator",
    "role": "admin",
    "status": "Active",
    "updated_at": now,
}
existing_admin = db.admin.find_one({"$or": [{"username": "admin"}, {"email": "admin"}]})
if existing_admin:
    db.admin.update_one({"_id": existing_admin["_id"]}, {"$set": admin_payload})
    admin_action = "updated"
    admin_id = str(existing_admin["_id"])
else:
    admin_insert = {**admin_payload, "created_at": now}
    admin_result = db.admin.insert_one(admin_insert)
    admin_action = "inserted"
    admin_id = str(admin_result.inserted_id)

# 2) Upsert user with requested ID
user_payload = {
    "user_id": USER_ID,
    "name": "ESP32 Tester",
    "email": "esp32.tester@example.com",
    "password": "user123",
    "status": "Active",
    "pond_id": POND_ID,
    "role": "user",
    "updated_at": now,
}
existing_user = db.users.find_one({"$or": [{"user_id": USER_ID}, {"_id": user_oid}]})
if existing_user:
    db.users.update_one({"_id": existing_user["_id"]}, {"$set": user_payload})
    user_action = "updated"
    user_db_id = str(existing_user["_id"])
else:
    user_insert = {"_id": user_oid, **user_payload, "created_at": now}
    db.users.insert_one(user_insert)
    user_action = "inserted"
    user_db_id = str(user_oid)

# 3) Upsert pond with requested ID
pond_payload = {
    "pond_id": POND_ID,
    "name": "ESP32 Test Pond",
    "location": "Section TEST, Block ESP32",
    "user_id": USER_ID,
    "user_name": "ESP32 Tester",
    "devices_count": 6,
    "status": "Active",
    "updated_at": now,
}
existing_pond = db.ponds.find_one({"$or": [{"pond_id": POND_ID}, {"_id": pond_oid}]})
if existing_pond:
    db.ponds.update_one({"_id": existing_pond["_id"]}, {"$set": pond_payload})
    pond_action = "updated"
    pond_db_id = str(existing_pond["_id"])
else:
    pond_insert = {"_id": pond_oid, **pond_payload, "created_at": now}
    db.ponds.insert_one(pond_insert)
    pond_action = "inserted"
    pond_db_id = str(pond_oid)

# 4) Ensure AiButton state row exists for runtime sensor snapshots
ai_control_set = {
    "user_id": USER_ID,
    "pond_id": POND_ID,
    "aiMode": False,
    "devices": {"aerator": False, "waterpump": False, "heater": False},
    "updated_at": now,
}
ai_control_result = db.AiButton.update_one(
    {"user_id": USER_ID, "pond_id": POND_ID},
    {"$set": ai_control_set, "$setOnInsert": {"created_at": now}},
    upsert=True,
)
ai_control_action = "inserted" if ai_control_result.upserted_id else "updated"

# 5) Ensure pond-specific safe levels exist
safe_levels_payload = {
    "pond_id": POND_ID,
    "parameters": [
        {"name": "Temperature", "min": "26.0", "max": "31.0"},
        {"name": "Dissolved Oxygen", "min": "5.5", "max": "9.0"},
        {"name": "Ammonia", "min": "0.000", "max": "0.050"},
        {"name": "pH Level", "min": "6.5", "max": "8.5"},
        {"name": "Turbidity", "min": "0.0", "max": "25.0"},
    ],
    "updated_at": now,
}
safe_levels_result = db.pondSafeLevels.update_one(
    {"pond_id": POND_ID},
    {"$set": safe_levels_payload, "$setOnInsert": {"created_at": now}},
    upsert=True,
)
safe_levels_action = "inserted" if safe_levels_result.upserted_id else "updated"

summary = {
    "admin": {"action": admin_action, "id": admin_id, "email": "admin"},
    "user": {"action": user_action, "_id": user_db_id, "user_id": USER_ID, "email": "esp32.tester@example.com"},
    "pond": {"action": pond_action, "_id": pond_db_id, "pond_id": POND_ID, "name": "ESP32 Test Pond"},
    "ai_button": {"action": ai_control_action, "user_id": USER_ID, "pond_id": POND_ID},
    "safe_levels": {"action": safe_levels_action, "pond_id": POND_ID},
}

print(json.dumps(summary, indent=2))

client.close()
