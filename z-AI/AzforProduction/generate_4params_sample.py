import joblib
import numpy as np
import pandas as pd

MODEL_PATH = r"C:\Users\USER\Desktop\capstone\z-AI\AforProduction\4ParametersPkl.pkl"
DATA_PATH = r"C:\Users\USER\Desktop\capstone\z-AI\DODO\AforDeviceControlModel\withTimePondData_station1.csv"

artifact = joblib.load(MODEL_PATH)
model = artifact["model"]

df = pd.read_csv(DATA_PATH)
X = pd.DataFrame(
    {
        "pH": pd.to_numeric(df["PH"], errors="coerce"),
        "Ammonia": pd.to_numeric(df["AMMONIA"], errors="coerce"),
        "Temp": pd.to_numeric(df["TEMP"], errors="coerce"),
        "Turbidity": pd.to_numeric(df["TURBIDITY"], errors="coerce"),
    }
).dropna().reset_index(drop=True)

X["pH_Status"] = np.where((X["pH"] >= 6.5) & (X["pH"] <= 8.5), 1, 0)
X["Ammonia_Status"] = np.where(X["Ammonia"] <= 0.05, 1, 0)
X["Temp_Status"] = np.where(X["Temp"] >= 26.0, 1, 0)
X["Turbidity_Status"] = np.where(X["Turbidity"] <= 20.0, 1, 0)

y_actual_wp = np.where((X["Ammonia_Status"] == 0) | (X["Turbidity_Status"] == 0), "ON", "OFF")
y_actual_h = np.where(X["Temp_Status"] == 0, "ON", "OFF")

features = [
    "pH",
    "Ammonia",
    "Temp",
    "Turbidity",
    "pH_Status",
    "Ammonia_Status",
    "Temp_Status",
    "Turbidity_Status",
]
pred = model.predict(X[features].iloc[:20])

y_pred_wp = np.where(pred[:, 0] == 1, "ON", "OFF")
y_pred_h = np.where(pred[:, 1] == 1, "ON", "OFF")

out = pd.DataFrame(
    {
        "No": range(1, 21),
        "pH": X.loc[:19, "pH"].round(2),
        "Ammonia": X.loc[:19, "Ammonia"].round(4),
        "Temp": X.loc[:19, "Temp"].round(2),
        "Turbidity": X.loc[:19, "Turbidity"].round(2),
        "Actual_WaterPump": y_actual_wp[:20],
        "Pred_WaterPump": y_pred_wp,
        "Actual_Heater": y_actual_h[:20],
        "Pred_Heater": y_pred_h,
    }
)
out["Match"] = np.where(
    (out["Actual_WaterPump"] == out["Pred_WaterPump"])
    & (out["Actual_Heater"] == out["Pred_Heater"]),
    "Yes",
    "No",
)

print(out.to_csv(index=False))
print(f"RowMatchRate={((out['Match'] == 'Yes').mean() * 100):.2f}%")
