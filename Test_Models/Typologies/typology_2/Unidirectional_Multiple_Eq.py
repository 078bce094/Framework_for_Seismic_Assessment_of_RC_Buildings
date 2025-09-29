# source /Users/niraj/x86_env/bin/activate 

import openseespy.opensees as ops
import numpy as np

import ReadRecord
from Gravity_Analysis import *

print('-------------------------------------------------')
print("Gravity Analysis Done.")
print('-------------------------------------------------')

def EigenValues(nModes):
    lambdas = ops.eigen(nModes)  # returns a list of eigenvalues

    omega = []
    frequencies = []
    periods = []

    for lam in lambdas:
        sqrt_lam = lam ** 0.5
        omega.append(sqrt_lam)
        frequencies.append(sqrt_lam / (2 * np.pi))
        periods.append((2 * np.pi) / sqrt_lam)
    
    return periods

direction = 1    # 1, 2 in X and Y Direction respectively
einstein  = 1    # Earthquake no

if direction == 1:
    print("Earthquake in X Direction...")
elif direction == 2:
    print("Earthquake in Y Direction...")
else:
    print("ERROR Direction")

# -----------------------------------------------------
# Read Earthquake Data
# -----------------------------------------------------

GM_input_dir = '/Users/niraj/Documents/openseespy/Typologies/Earthquake_Data'
GM_input_file = f'{GM_input_dir}/GM_{einstein}.at2'
GM_output_file = f'{GM_input_dir}/record_{einstein}.dat'

# Permform the conversion from SMD record to OpenSees record
dt, nPts = ReadRecord.ReadRecord(GM_input_file, GM_output_file)  

Analysis_output_dir = '/Users/niraj/Documents/openseespy/Typologies/Output'
if direction == 1:
    output_dir = f'{Analysis_output_dir}/Earthquake_{einstein}/outputx'
elif direction == 2:
    output_dir = f'{Analysis_output_dir}/Earthquake_{einstein}/outputy'
else:
    print("ERROR Direction.")  

# -----------------------------------------------------
# Recorders for Column Sections || Change to Elements for final version
# -----------------------------------------------------

temp = 111112

for tag in Column_Tags:                # Change to Element_Tags for final version
    file_curv_sec1 = f"{output_dir}/ele{tag}_sec1_curv.out"
    file_curv_sec2 = f"{output_dir}/ele{tag}_sec2_curv.out"
    file_curv_sec3 = f"{output_dir}/ele{tag}_sec3_curv.out"
    file_curv_sec4 = f"{output_dir}/ele{tag}_sec4_curv.out"
    file_curv_sec5 = f"{output_dir}/ele{tag}_sec5_curv.out"
    file_energy_sec1 = f"{output_dir}/ele{tag}_energy_sec1.out"
    file_energy_sec2 = f"{output_dir}/ele{tag}_energy_sec2.out"
    file_energy_sec3 = f"{output_dir}/ele{tag}_energy_sec3.out"
    file_energy_sec4 = f"{output_dir}/ele{tag}_energy_sec4.out"
    file_energy_sec5 = f"{output_dir}/ele{tag}_energy_sec5.out"

    if tag == temp:
        ops.recorder('Element', '-file', file_curv_sec1, '-time', '-ele', tag, 'section', 1, 'deformation') 
        ops.recorder('Element', '-file', file_curv_sec2, '-time', '-ele', tag, 'section', 2, 'deformation') 
        ops.recorder('Element', '-file', file_curv_sec3, '-time', '-ele', tag, 'section', 3, 'deformation') 
        ops.recorder('Element', '-file', file_curv_sec4, '-time', '-ele', tag, 'section', 4, 'deformation') 
        ops.recorder('Element', '-file', file_curv_sec5, '-time', '-ele', tag, 'section', 5, 'deformation')
        ops.recorder('Element', '-file', file_energy_sec1, '-time', '-ele', tag, 'section', 1,  'energy')  
        ops.recorder('Element', '-file', file_energy_sec2, '-time', '-ele', tag, 'section', 2,  'energy')  
        ops.recorder('Element', '-file', file_energy_sec3, '-time', '-ele', tag, 'section', 3,  'energy')  
        ops.recorder('Element', '-file', file_energy_sec4, '-time', '-ele', tag, 'section', 4,  'energy')  
        ops.recorder('Element', '-file', file_energy_sec5, '-time', '-ele', tag, 'section', 5,  'energy') 

# -----------------------------------------------------
# Setup For Transient Analysis
# -----------------------------------------------------

# Define & apply RAYLEIGH damping parameters (D = αM*M + βKcurr*Kcurrent + βKcomm*KlastCommit + βKinit*Kinitial)
xDamp = 0.05  # damping ratio

# damping contribution switches
MpropSwitch = 1.0
KcurrSwitch = 0.0
KcommSwitch = 1.0
KinitSwitch = 0.0

nEigenI = 1  # mode i
nEigenJ = 3  # mode j

# eigenvalue analysis
lambdaN = ops.eigen(nEigenJ)
lambdaI = lambdaN[nEigenI - 1]
lambdaJ = lambdaN[nEigenJ - 1]

# natural frequencies
omegaI = lambdaI ** 0.5
omegaJ = lambdaJ ** 0.5

# Rayleigh damping coefficients
alphaM = MpropSwitch * xDamp * (2 * omegaI * omegaJ) / (omegaI + omegaJ)
betaKcurr = KcurrSwitch * 2.0 * xDamp / (omegaI + omegaJ)
betaKcomm = KcommSwitch * 2.0 * xDamp / (omegaI + omegaJ)
betaKinit = KinitSwitch * 2.0 * xDamp / (omegaI + omegaJ)

ops.rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm)       # apply Rayleigh damping
# ops.rayleigh(0.0, 0.0, 0.0, 0.000625)

ops.timeSeries('Path', 200, '-filePath', GM_output_file, '-dt', dt, '-factor', g)   # tag = 200
ops.pattern('UniformExcitation',  200,   direction,  '-accel', 200) 

ops.wipeAnalysis()

ops.constraints('Transformation')
# ops.test('NormDispIncr', 1.0e-6, 50)
ops.test('EnergyIncr', 1.0e-5,  20 )
ops.algorithm('Newton')
ops.numberer('RCM')
ops.system('BandGen')
ops.integrator('Newmark',  0.5,  0.25 )
ops.analysis('Transient')

# -----------------------------------------------------
# Eigenvalue analysis before earthquake
# -----------------------------------------------------
Initial_TimePeriods = EigenValues(5)
print("Initial Time Periods : ", [f"{p:.10f}" for p in Initial_TimePeriods])

# -----------------------------------------------------
# Transient Analysis
# -----------------------------------------------------
tFinal = nPts * dt
tCurrent = ops.getTime()
ok = 0

control_node = 1 * 100 + 1 * 10 + NplaneZ
time = []
baseshear = []
control_node_disp = []
drifts_all_floors = [[] for _ in range(NBayZ)]        # One list per floor

while ok == 0 and tCurrent < tFinal: 
    ok = ops.analyze(1, .002)

    if ok != 0:
        print("regular newton failed ... trying ModifiedNewton...")
        ops.test('NormDispIncr', 1.0e-6,  1000, 0)
        ops.algorithm('ModifiedNewton')
        ok = ops.analyze( 1, .002)
        if ok == 0:
            print("ModifiedNewton worked .. back to regular newton")
            ops.test('EnergyIncr', 1.0e-5,  10 )
            ops.algorithm('Newton')
        else:
            print("ModifiedNewton failed ... trying Broyden...")
            ops.algorithm('Broyden')
            ok = ops.analyze( 1, .002)
        if ok == 0:
            print("Broyden worked .. back to regular newton")
            ops.algorithm('Newton')
        else:
            print("Broyden failed ... trying NewtonLineSearch...")
            ops.algorithm('NewtonLineSearch')
            ok = ops.analyze( 1, .002)
        if ok == 0:
            print("NewtonLineSearch worked .. back to regular newton")
            ops.algorithm('Newton')
        else:
            print("NewtonLineSearch failed ... trying KrylovNewton...")
            ops.algorithm('KrylovNewton')
            ok = ops.analyze( 1, .002)
        if ok == 0:
            print("KrylovNewton worked .. back to regular newton")
            ops.algorithm('Newton')
        else:
            print('Analysis Not Successful..')

    tCurrent = ops.getTime()
    time.append(tCurrent)
    ops.reactions()
    basereac = sum(ops.nodeReaction(n, direction) for n in support_nodes)
    baseshear.append(basereac / 1000)
    control_node_disp.append(ops.nodeDisp(control_node, direction))

    for floor in range(NBayZ):
        base_node = nodes_forIDR[floor]   
        top_node = nodes_forIDR[floor + 1]    

        base_disp = ops.nodeDisp(base_node, direction)
        top_disp = ops.nodeDisp(top_node, direction)

        drift = abs(top_disp - base_disp) / bay_width_Z
        drifts_all_floors[floor].append(drift)

# Final Shape
# opsv.plot_defo()
# plt.title("Deformed Shape")
# plt.show()

# -----------------------------------------------------
# Eigenvalue analysis after earthquake
# -----------------------------------------------------
Final_TimePeriods = EigenValues(5)
print("Final Time Periods : ", [f"{p:.10f}" for p in Final_TimePeriods])
print('-------------------------------------------------')
# -----------------------------------------------------
# Maximum Induced Base Shear
# -----------------------------------------------------
max_base_shear = max(np.abs(baseshear))
print(f"Maximum Induced Base Shear = {max_base_shear:.4f} kN")

max_control_node_disp = max(np.abs(control_node_disp))
print(f"Maximum Induced Control Node Displacement = {max_control_node_disp:.4f} mm")

MIDRs = [max(drifts) for drifts in drifts_all_floors]
MIDR_1st_floor = MIDRs[0]
MIDRall = max(MIDRs)

for i in range(NBayZ):
    print(f'MIDR for Floor {i+1} = {MIDRs[i] * 100:.4f} %')

# -----------------------------------------------------
# Exporting Other Data
# -----------------------------------------------------
output_dir_periods = f"/Users/niraj/Documents/openseespy/Typologies/Output/Earthquake_{einstein}" 
periods_bshear_MIDR1_MIDRall = Initial_TimePeriods + Final_TimePeriods + [max_base_shear * 1000] + [MIDR_1st_floor] + [MIDRall]

if direction == 1:
    with open(f"{output_dir_periods}/periods_bshear_MIDR1_MIDRall_X.out", "w") as f:
        f.write(" ".join(f"{p:.10f}" for p in periods_bshear_MIDR1_MIDRall))
else:
    with open(f"{output_dir_periods}/periods_bshear_MIDR1_MIDRall_Y.out", "w") as f:
        f.write(" ".join(f"{p:.10f}" for p in periods_bshear_MIDR1_MIDRall))

# -----------------------------------------------------
# Plots
# -----------------------------------------------------

# plt.plot(time, baseshear)
# plt.title("Base Shear Vs Time Curve")
# plt.xlabel("Time (s)")
# plt.ylabel("Base Shear (kN)")
# plt.grid(True)
# plt.tight_layout()
# plt.show()