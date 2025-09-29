# source /Users/niraj/x86_env/bin/activate 

import numpy as np

# data_dir = '/Users/niraj/Documents/Outputs/compiled/SC2_Compiled.csv'
data_dir = '/Users/niraj/Documents/Outputs/compiled/SC1_CCP.csv'
# data_dir = '/Users/niraj/Documents/Outputs/compiled/SC1_NBC_205_1994.csv'
# data_dir = '/Users/niraj/Documents/Outputs/compiled/SC1_NBC_205_2012.csv'
# data_dir = '/Users/niraj/Documents/Outputs/compiled/SC1_NBC_105_2020.csv'
# data_dir = '/Users/niraj/Documents/Outputs/compiled/SC1_NBC_205_2024.csv'

input_data = np.genfromtxt(data_dir, delimiter=',', skip_header=1)

soil_type_A = [496,990,410,4455,139,1052,4863]
soil_type_B = [1045,998,3749,4458,960,5814,949]
soil_type_C = [2990,3285,5665,962,3319,5117,5470]
soil_type_D = [5259,5676,3282,4199,2476,2510,334]

soil_RSN_data = input_data[:,1]
drift_data = input_data[:,38]

for variable in range(4):

    if variable == 0:
        soil_type = soil_type_A
        name = "A"
    elif variable == 1:
        soil_type = soil_type_B
        name = "B"
    elif variable == 2:
        soil_type = soil_type_C
        name = "C"
    elif variable == 3:
        soil_type = soil_type_D
        name = "D"

    slight = 0
    light = 0
    moderate = 0
    extensive = 0
    partial = 0
    collapse = 0

    for i in range(len(drift_data)):
        if soil_RSN_data[i] in soil_type:
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
    print(f"Results for Soil Type: {name}")
    print(f"DG1 = {slight + light}")
    print(f"DG2 = {moderate}")
    print(f"DG3 = {extensive}")
    print(f"DG4 = {partial}")
    print(f"DG5 = {collapse}")
    print("========================================================")
