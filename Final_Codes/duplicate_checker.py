# source /Users/niraj/x86_env/bin/activate

import pandas as pd

# Replace with your actual CSV file path
csv_file = '/Users/niraj/Documents/Outputs/compiled/SC2_Compiled.csv'

# Read the CSV file
df = pd.read_csv(csv_file)

# Check for duplicate rows
duplicates = df[df.duplicated()]

if not duplicates.empty:
    print("Duplicate rows found:")
    print(duplicates)
else:
    print("No duplicate rows found.")