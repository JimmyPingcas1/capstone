from __future__ import annotations

"""
MongoDB seeder for fishpond admin/demo data.

What this seeds by default:
- 5 users
- 5 ponds (1 pond per user)
- 60 sensor + prediction records per user (300 total per collection)
- AI control state docs
- Pond safe levels docs (global + per pond)
- Admin account in `admin` collection

Run from `server` folder:
	python app/seed/seeder.py

Optional args:
	python app/seed/seeder.py --users 5 --predictions-per-user 60 --seed 123
	python app/seed/seeder.py --keep-existing
"""

import argparse
import asyncio
import random
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

# Allow running this file directly: `python app/seed/seeder.py`
SERVER_ROOT = Path(__file__).resolve().parents[2]
if str(SERVER_ROOT) not in sys.path:
	sys.path.insert(0, str(SERVER_ROOT))

import app.db as db


@dataclass
class SeedConfig:
	user_count: int = 5
	predictions_per_user: int = 60
	clear_existing: bool = True
	seed: int | None = None


FIRST_NAMES = [
	"John",
	"Jane",
	"Mike",
	"Sarah",
	"Robert",
	"Emily",
	"David",
	"Lisa",
	"Chris",
	"Anna",
]

LAST_NAMES = [
	"Doe",
	"Smith",
	"Johnson",
	"Williams",
	"Brown",
	"Davis",
	"Wilson",
	"Anderson",
	"Taylor",
	"Martin",
]


def clamp(value: float, min_value: float, max_value: float) -> float:
	return max(min_value, min(max_value, value))


def risk_level_from_do(do_value: float) -> str:
	if do_value < 3.0:
		return "CRITICAL_LOW"
	if do_value < 5.0:
		return "LOW"
	if do_value <= 9.0:
		return "OPTIMAL"
	if do_value <= 12.0:
		return "HIGH"
	return "VERY_HIGH"


def random_name(rng: random.Random) -> str:
	return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def build_mode_plan(length: int, rng: random.Random) -> list[str]:
	"""Build a dynamic timeline with guaranteed safe/warning/danger windows."""
	plan = ["safe"] * length

	def place_windows(mode: str, count: int, min_len: int, max_len: int) -> None:
		for _ in range(count):
			win_len = rng.randint(min_len, max_len)
			if win_len >= length:
				start = 0
				end = length
			else:
				start = rng.randint(0, length - win_len)
				end = start + win_len
			for i in range(start, end):
				plan[i] = mode

	# Ensure each user gets at least some warning and danger periods.
	place_windows(mode="danger", count=2, min_len=3, max_len=6)
	place_windows(mode="warning", count=3, min_len=4, max_len=8)

	for i in range(length):
		if plan[i] == "safe" and rng.random() < 0.25:
			plan[i] = "warning"

	return plan


def random_target_for_mode(mode: str, rng: random.Random) -> dict[str, float]:
	"""Generate target values for a given quality mode."""
	if mode == "danger":
		hot_or_cold = rng.random() < 0.5
		acidic_or_alkaline = rng.random() < 0.5
		return {
			"temperature": rng.uniform(33.0, 36.5) if hot_or_cold else rng.uniform(20.0, 24.0),
			"ph": rng.uniform(4.8, 6.0) if acidic_or_alkaline else rng.uniform(8.9, 10.2),
			"ammonia": rng.uniform(0.08, 0.18),
			"turbidity": rng.uniform(30.0, 65.0),
			"do": rng.uniform(1.8, 4.6),
		}

	if mode == "warning":
		warm_bias = rng.random() < 0.5
		ph_high = rng.random() < 0.5
		return {
			"temperature": rng.uniform(30.0, 33.0) if warm_bias else rng.uniform(24.0, 26.0),
			"ph": rng.uniform(8.1, 8.8) if ph_high else rng.uniform(6.0, 6.5),
			"ammonia": rng.uniform(0.03, 0.09),
			"turbidity": rng.uniform(18.0, 35.0),
			"do": rng.uniform(4.3, 6.5),
		}

	# safe
	return {
		"temperature": rng.uniform(26.0, 30.0),
		"ph": rng.uniform(6.7, 8.2),
		"ammonia": rng.uniform(0.005, 0.045),
		"turbidity": rng.uniform(8.0, 24.0),
		"do": rng.uniform(6.0, 9.8),
	}


def step_values(
	current: dict[str, float],
	target: dict[str, float],
	rng: random.Random,
) -> dict[str, float]:
	"""Move current values toward a mode target with noise for realistic dynamics."""
	noise = {
		"temperature": 0.35,
		"ph": 0.08,
		"ammonia": 0.008,
		"turbidity": 1.8,
		"do": 0.30,
	}
	bounds = {
		"temperature": (18.0, 38.0),
		"ph": (4.5, 10.5),
		"ammonia": (0.0, 0.25),
		"turbidity": (0.0, 80.0),
		"do": (1.0, 14.0),
	}

	next_values: dict[str, float] = {}
	for key in ["temperature", "ph", "ammonia", "turbidity", "do"]:
		drift = current[key] + 0.40 * (target[key] - current[key])
		candidate = drift + rng.gauss(0.0, noise[key])
		next_values[key] = clamp(candidate, bounds[key][0], bounds[key][1])

	return next_values


def confidence_value(is_issue: bool, severity: float, rng: random.Random) -> float:
	if is_issue:
		base = rng.uniform(72.0, 94.0)
		return round(clamp(base + severity * 12.0, 60.0, 99.8), 2)
	return round(rng.uniform(2.0, 38.0), 2)


def evaluate_prediction(values: dict[str, float], rng: random.Random) -> dict[str, Any]:
	temp = values["temperature"]
	ph = values["ph"]
	ammonia = values["ammonia"]
	turbidity = values["turbidity"]
	do_value = values["do"]

	low_temp = temp < 26.0
	high_temp = temp > 32.0
	low_do = do_value < 5.0
	high_ammonia = ammonia > 0.05
	ph_imbalance = ph < 6.5 or ph > 8.5
	high_turbidity = turbidity > 25.0
	low_turbidity = turbidity < 5.0

	critical_danger = (
		do_value < 4.5
		or ammonia > 0.08
		or ph < 6.0
		or ph > 9.0
		or temp < 24.0
		or temp > 34.0
		or turbidity > 40.0
	)

	labels = {
		"LOW_TEMP": int(low_temp),
		"HIGH_TEMP": int(high_temp),
		"LOW_DO": int(low_do),
		"HIGH_AMMONIA": int(high_ammonia),
		"PH_IMBALANCE": int(ph_imbalance),
		"HIGH_TURBIDITY": int(high_turbidity),
		"LOW_TURBIDITY": int(low_turbidity),
	}

	detected_issues = [issue for issue, flagged in labels.items() if flagged == 1]

	confidences = {
		"LOW_TEMP": confidence_value(low_temp, max((26.0 - temp) / 6.0, 0.0), rng),
		"HIGH_TEMP": confidence_value(high_temp, max((temp - 32.0) / 6.0, 0.0), rng),
		"LOW_DO": confidence_value(low_do, max((5.0 - do_value) / 4.0, 0.0), rng),
		"HIGH_AMMONIA": confidence_value(high_ammonia, max((ammonia - 0.05) / 0.15, 0.0), rng),
		"PH_IMBALANCE": confidence_value(
			ph_imbalance,
			max(max(6.5 - ph, 0.0), max(ph - 8.5, 0.0)) / 2.0,
			rng,
		),
		"HIGH_TURBIDITY": confidence_value(high_turbidity, max((turbidity - 25.0) / 40.0, 0.0), rng),
		"LOW_TURBIDITY": confidence_value(low_turbidity, max((5.0 - turbidity) / 5.0, 0.0), rng),
	}

	devices_on: list[str] = []
	if low_temp:
		devices_on.append("HEATER")
	if high_temp or high_ammonia or high_turbidity:
		devices_on.append("WATER_PUMP")
	if low_do:
		devices_on.append("AERATOR")

	devices_on = sorted(set(devices_on))
	devices_off = [d for d in ["AERATOR", "WATER_PUMP", "HEATER"] if d not in devices_on]

	if critical_danger:
		prediction_class = "Danger"
	elif detected_issues:
		prediction_class = "Warning" if (low_do or high_ammonia or high_turbidity) else "Fair"
	else:
		prediction_class = "Excellent" if do_value >= 8.4 else "Good"

	return {
		"labels": labels,
		"confidences": confidences,
		"detected_issues": detected_issues,
		"danger": critical_danger,
		"fixed": not critical_danger,
		"prediction_class": prediction_class,
		"devices_on": devices_on,
		"devices_off": devices_off,
	}


def build_users_and_ponds(config: SeedConfig, rng: random.Random) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
	users: list[dict[str, Any]] = []
	ponds: list[dict[str, Any]] = []
	now_utc = datetime.now(timezone.utc)

	for i in range(config.user_count):
		user_code = f"U{i + 1:03d}"
		pond_code = f"P{i + 1:03d}"
		section = chr(ord("A") + (i % 4))
		block = (i % 6) + 1
		pond_slot = rng.randint(1, 24)
		name = random_name(rng)

		user_doc = {
			"user_id": user_code,
			"name": name,
			"email": f"{name.lower().replace(' ', '.')}@example.com",
			"password": "user123",
			"status": "Active" if i < max(1, config.user_count - 1) else "Inactive",
			"pond_id": pond_code,
			"role": "user",
			"created_at": now_utc,
			"updated_at": now_utc,
		}

		pond_doc = {
			"pond_id": pond_code,
			"name": f"Pond {section}-{pond_slot:02d}",
			"location": f"Section {section}, Block {block}",
			"user_id": user_code,
			"user_name": name,
			"devices_count": rng.randint(4, 6),
			"status": "Active",
			"created_at": now_utc,
			"updated_at": now_utc,
		}

		users.append(user_doc)
		ponds.append(pond_doc)

	return users, ponds


def build_safe_levels_docs(ponds: list[dict[str, Any]], rng: random.Random) -> list[dict[str, Any]]:
	now_utc = datetime.now(timezone.utc)
	docs: list[dict[str, Any]] = []

	# Global fallback safe-level document.
	docs.append(
		{
			"parameters": [
				{"name": "Temperature", "min": "26.0", "max": "31.0"},
				{"name": "Dissolved Oxygen", "min": "5.5", "max": "9.0"},
				{"name": "Ammonia", "min": "0.000", "max": "0.050"},
				{"name": "pH Level", "min": "6.5", "max": "8.5"},
				{"name": "Turbidity", "min": "0.0", "max": "25.0"},
			],
			"created_at": now_utc,
			"updated_at": now_utc,
		}
	)

	for pond in ponds:
		temp_min = round(rng.uniform(25.5, 26.5), 1)
		temp_max = round(rng.uniform(30.0, 31.5), 1)
		do_min = round(rng.uniform(5.0, 6.0), 1)
		do_max = round(rng.uniform(8.5, 9.5), 1)
		ammonia_max = round(rng.uniform(0.045, 0.060), 3)
		ph_min = round(rng.uniform(6.4, 6.8), 1)
		ph_max = round(rng.uniform(8.2, 8.7), 1)
		turbidity_max = round(rng.uniform(22.0, 30.0), 1)

		docs.append(
			{
				"pond_id": pond["pond_id"],
				"parameters": [
					{"name": "Temperature", "min": f"{temp_min}", "max": f"{temp_max}"},
					{"name": "Dissolved Oxygen", "min": f"{do_min}", "max": f"{do_max}"},
					{"name": "Ammonia", "min": "0.000", "max": f"{ammonia_max:.3f}"},
					{"name": "pH Level", "min": f"{ph_min}", "max": f"{ph_max}"},
					{"name": "Turbidity", "min": "0.0", "max": f"{turbidity_max}"},
				],
				"created_at": now_utc,
				"updated_at": now_utc,
			}
		)

	return docs


def generate_pond_timeline(
	user_id: str,
	pond_id: str,
	count: int,
	rng: random.Random,
) -> list[dict[str, Any]]:
	"""Create a dynamic, random, but realistic time-series for one pond."""
	mode_plan = build_mode_plan(count, rng)
	current = random_target_for_mode("safe", rng)

	start_time = datetime.now(timezone.utc) - timedelta(minutes=30 * (count - 1))
	rows: list[dict[str, Any]] = []

	for idx in range(count):
		mode = mode_plan[idx]
		target = random_target_for_mode(mode, rng)
		current = step_values(current, target, rng)

		rounded_values = {
			"temperature": round(current["temperature"], 2),
			"ph": round(current["ph"], 2),
			"ammonia": round(current["ammonia"], 3),
			"turbidity": round(current["turbidity"], 2),
			"predicted_dissolved_oxygen": round(current["do"], 2),
		}

		prediction = evaluate_prediction(
			{
				"temperature": rounded_values["temperature"],
				"ph": rounded_values["ph"],
				"ammonia": rounded_values["ammonia"],
				"turbidity": rounded_values["turbidity"],
				"do": rounded_values["predicted_dissolved_oxygen"],
			},
			rng,
		)

		timestamp = start_time + timedelta(minutes=30 * idx)
		do_confidence = round(rng.uniform(78.0, 98.0), 2)

		rows.append(
			{
				"user_id": user_id,
				"pond_id": pond_id,
				"timestamp": timestamp,
				"values": rounded_values,
				"do_confidence": do_confidence,
				"do_risk_level": risk_level_from_do(rounded_values["predicted_dissolved_oxygen"]),
				"prediction": prediction,
			}
		)

	return rows


async def seed_database(config: SeedConfig) -> dict[str, int]:
	db.init_db()

	collections = {
		"users": db.user_collection,
		"ponds": db.pond_collection,
		"sensorsdata": db.sensors_collection,
		"DevicePrediction": db.DevicePredictions_collection,
		"AiButton": db.aiControl_collection,
		# "pondSafeLevels": db.pondSafeLevels_collection,
		"admin": db.admin_collection,
	}

	missing = [name for name, collection in collections.items() if collection is None]
	if missing:
		raise RuntimeError(f"Database collections not initialized: {', '.join(missing)}")

	runtime_seed = config.seed if config.seed is not None else int(datetime.now(timezone.utc).timestamp() * 1_000_000) % (2**31)
	rng = random.Random(runtime_seed)

	if config.clear_existing:
		for name, collection in collections.items():
			deleted = await collection.delete_many({})
			print(f"Cleared {name}: {deleted.deleted_count}")

	users, ponds = build_users_and_ponds(config, rng)
	safe_levels_docs = build_safe_levels_docs(ponds, rng)

	await db.user_collection.insert_many(users)
	await db.pond_collection.insert_many(ponds)
	# await db.pondSafeLevels_collection.insert_many(safe_levels_docs)

	admin_doc = {
		"username": "admin",
		"email": "admin",
		"password": "admin123",
		"name": "System Administrator",
		"role": "admin",
		"status": "Active",
		"created_at": datetime.now(timezone.utc),
		"updated_at": datetime.now(timezone.utc),
	}
	await db.admin_collection.insert_one(admin_doc)

	total_sensor_docs = 0
	total_prediction_docs = 0
	ai_control_docs: list[dict[str, Any]] = []

	for user_doc, pond_doc in zip(users, ponds):
		user_id = user_doc["user_id"]
		pond_id = pond_doc["pond_id"]

		timeline = generate_pond_timeline(
			user_id=user_id,
			pond_id=pond_id,
			count=config.predictions_per_user,
			rng=rng,
		)

		sensor_docs = []
		for row in timeline:
			prediction = row["prediction"]
			devices_on = {str(device).upper() for device in prediction["devices_on"]}
			aerator_state = "AERATOR" in devices_on

			sensor_docs.append(
				{
					"user_id": row["user_id"],
					"pond_id": row["pond_id"],
					"temperature": row["values"]["temperature"],
					"turbidity": row["values"]["turbidity"],
					"ph": row["values"]["ph"],
					"ammonia": row["values"]["ammonia"],
					"predicted_dissolved_oxygen": row["values"]["predicted_dissolved_oxygen"],
					"do_confidence": row["do_confidence"],
					"do_risk_level": row["do_risk_level"],
					"water_quality_prediction": prediction["prediction_class"],
					"aerator_state": aerator_state,
					"validation_warnings": [],
					"created_at": row["timestamp"],
				}
			)

		sensor_insert_result = await db.sensors_collection.insert_many(sensor_docs)
		sensor_ids = sensor_insert_result.inserted_ids
		total_sensor_docs += len(sensor_ids)

		prediction_docs = []
		for idx, row in enumerate(timeline):
			pred = row["prediction"]
			devices = {
				"on": pred["devices_on"],
				"off": pred["devices_off"],
			}
			prediction_docs.append(
				{
					"user_id": row["user_id"],
					"pond_id": row["pond_id"],
					"sensor_id": str(sensor_ids[idx]),
					"sensor_snapshot": {
						"temperature": row["values"]["temperature"],
						"turbidity": row["values"]["turbidity"],
						"ph": row["values"]["ph"],
						"ammonia": row["values"]["ammonia"],
						"predicted_dissolved_oxygen": row["values"]["predicted_dissolved_oxygen"],
					},
					"labels": pred["labels"],
					"confidences": pred["confidences"],
					"devices": devices,
					"danger": pred["danger"],
					"fixed": pred["fixed"],
					"detected_issues": pred["detected_issues"],
					"fixing_status": {
						"fixed": pred["fixed"],
						"detected_issues": pred["detected_issues"],
						"detected_at": row["timestamp"] if pred["danger"] else None,
						"last_evaluated_at": row["timestamp"],
						"fixed_at": row["timestamp"] if pred["fixed"] else None,
					},
					"prediction_class": pred["prediction_class"],
					"created_at": row["timestamp"],
					"updated_at": row["timestamp"],
				}
			)

		prediction_insert_result = await db.DevicePredictions_collection.insert_many(prediction_docs)
		total_prediction_docs += len(prediction_insert_result.inserted_ids)

		last_devices_on = timeline[-1]["prediction"]["devices_on"]
		ai_control_docs.append(
			{
				"user_id": user_id,
				"pond_id": pond_id,
				"aiMode": True,
				"devices": {
					"aerator": "AERATOR" in last_devices_on,
					"waterpump": "WATER_PUMP" in last_devices_on,
					"heater": "HEATER" in last_devices_on,
				},
				"created_at": datetime.now(timezone.utc),
				"updated_at": datetime.now(timezone.utc),
			}
		)

	await db.aiControl_collection.insert_many(ai_control_docs)

	summary = {
		"seed": runtime_seed,
		"users": len(users),
		"ponds": len(ponds),
		"safe_levels": len(safe_levels_docs),
		"ai_controls": len(ai_control_docs),
		"sensors": total_sensor_docs,
		"device_predictions": total_prediction_docs,
		"admins": 1,
	}

	print("\nSeeding complete:")
	for key, value in summary.items():
		print(f"  {key}: {value}")

	if db.client:
		db.client.close()

	return summary


def parse_args() -> SeedConfig:
	parser = argparse.ArgumentParser(description="Seed fishpond MongoDB collections")
	parser.add_argument("--users", type=int, default=5, help="Number of users to create")
	parser.add_argument(
		"--predictions-per-user",
		type=int,
		default=60,
		help="Number of predictions/sensor rows per user",
	)
	parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible output")
	parser.add_argument(
		"--keep-existing",
		action="store_true",
		help="Do not clear existing documents before seeding",
	)
	args = parser.parse_args()

	return SeedConfig(
		user_count=max(1, args.users),
		predictions_per_user=max(1, args.predictions_per_user),
		clear_existing=not args.keep_existing,
		seed=args.seed,
	)


if __name__ == "__main__":
	cfg = parse_args()
	asyncio.run(seed_database(cfg))

