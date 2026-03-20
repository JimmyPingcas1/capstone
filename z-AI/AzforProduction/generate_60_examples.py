import joblib
import pandas as pd
import numpy as np

# Load the dataset
data_path = r'C:\Users\USER\Desktop\capstone\z-AI\DODO\AforDeviceControlModel\withTimePondData_station1.csv'
df = pd.read_csv(data_path)

# Model 1: Water Quality AI
print("=" * 80)
print("GENERATING 60 EXAMPLES FOR WATER QUALITY MODEL")
print("=" * 80)

# Load water quality model
wq_model = joblib.load(r'C:\Users\USER\Desktop\capstone\z-AI\AforProduction\station1_random_classifier_compact.pkl')

# Feature engineering for water quality model
def prepare_features_wq(df_input):
    df = df_input.copy()
    df['NH3_high'] = (df['AMMONIA'] > 0.05).astype(int)
    df['Temp_low'] = (df['TEMP'] < 26.0).astype(int)
    df['pH_low'] = (df['PH'] < 6.5).astype(int)
    df['pH_high'] = (df['PH'] > 8.5).astype(int)
    df['Turbidity_high'] = (df['TURBIDITY'] > 20.0).astype(int)
    
    df['pH_x_NH3'] = df['PH'] * df['AMMONIA']
    df['Temp_x_Turbidity'] = df['TEMP'] * df['TURBIDITY']
    df['pH_x_Temp'] = df['PH'] * df['TEMP']
    
    df['TotalStressFlags'] = (
        df['NH3_high'] + df['Temp_low'] + df['pH_low'] + 
        df['pH_high'] + df['Turbidity_high']
    )
    
    features = [
        'PH', 'AMMONIA', 'TEMP', 'TURBIDITY',
        'NH3_high', 'Temp_low', 'pH_low', 'pH_high', 'Turbidity_high',
        'pH_x_NH3', 'Temp_x_Turbidity', 'pH_x_Temp', 'TotalStressFlags'
    ]
    
    # Rename for consistency
    df_out = df[features].copy()
    df_out.columns = [
        'pH', 'Ammonia', 'Temp', 'Turbidity',
        'NH3_high', 'Temp_low', 'pH_low', 'pH_high', 'Turbidity_high',
        'pH_x_NH3', 'Temp_x_Turbidity', 'pH_x_Temp', 'TotalStressFlags'
    ]
    
    return df_out

# Select safe, warning, danger scenarios based on DO
safe_df = df[(df['DO'] >= 7.5) & (df['DO'] <= 10.0)].head(20)
warning_df = df[(df['DO'] >= 4.5) & (df['DO'] < 6.5)].head(20)
danger_df = df[df['DO'] < 3.5].head(20)

# Generate predictions for water quality model
def predict_wq(df_subset):
    X = prepare_features_wq(df_subset)
    pred_class = wq_model['model'].predict(X)
    pred_do = wq_model['do_calibrator'].predict(wq_model['model'].predict_proba(X))
    return pred_class, pred_do

safe_class, safe_do = predict_wq(safe_df)
warning_class, warning_do = predict_wq(warning_df)
danger_class, danger_do = predict_wq(danger_df)

# Output for water quality model
wq_output = []
wq_output.append("## SAFE Scenarios (20 examples)\n")
wq_output.append("| pH | Ammonia | Temp | Turbidity | DO | Water_Class | Pred_DO |")
wq_output.append("|---:|---:|---:|---:|---:|---|---:|")
for i in range(len(safe_df)):
    row = safe_df.iloc[i]
    wq_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['TURBIDITY']:.0f} | {row['DO']:.1f} | {safe_class[i]} | {safe_do[i]:.1f} |")

wq_output.append("\n## WARNING Scenarios (20 examples)\n")
wq_output.append("| pH | Ammonia | Temp | Turbidity | DO | Water_Class | Pred_DO |")
wq_output.append("|---:|---:|---:|---:|---:|---|---:|")
for i in range(len(warning_df)):
    row = warning_df.iloc[i]
    wq_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['TURBIDITY']:.0f} | {row['DO']:.1f} | {warning_class[i]} | {warning_do[i]:.1f} |")

wq_output.append("\n## DANGER Scenarios (20 examples)\n")
wq_output.append("| pH | Ammonia | Temp | Turbidity | DO | Water_Class | Pred_DO |")
wq_output.append("|---:|---:|---:|---:|---:|---|---:|")
for i in range(len(danger_df)):
    row = danger_df.iloc[i]
    wq_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['TURBIDITY']:.0f} | {row['DO']:.1f} | {danger_class[i]} | {danger_do[i]:.1f} |")

with open(r'C:\Users\USER\Desktop\capstone\z-AI\AforProduction\wq_60_examples.txt', 'w') as f:
    f.write('\n'.join(wq_output))

print("Water Quality model: 60 examples saved to wq_60_examples.txt")

# Model 2: Actuator Control Full (pondContol.pkl)
print("=" * 80)
print("GENERATING 60 EXAMPLES FOR ACTUATOR CONTROL FULL MODEL")
print("=" * 80)

actuator_model = joblib.load(r'C:\Users\USER\Desktop\capstone\z-AI\AforProduction\pondContol.pkl')

# Feature engineering for actuator model
def prepare_features_actuator(df_input):
    df = df_input.copy()
    df['pH_Status'] = ((df['PH'] >= 6.5) & (df['PH'] <= 8.5)).astype(int)
    df['Ammonia_Status'] = (df['AMMONIA'] <= 0.05).astype(int)
    df['Temp_Status'] = (df['TEMP'] >= 26.0).astype(int)
    df['DO_Status'] = ((df['DO'] >= 6.0) & (df['DO'] <= 8.5)).astype(int)
    df['Turbidity_Status'] = (df['TURBIDITY'] <= 20.0).astype(int)
    
    df_out = df[['PH', 'AMMONIA', 'TEMP', 'DO', 'TURBIDITY',
                'pH_Status', 'Ammonia_Status', 'Temp_Status', 'DO_Status', 'Turbidity_Status']].copy()
    df_out.columns = ['pH', 'Ammonia', 'Temp', 'DO', 'Turbidity',
                'pH_Status', 'Ammonia_Status', 'Temp_Status', 'DO_Status', 'Turbidity_Status']
    return df_out

# Select scenarios based on DO for actuator model (same as water quality)
safe_act_df = df[(df['DO'] >= 7.5) & (df['DO'] <= 10.0)].head(20)
warning_act_df = df[(df['DO'] >= 4.5) & (df['DO'] < 6.5)].head(20)
danger_act_df = df[df['DO'] < 3.5].head(20)

# Generate predictions
def predict_actuator(df_subset):
    X = prepare_features_actuator(df_subset)
    pred = actuator_model.predict(X)
    return pred

safe_act_pred = predict_actuator(safe_act_df)
warning_act_pred = predict_actuator(warning_act_df)
danger_act_pred = predict_actuator(danger_act_df)

# Output for actuator control full
act_output = []
act_output.append("## SAFE Scenarios (20 examples)\n")
act_output.append("| pH | Ammonia | Temp | DO | Turbidity | Aerator | Water_Pump | Heater |")
act_output.append("|---:|---:|---:|---:|---:|---|---|---|")
for i in range(len(safe_act_df)):
    row = safe_act_df.iloc[i]
    act_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['DO']:.1f} | {row['TURBIDITY']:.0f} | {'ON' if safe_act_pred[i][0] == 1 else 'OFF'} | {'ON' if safe_act_pred[i][1] == 1 else 'OFF'} | {'ON' if safe_act_pred[i][2] == 1 else 'OFF'} |")

act_output.append("\n## WARNING Scenarios (20 examples)\n")
act_output.append("| pH | Ammonia | Temp | DO | Turbidity | Aerator | Water_Pump | Heater |")
act_output.append("|---:|---:|---:|---:|---:|---|---|---|")
for i in range(len(warning_act_df)):
    row = warning_act_df.iloc[i]
    act_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['DO']:.1f} | {row['TURBIDITY']:.0f} | {'ON' if warning_act_pred[i][0] == 1 else 'OFF'} | {'ON' if warning_act_pred[i][1] == 1 else 'OFF'} | {'ON' if warning_act_pred[i][2] == 1 else 'OFF'} |")

act_output.append("\n## DANGER Scenarios (20 examples)\n")
act_output.append("| pH | Ammonia | Temp | DO | Turbidity | Aerator | Water_Pump | Heater |")
act_output.append("|---:|---:|---:|---:|---:|---|---|---|")
for i in range(len(danger_act_df)):
    row = danger_act_df.iloc[i]
    act_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['DO']:.1f} | {row['TURBIDITY']:.0f} | {'ON' if danger_act_pred[i][0] == 1 else 'OFF'} | {'ON' if danger_act_pred[i][1] == 1 else 'OFF'} | {'ON' if danger_act_pred[i][2] == 1 else 'OFF'} |")

with open(r'C:\Users\USER\Desktop\capstone\z-AI\AforProduction\actuator_60_examples.txt', 'w') as f:
    f.write('\n'.join(act_output))

print("Actuator Control Full model: 60 examples saved to actuator_60_examples.txt")

# Model 3: Actuator Control 4-Parameters
print("=" * 80)
print("GENERATING 60 EXAMPLES FOR 4-PARAMETER MODEL")
print("=" * 80)

param4_model = joblib.load(r'C:\Users\USER\Desktop\capstone\z-AI\AforProduction\4ParametersPkl.pkl')

# Feature engineering for 4-parameter model
def prepare_features_4param(df_input):
    df = df_input.copy()
    df['pH_Status'] = ((df['PH'] >= 6.5) & (df['PH'] <= 8.5)).astype(int)
    df['Ammonia_Status'] = (df['AMMONIA'] <= 0.05).astype(int)
    df['Temp_Status'] = (df['TEMP'] >= 26.0).astype(int)
    df['Turbidity_Status'] = (df['TURBIDITY'] <= 20.0).astype(int)
    
    df_out = df[['PH', 'AMMONIA', 'TEMP', 'TURBIDITY',
                'pH_Status', 'Ammonia_Status', 'Temp_Status', 'Turbidity_Status']].copy()
    df_out.columns = ['pH', 'Ammonia', 'Temp', 'Turbidity',
                'pH_Status', 'Ammonia_Status', 'Temp_Status', 'Turbidity_Status']
    return df_out

# Select scenarios (same as others)
safe_4p_df = df[(df['DO'] >= 7.5) & (df['DO'] <= 10.0)].head(20)
warning_4p_df = df[(df['DO'] >= 4.5) & (df['DO'] < 6.5)].head(20)
danger_4p_df = df[df['DO'] < 3.5].head(20)

# Generate predictions
def predict_4param(df_subset):
    X = prepare_features_4param(df_subset)
    pred = param4_model.predict(X)
    return pred

safe_4p_pred = predict_4param(safe_4p_df)
warning_4p_pred = predict_4param(warning_4p_df)
danger_4p_pred = predict_4param(danger_4p_df)

# Output for 4-parameter model
param4_output = []
param4_output.append("## SAFE Scenarios (20 examples)\n")
param4_output.append("| pH | Ammonia | Temp | Turbidity | pH_Status | Ammonia_Status | Temp_Status | Turbidity_Status | Water_Pump | Heater |")
param4_output.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
for i in range(len(safe_4p_df)):
    row = safe_4p_df.iloc[i]
    X_row = prepare_features_4param(safe_4p_df.iloc[[i]])
    param4_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['TURBIDITY']:.0f} | {X_row['pH_Status'].values[0]} | {X_row['Ammonia_Status'].values[0]} | {X_row['Temp_Status'].values[0]} | {X_row['Turbidity_Status'].values[0]} | {'ON' if safe_4p_pred[i][0] == 1 else 'OFF'} | {'ON' if safe_4p_pred[i][1] == 1 else 'OFF'} |")

param4_output.append("\n## WARNING Scenarios (20 examples)\n")
param4_output.append("| pH | Ammonia | Temp | Turbidity | pH_Status | Ammonia_Status | Temp_Status | Turbidity_Status | Water_Pump | Heater |")
param4_output.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
for i in range(len(warning_4p_df)):
    row = warning_4p_df.iloc[i]
    X_row = prepare_features_4param(warning_4p_df.iloc[[i]])
    param4_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['TURBIDITY']:.0f} | {X_row['pH_Status'].values[0]} | {X_row['Ammonia_Status'].values[0]} | {X_row['Temp_Status'].values[0]} | {X_row['Turbidity_Status'].values[0]} | {'ON' if warning_4p_pred[i][0] == 1 else 'OFF'} | {'ON' if warning_4p_pred[i][1] == 1 else 'OFF'} |")

param4_output.append("\n## DANGER Scenarios (20 examples)\n")
param4_output.append("| pH | Ammonia | Temp | Turbidity | pH_Status | Ammonia_Status | Temp_Status | Turbidity_Status | Water_Pump | Heater |")
param4_output.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
for i in range(len(danger_4p_df)):
    row = danger_4p_df.iloc[i]
    X_row = prepare_features_4param(danger_4p_df.iloc[[i]])
    param4_output.append(f"| {row['PH']:.1f} | {row['AMMONIA']:.3f} | {row['TEMP']:.1f} | {row['TURBIDITY']:.0f} | {X_row['pH_Status'].values[0]} | {X_row['Ammonia_Status'].values[0]} | {X_row['Temp_Status'].values[0]} | {X_row['Turbidity_Status'].values[0]} | {'ON' if danger_4p_pred[i][0] == 1 else 'OFF'} | {'ON' if danger_4p_pred[i][1] == 1 else 'OFF'} |")

with open(r'C:\Users\USER\Desktop\capstone\z-AI\AforProduction\4param_60_examples.txt', 'w') as f:
    f.write('\n'.join(param4_output))

print("4-Parameter model: 60 examples saved to 4param_60_examples.txt")

print("\n" + "=" * 80)
print("ALL 3 MODELS: 60 EXAMPLES EACH GENERATED SUCCESSFULLY")
print("=" * 80)
