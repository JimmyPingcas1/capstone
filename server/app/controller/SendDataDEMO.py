from ..models.DeviceControlModel import model, LABELS, DEVICE_MAP
from ..helpers.RecursivelyConvert import to_native
import numpy as np


async def predict_water_quality(temp, turbidity, do, ph, ammonia, ai_enabled=True):
    X = np.array([[temp, turbidity, do, ph, ammonia]])

    # Predict labels (0/1)
    prediction = model.predict(X)[0]

    # Predict probabilities/confidences
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        confidences = []

        if isinstance(proba, list) or len(proba.shape) == 3:
            for i, label in enumerate(LABELS):
                conf = proba[i][0][1] * 100
                confidences.append(round(conf, 1))
        else:
            confidences = [round(p[1] * 100, 1) for p in proba]
    else:
        confidences = [100 if p == 1 else 0 for p in prediction]

    # Convert NumPy → Python
    labels = {k: int(v) for k, v in zip(LABELS, prediction)}
    devices = [DEVICE_MAP[k] for k, v in labels.items() if v == 1]
    label_confidence = {k: float(v) for k, v in zip(LABELS, confidences)}

    # Do NOT persist anything to the database — return prediction only.
    return to_native({
        "sensor_id": None,
        "prediction_id": None,
        "labels": labels,
        "confidences": label_confidence,
        "devices": list(dict.fromkeys(devices))
    })

