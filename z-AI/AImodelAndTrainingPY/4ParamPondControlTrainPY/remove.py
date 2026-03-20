import pandas as pd

# Load the dataset
df = pd.read_csv("withTimePondData_station1.csv")

# Remove the DO column
df = df.drop(columns=["DO"])

# Save the new dataset
df.to_csv("data_without_do.csv", index=False)

print(df.head())