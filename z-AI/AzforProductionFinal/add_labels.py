import pandas as pd
import numpy as np

# Read the CSV
df = pd.read_csv('withTimePondData_station1.csv')

# Apply the same 5-class labeling function used in training
def do_band(do_val):
    conditions = [
        do_val < 2.5,                           # Danger
        (do_val >= 2.5) & (do_val < 4.0),      # Poor
        (do_val >= 4.0) & (do_val < 5.5),      # Fair
        (do_val >= 5.5) & (do_val < 8.5),      # Good
        do_val >= 8.5                           # Excellent
    ]
    choices = ['Danger', 'Poor', 'Fair', 'Good', 'Excellent']
    return np.select(conditions, choices, default='Unknown')

# Add the 'do' label column right after DO column
df['do'] = do_band(df['DO'])

# Reorder columns to put 'do' label after 'DO'
cols = ['Date', 'Time', 'PH', 'AMMONIA', 'TEMP', 'DO', 'do', 'TURBIDITY']
df = df[cols]

# Save with the new column
df.to_csv('withTimePondData_station1.csv', index=False)

# Show summary
print('Added "do" column with classification labels')
print(f'Total rows: {len(df):,}')
print(f'\nColumns: {list(df.columns)}')
print(f'\nLabel distribution (count):')
print(df['do'].value_counts().sort_index())
print(f'\nLabel distribution (%):')
print((df['do'].value_counts(normalize=True).sort_index() * 100).round(2))
print(f'\nFirst 5 rows:')
print(df.head())
