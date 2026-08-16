# source /Users/niraj/x86_env/bin/activate 

import numpy as np

data_dir_CCP = '/Users/niraj/Documents/Outputs/compiled/CCP_outputs_compiled.csv'
data_dir_NBC_205_1994 = '/Users/niraj/Documents/Outputs/compiled/NBC_205_1994_outputs_compiled.csv'
data_dir_NBC_205_2012 = '/Users/niraj/Documents/Outputs/compiled/NBC_205_2012_outputs_compiled.csv'
data_dir_NBC_105_2020 = '/Users/niraj/Documents/Outputs/compiled/NBC_105_2020_outputs_compiled.csv'
data_dir_NBC_205_2024 = '/Users/niraj/Documents/Outputs/compiled/NBC_205_2024_outputs_compiled.csv'

data_files = [data_dir_CCP, data_dir_NBC_205_1994, data_dir_NBC_205_2012, data_dir_NBC_105_2020, data_dir_NBC_205_2024]
names = ["CCP", "NBC_205_1994", "NBC_205_2012", "NBC_105_2020", "NBC_205_2024"]
j = 0

for data_dir in data_files:
    input_data = np.genfromtxt(data_dir, delimiter=',', skip_header=1)
    drift_data = input_data[:,37]

    slight = 0
    light = 0
    moderate = 0
    extensive = 0
    partial = 0
    collapse = 0

    for i in range(len(drift_data)):
        if np.isnan(drift_data[i]):
            print("NAN encountered.")
            continue
        if drift_data[i] < 0.13:
            slight = slight + 1
        elif 0.13 <= drift_data[i] < 0.19:
            light = light + 1
        elif 0.19 <= drift_data[i] < 0.56:
            moderate = moderate + 1
        elif 0.56 <= drift_data[i] < 1.63:
            extensive = extensive + 1
        elif 1.63 <= drift_data[i] < 3.34:
            partial = partial + 1
        else:
            collapse = collapse + 1

    print("========================================================")
    print(f"Results for Category: {names[j]}")
    print(f"Slightly Damaged = {slight}")
    print(f"Lightly Damaged = {light}")
    print(f"Moderate Damaged = {moderate}")
    print(f"Extensively Damaged = {extensive}")
    print(f"Partially Collapsed = {partial}")
    print(f"Collapsed = {collapse}")
    print("========================================================")

    j = j + 1
