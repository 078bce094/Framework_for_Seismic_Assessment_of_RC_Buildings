import numpy as np

# Format
# Time, Axial Strain, Curvature about the local z-axis, Curvature about the local y-axis
# Initial T1, Initial T2, Initial T3, Initial T4, Initial T5, Final T1, Final T2, Final T3, Final T4, Final T5, max_base_shear, MIDR_1st_floor, MIDRall
# MomentCurvature3D(secTag, axialLoad, DimBA, Cover, mu, numIncr, bendingAxis)

from MomentCurvature import *      # NOTE Turn OFF rigid diaphragm for moment curvature analysis

direction = 2  # 1, 2 in X and Y Direction respectively
sample_no = 1

DI_Global_list = []

mu = 15.0           # Target ductility for analysis
numIncr = 100       # Number of analysis increment
P = -1000.0         # Set reference axial load 

if direction == 1:
    phiy, phiu, yieldM, ultM = MomentCurvature3D(Col_1_SecTag, P, Col_1_y, Col_1_Cover, mu, numIncr, 'y')
elif direction == 2:
    phiy, phiu, yieldM, ultM = MomentCurvature3D(Col_1_SecTag, P, Col_1_z, Col_1_Cover, mu, numIncr, 'z')
else:
    print("ERROR Direction.")

# print(phiy, phiu, yieldM, ultM)

for CarlSagan in range(1,2):

    if direction == 1:
        input_dir = f"/Users/niraj/Documents/openseespy/Groups/NBC_105_2020/Output/sample_{sample_no}/Earthquake_{CarlSagan}/outputx"
    elif direction == 2:
        input_dir = f"/Users/niraj/Documents/openseespy/Groups/NBC_105_2020/Output/sample_{sample_no}/Earthquake_{CarlSagan}/outputy"

    beta = 0.1
    Et = []
    Sum_Et = 0.0
    DI_Local = []

    for tag in ground_floor_col_tags:         
        file_curv = [f"{input_dir}/ele{tag}_sec1_curv.out", f"{input_dir}/ele{tag}_sec2_curv.out", f"{input_dir}/ele{tag}_sec3_curv.out", f"{input_dir}/ele{tag}_sec4_curv.out", f"{input_dir}/ele{tag}_sec5_curv.out"] # 4 columns (time, axial strain, κz, κy)

        file_energy = [f"{input_dir}/ele{tag}_energy_sec1.out", f"{input_dir}/ele{tag}_energy_sec2.out", f"{input_dir}/ele{tag}_energy_sec3.out", f"{input_dir}/ele{tag}_energy_sec4.out", f"{input_dir}/ele{tag}_energy_sec5.out"]
            
        phi_list = []
        total_ET = 0.0

        for file in file_curv:
            with open(file) as f:
                data = [list(map(float, line.split()[:4])) for line in f if len(line.split()) >= 4]
                filtered_data = np.array(data)  # time, curvature
            if direction == 1:
                phi = np.max(np.abs(filtered_data[:,3]))    # phi y
            else:
                phi = np.max(np.abs(filtered_data[:,2]))    # phi z
            phi_list.append(phi)
            
        phim = max(np.abs(phi_list))

        for file in file_energy:
            with open(file, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    energy_value = float(last_line.strip().split()[1])
                    total_ET += energy_value

        Et.append(total_ET)
        Sum_Et += total_ET

        print(f"Total Dissipated Energy ET : {total_ET}")
        print(f"Maximum Induced Curvature : {phim}")

        DI_l = ((phim - phiy) / (phiu - phiy)) + ((beta * total_ET) / (yieldM * phiu))
        DI_Local.append(DI_l)

    for i in DI_Local:
        print(f"DI_Local = {i * 100:.2f} %")

    DI_Global = sum(d * e for d, e in zip(DI_Local, Et)) / Sum_Et
    print(f"DI_Global for Earthquake {CarlSagan} = {DI_Global * 100:.2f} %")
    DI_Global_list.append(DI_Global)