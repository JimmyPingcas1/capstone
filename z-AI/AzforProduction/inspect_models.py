import joblib
import pandas as pd
from pathlib import Path

base = Path(r"C:/Users/USER/Desktop/capstone/z-AI/AforProduction")

m5 = joblib.load(base / "pondContol.pkl")
m4 = joblib.load(base / "4ParametersPkl.pkl")
mdo = joblib.load(base / "station1_random_classifier_compact.pkl")

print("m5 type:", type(m5))
print("m4 type:", type(m4))
print("mdo keys:", list(mdo.keys()))
print("do feature count:", len(mdo.get("feature_columns", [])))
print("do first 20 features:", mdo.get("feature_columns", [])[:20])

if hasattr(m5, "estimators_") and len(m5.estimators_) > 0:
    print("m5 first estimator features:", getattr(m5.estimators_[0], "feature_names_in_", []))
if hasattr(m4, "estimators_") and len(m4.estimators_) > 0:
    print("m4 first estimator features:", getattr(m4.estimators_[0], "feature_names_in_", []))

df = pd.read_csv(r"C:/Users/USER/Desktop/capstone/z-AI/DODO/AforDeviceControlModel/withTimePondData_station1.csv")

safe = (
    df["PH"].between(6.5, 8.5)
    & (df["AMMONIA"] <= 0.05)
    & (df["TEMP"] >= 26.0)
    & (df["TURBIDITY"] <= 20.0)
    & df["DO"].between(6.0, 8.5)
)

warning = (
    df["PH"].between(6.0, 6.49)
    | df["PH"].between(8.51, 9.0)
    | df["AMMONIA"].between(0.051, 0.08)
    | df["TEMP"].between(24.0, 25.99)
    | df["TURBIDITY"].between(20.01, 30.0)
    | df["DO"].between(4.5, 5.99)
)

danger = (
    (df["PH"] < 6.0)
    | (df["PH"] > 9.0)
    | (df["AMMONIA"] > 0.08)
    | (df["TEMP"] < 24.0)
    | (df["TURBIDITY"] > 30.0)
    | (df["DO"] < 4.5)
)

print("counts safe/warning/danger:", int(safe.sum()), int(warning.sum()), int(danger.sum()))
