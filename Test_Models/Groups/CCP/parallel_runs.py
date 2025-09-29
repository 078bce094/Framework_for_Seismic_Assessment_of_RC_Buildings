# source /Users/niraj/x86_env/bin/activate 

import numpy as np
import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
import os
import csv
import multiprocessing as mp

# -------------------------------------------------------------
# inputs
# -------------------------------------------------------------

samples_data_file = '/Users/niraj/Documents/openseespy/Groups/CCP/CCP_samples.csv'
samples_data = np.genfromtxt(samples_data_file, delimiter=',', skip_header=1)

sample_no_data = samples_data[:,0]
fc_concrete_data = samples_data[:,1]
fy_steel_data = samples_data[:,2]
beam_area_data = samples_data[:,3]
column_area_data = samples_data[:,4]
bay_width_X_data = samples_data[:,5]
bay_width_Y_data = samples_data[:,6]
bay_width_Z_data = samples_data[:,7]
no_of_bay_X_data = samples_data[:,8]
no_of_bay_Y_data = samples_data[:,9]
no_of_bay_Z_data = samples_data[:,10]
plinth_area_data = samples_data[:,11]

IM_data_file = '/Users/niraj/Documents/openseespy/Groups/Earthquake_Data/IM_Parameters_original.csv'
IM_data = np.genfromtxt(IM_data_file, delimiter=',', skip_header=1)

GM_no_data = IM_data[:,0]
GM_RSN_data = IM_data[:,1]
GM_PGA_data = IM_data[:,2]
GM_PGV_data = IM_data[:,3]
GM_PGD_data = IM_data[:,4]
GM_Vmax_by_Amax_data = IM_data[:,5]
GM_Arms_data = IM_data[:,6]
GM_Vrms_data = IM_data[:,7]
GM_Drms_data = IM_data[:,8]
GM_AI_data = IM_data[:,9]
GM_CI_data = IM_data[:,10]
GM_SED_data = IM_data[:,11]
GM_CAV_data = IM_data[:,12]
GM_HI_data = IM_data[:,15]
GM_SMA_data = IM_data[:,16]
GM_SMV_data = IM_data[:,17]
GM_PP_data = IM_data[:,20]
GM_SD_data = IM_data[:,21]
GM_dT_data = IM_data[:,22]
GM_nPts_data = IM_data[:,23]

# -------------------------------------------------------------
# outputs
# -------------------------------------------------------------

output_csv_file = '/Users/niraj/Documents/openseespy/Groups/CCP/results.csv'

# Output data column titles
headers = [
    'fc_MPa', 'fy_MPa',
    'Beam_Area_m2', 'Col_Area_m2',
    'Bay_Width_X_m', 'Bay_Width_Y_m', 'Bay_Width_Z_m',
    'No_of_bay_X', 'No_of_bay_Y', 'No_of_bay_Z',
    'Plinth_Area_m2', 'Aspect Ratio',

    'Accelerogram', 
    'Max Aceleration (g)', 'Max Velocity (cm/sec)', 'Max Displacement (cm)',
    'Amax/Vmax (1/sec)',
    'Acceleration RMS (g)', 'Velocity RMS (cm/sec)', 'Displacement RMS (cm)',
    'Arias Intensity', 'Characteristic Intensity',
    'Specific Energy Density (cm2/sec)', 'Cum. Abs. Velocity (cm/sec)', 
    'Housner Intensity (cm)', 
    'Sustained Max.Acceleration (g)', 'Sustained Max.Velocity (cm/sec)', 
    'Predominant Period (sec)', 'Significant Duration (sec)',

    'Initial_T1', 'Initial_T2', 'Initial_T3', 'Initial_T4', 'Initial_T5',
    'Final_T1', 'Final_T2', 'Final_T3', 'Final_T4', 'Final_T5',
    'max_base_shear_kN', 'MIDR_1st_floor', 'MIDR_2nd_floor', 'MIDR_all_floor',
    'Park_Ang_DI',
]

# Function to initialize CSV file with headers (run once)
def initialize_csv():
    with open(output_csv_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

# Function to append a row of results (call in your analysis loop)
def append_results(row):
    if len(row) == len(headers):
        with open(output_csv_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

initialize_csv()

# ---------------------------------------------------------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------------------------------------------------------

# Fiber Section Builder -------------------------------------------------------------
def Section(secTag, sec_name, len_y, len_z, cover, nfCore_y, nfCore_z, nfCover_y, nfCover_z, nBT, nBM, nBI, nBB, aBT, aBM, aBI, aBB, coreMatTag, coverMatTag, steelMatTag):

    y1 = len_y / 2.0
    z1 = len_z / 2.0
    c = cover

    fiber_section = [['section', 'Fiber', secTag, '-GJ', 1.0e6],
                     ['patch', 'rect', coreMatTag, nfCore_y, nfCore_z, c - y1, c - z1, y1 - c, z1 - c], # core
                     ['patch', 'quad', coverMatTag, nfCover_y, 2, *[-y1,-z1], *[y1,-z1], *[y1-c,-z1+c], *[-y1+c,-z1+c]], # right side cover
                     ['patch', 'quad', coverMatTag, nfCover_y, 2, *[-y1+c,z1-c], *[y1-c,z1-c], *[y1,z1], *[-y1,z1]],  # left side cover
                     ['patch', 'quad', coverMatTag, 2, nfCover_z, *[-y1,-z1], *[-y1+c,-z1+c], *[-y1+c,z1-c], *[-y1,z1]],  # bottom side cover
                     ['patch', 'quad', coverMatTag, 2, nfCover_z, *[y1-c,-z1+c], *[y1,-z1], *[y1,z1], *[y1-c,z1-c]]]  # top side cover
    
    if nBT > 0:
        fiber_section.append(['layer', 'straight', steelMatTag, nBT, aBT, y1 - c, z1 - c, y1 - c, c - z1]) # top layer
    if nBM > 0:
        fiber_section.append(['layer', 'straight', steelMatTag, nBM, aBM, 0.0, z1 - c, 0.0, c - z1]) # mid layer
    if nBI > 0:
        fiber_section.append(['layer', 'straight', steelMatTag, nBI, aBI, -y1 + c, 0.0, y1 - c, 0.0]) # mid layer perpinducular to y
    if nBB > 0:
        fiber_section.append(['layer', 'straight', steelMatTag, nBB, aBB, - y1 + c, z1 - c, - y1 + c, c - z1]) # bottom layer
    
    title_of_section = sec_name
    opsv.fib_sec_list_to_cmds(fiber_section)
    # matcolor = ['r', 'lightgrey', 'gold', 'w', 'w', 'w']
    # opsv.plot_fiber_section(fiber_section, matcolor=matcolor)
    # plt.title(title_of_section)
    # plt.axis('equal')
    # plt.show()
    return fiber_section

# Moment Curvature Analysis -------------------------------------------------------------
def MomentCurvature3D(secTag, axialLoad, DimBA, Cover, mu, numIncr, bendingAxis, Fy_steel, E0_steel):
    # Estimate yield curvature (Assuming no axial load and only top and bottom steel)
    epsy = Fy_steel / E0_steel   # Steel yield strain
    eff_d = DimBA - Cover   # d -- from top cover to lower rebar center in tension
    Kaxis = epsy/(0.7 * eff_d)    # Approximate yield curvature (when only steel yields)

    maxK = Kaxis * mu  # Maximum curvature for analysis
    
    # Define two nodes at (0,0,0)
    ops.node(1, 0.0, 0.0, 0.0)
    ops.node(2, 0.0, 0.0, 0.0)

    if bendingAxis == 'z':
        # Bending about local y-axis (curvature about z-axis, rotation DOF 6)
        ops.fix(1, 1, 1, 1, 1, 1, 1)
        ops.fix(2, 0, 1, 1, 1, 1, 0)
    elif bendingAxis == 'y':
        # Bending about local z-axis (curvature about y-axis, rotation DOF 5)
        ops.fix(1, 1, 1, 1, 1, 1, 1)
        ops.fix(2, 0, 1, 1, 1, 0, 1)
    else:
        raise ValueError("Invalid bendingAxis. Choose 'y' or 'z'.")

    # element('zeroLengthSection', eleTag, *eleNodes, secTag, <'-orient', *vecx, *vecyp>, <'-doRayleigh', rFlag>)
    ops.element('zeroLengthSection', 1, 1, 2, secTag) # zeroLengthSection element

    # Define constant axial load only at node 2
    ops.timeSeries('Constant', 100)
    ops.pattern('Plain', 100, 100)
    ops.load(2, axialLoad, 0.0, 0.0, 0.0, 0.0, 0.0)

    # Define analysis parameters
    # integrator('LoadControl', incr, numIter=1, minIncr=incr, maxIncr=incr)

    ops.integrator('LoadControl', 0, 1, 0, 0)
    ops.system('SparseGeneral', '-piv')
    ops.test('EnergyIncr', 1e-9, 10)
    ops.numberer('Plain')
    ops.constraints('Plain')
    ops.algorithm('Newton')
    ops.analysis('Static')

    # Apply the constant axial load only and reset time to zero
    ops.analyze(1)
    ops.loadConst('-time', 0.0)

    # Define reference moment based on the bending axis
    ops.timeSeries('Linear', 101)
    ops.pattern('Plain',101, 101)

    if bendingAxis == 'z':
        disp_dof = 6 
    elif bendingAxis == 'y':
        disp_dof = 5
        
    if bendingAxis == 'z':
        ops.load(2, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0)  # Moment about z-axis
    elif bendingAxis == 'y':
        ops.load(2, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)  # Moment about y-axis

    dK = maxK / numIncr
    # integrator('DisplacementControl', nodeTag, dof, incr, numIter=1, dUmin=incr, dUmax=incr)
    ops.integrator('DisplacementControl', 2, disp_dof, dK, 1, dK, dK)

    # Section analysis one step at a time to record results
    moments = []
    curvatures = []

    for i in range(numIncr):
        ops.analyze(1)
        curvature = ops.nodeDisp(2, disp_dof)
        moment = ops.getLoadFactor(101)  # Load factor multiplied by unit moment
        curvatures.append(curvature)
        moments.append(moment)

    # Estimate yield curvature and yield moment
    yield_curvature = None
    yield_moment = None
    for c, m in zip(curvatures, moments):
        if c >= (Kaxis):
            yield_curvature = c
            yield_moment = m
            break

    # Ultimate moment and curvature (maximum moment value)
    ultimate_moment = max(moments)
    ultimate_index = moments.index(ultimate_moment)
    ultimate_curvature = curvatures[ultimate_index]

    return abs(yield_curvature), abs(ultimate_curvature), abs(yield_moment), abs(ultimate_moment)

# ---------------------------------------------------------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------------------------------------------------------

def run_analysis(u, CarlSagan):

    print("------------------------------------------------------------------------")
    print("------------------------------------------------------------------------")
    print("------------------------------------------------------------------------")
    print("Sample Properties...")
    print(f'sample no : {int(sample_no_data[u])}')
    print(f'Concrete Compressive Strength : {fc_concrete_data[u]} MPa')
    print(f'Steel yield Strength : {fy_steel_data[u]} MPa')
    print(f'Beam Area : {beam_area_data[u]} m2')
    print(f'Column Area : {column_area_data[u]} m2')
    print(f'No of Bay in X : {int(no_of_bay_X_data[u])}, Bay Width X = {bay_width_X_data[u]} m')
    print(f'No of Bay in Y : {int(no_of_bay_Y_data[u])}, Bay Width Y = {bay_width_Y_data[u]} m')
    print(f'No of Bay in Z : {int(no_of_bay_Z_data[u])}, Bay Width Z = {bay_width_Z_data[u]} m')
    print(f'Plinth Area : {plinth_area_data[u]} m2')

    # for CarlSagan in range(len(GM_no_data)):

    direction = 2    # 1, 2 in X and Y Direction respectively
    sample_no = int(sample_no_data[u])

    # Read Earthquake Data --------------------------------------------------------------

    GM_input_dir = '/Users/niraj/Documents/openseespy/Groups/Earthquake_Data'
    GM_output_file = f'{GM_input_dir}/GM_{CarlSagan}.dat'
    dt, nPts = GM_dT_data[CarlSagan], GM_nPts_data[CarlSagan]

    Analysis_output_dir = f'/Users/niraj/Documents/openseespy/Groups/CCP/Output/sample_{sample_no}'
    os.makedirs(Analysis_output_dir, exist_ok=True)

    if direction == 1:
        output_dir = f'{Analysis_output_dir}/Earthquake_{CarlSagan}/outputx'
    elif direction == 2:
        output_dir = f'{Analysis_output_dir}/Earthquake_{CarlSagan}/outputy'
    else:
        print("ERROR Direction.")  
    
    os.makedirs(output_dir, exist_ok=True) 

    print("---------------------------------------------------------")
    print("---------------------------------------------------------")
    print("Seismic Properties...")
    print(f'GM no : {int(GM_no_data[CarlSagan])}')
    print(f'RSN : {GM_RSN_data[CarlSagan]}')
    print(f'PGA (g): {GM_PGA_data[CarlSagan]}')
    print(f'Arias Intensity : {GM_AI_data[CarlSagan]}')
    print(f'Predominant Period (sec) : {GM_PP_data[CarlSagan]}')
    print(f'Significant Duration (sec) : {GM_SD_data[CarlSagan]}')
    print("-------------------------------")
        
    output_array = []
    output_array.append(fc_concrete_data[u])
    output_array.append(fy_steel_data[u])
    output_array.append(beam_area_data[u])
    output_array.append(column_area_data[u])
    output_array.append(bay_width_X_data[u]) 
    output_array.append(bay_width_Y_data[u])
    output_array.append(bay_width_Z_data[u])
    output_array.append(no_of_bay_X_data[u])
    output_array.append(no_of_bay_Y_data[u])
    output_array.append(no_of_bay_Z_data[u])
    output_array.append(plinth_area_data[u])
    output_array.append((no_of_bay_X_data[u] * bay_width_X_data[u]) / (no_of_bay_Y_data[u] * bay_width_Y_data[u]))

    output_array.append(GM_RSN_data[CarlSagan])
    output_array.append(GM_PGA_data[CarlSagan])
    output_array.append(GM_PGV_data[CarlSagan])
    output_array.append(GM_PGD_data[CarlSagan])
    output_array.append(1 / GM_Vmax_by_Amax_data[CarlSagan])
    output_array.append(GM_Arms_data[CarlSagan])
    output_array.append(GM_Vrms_data[CarlSagan])
    output_array.append(GM_Drms_data[CarlSagan])
    output_array.append(GM_AI_data[CarlSagan])
    output_array.append(GM_CI_data[CarlSagan])
    output_array.append(GM_SED_data[CarlSagan])
    output_array.append(GM_CAV_data[CarlSagan])
    output_array.append(GM_HI_data[CarlSagan])
    output_array.append(GM_SMA_data[CarlSagan])
    output_array.append(GM_SMV_data[CarlSagan])
    output_array.append(GM_PP_data[CarlSagan])
    output_array.append(GM_SD_data[CarlSagan])

    ops.wipe()
    ops.model('BasicBuilder', '-ndm', 3, '-ndf', 6)

    # --------------------------------------------------------------
    # Geometry, Dimensions And Units (mm, s, N) , Global axes X, Y, Z (vertical) 
    # --------------------------------------------------------------

    # Bays and stories 
    NBayX = int(no_of_bay_X_data[u])  # number of bays in X direction
    NBayY = int(no_of_bay_Y_data[u])  # number of bays in Y direction
    NBayZ = int(no_of_bay_Z_data[u])  # number of bays in Z direction || no of stories

    bay_width_X = bay_width_X_data[u] * 1000 # convert to mm
    bay_width_Y = bay_width_Y_data[u] * 1000 # convert to mm
    bay_width_Z = bay_width_Z_data[u] * 1000 # convert to mm

    slab_thickness = 115.0    # mm

    rigidDiaphragm = 1   # 1 = yes, 0 = no  NOTE : Turn off (0) when doing moment curvature analysis 
    infillIncusion = 2   # 0 = no infills, 1 = infill in X direction only, 2 = infill in Y direction only, 3 = infill in both X and Y

    # Section properties length in local y and z direction
    if beam_area_data[u] == 0.07475:
        Beam_1_y = 325.0
        Beam_1_z = 230.0
        Beam_1_Cover = 30.0

    if column_area_data[u] == 0.0529:
        Col_1_y = 230.0
        Col_1_z = 230.0
        Col_1_Cover = 23.0

        Col_2_y = 230.0
        Col_2_z = 230.0
        Col_2_Cover = 23.0

    # --------------------------------------------------------------
    # Materials
    # --------------------------------------------------------------

    gamma_conc = 2.5e-5       # N/mm^3 (for γ = 25 kN/m^3)
    g = 9.81e3                # mm/s^2

    unconfined_concrete_tag = 1     # unconfined concrete for cover
    confined_concrete_tag = 2       # confined concrete for core
    steel_tag = 3                   # reinforcement

    # nominal concrete compressive strength
    fc = -fc_concrete_data[u]              # CONCRETE Compressive Strength (+Tension, -Compression)
    Ec = 5000 * (-fc)**0.5  # Concrete Elastic Modulus (the term in sqr root in Mpa)
    Kfc = 1.3			    # ratio of confined to unconfined concrete strength
    Kres = 0.1			    # ratio of residual/ultimate to maximum stress
    lambda_u = 0.1          # ratio between unloading slope at $eps2 and initial slope $Ec

    # unconfined concrete (U) : compressive stress-strain properties
    fc1U = fc               # (todeschini parabolic model), maximum compressive stress
    eps1U = -0.002          # strain at maximum compressive stress
    fc2U = Kres * fc1U      # ultimate compressive stress
    eps2U = -0.02           # strain at ultimate compressive stress

    # confined concrete (C) : compressive stress-strain properties
    fc1C = Kfc * fc1U           # (mander model), maximum compressive stress
    eps1C = 1.7 * fc1C / Ec     # strain at maximum compressive stress
    fc2C = Kres * fc1C          # ultimate compressive stress
    eps2C = 20 * eps1C          # strain at ultimate compressive stress

    # tensile stress-strain properties
    ftC = -0.1 * fc1C  # tensile strength +tension
    ftU = -0.1 * fc1U  # tensile strength +tension
    Ets = ftU / 0.002   # tension softening stiffness

    # STEEL parameters for Steel02
    Fy_steel = fy_steel_data[u]    # Yield stress (MPa)
    E0_steel = 2.0e5    # Initial modulus (MPa)
    Bs = 0.01           # strain-hardening ratio
    params_steel = [20,0.925,0.15]             # control the transition from elastic to plastic branches

    # uniaxial materials
    def materials_function():
        ops.uniaxialMaterial("Concrete02", unconfined_concrete_tag, fc1U, eps1U, fc2U, eps2U, lambda_u, ftU, Ets) # unconfined concrete for cover
        ops.uniaxialMaterial("Concrete02", confined_concrete_tag, fc1C, eps1C, fc2C, eps2C, lambda_u, ftC, Ets) # confined concrete for core
        ops.uniaxialMaterial("Steel02", steel_tag, Fy_steel, E0_steel, Bs, *params_steel) 
    
    materials_function()

    # --------------------------------------------------------------------------------------------------------

    hys_Mat_tag_Y = 5

    def calculate_strut_width(hys_Mat_tag, dim_perp, dim_along, bayWidth_along):
        h_col = bay_width_Z - Beam_1_y
        h_inf = bay_width_Z - Beam_1_y
        E_fe = Ec
        E_me = 2300.0 # Mpa Modulus of elasticity of masonary
        I_col = dim_perp * (dim_along ** 3) / 12
        L_inf = bayWidth_along - dim_along
        t_inf = 100.0 # mm thickness of masonary wall

        r_inf = np.sqrt(h_inf**2 + L_inf**2)     # diagonal length of infill panel
        theta = np.atan(h_inf / L_inf)           # angle θ whose tangent is the height-to-length aspect ratio
        lambda_1 = ((E_me * t_inf * np.sin(2 * theta)) / (4 * E_fe * I_col * h_inf))**(1/4)
        bm = 0.175 * (lambda_1 * h_col)**(-0.4) * r_inf   # width of the equivalent strut
        
        Em = 2300.0    # MPa
        Gm = 1.171e3   # MPa 
        fms = 0.575    # MPa

        tm = t_inf
        lm = L_inf
        hm = h_inf
        dm = r_inf

        R1 = Gm * tm * lm / hm
        R2 = Em * tm * bm / dm
        R3 = 0.1 * R1

        Fy = fms * tm * lm 
        Fm = 1.3 * Fy
        Fr = 0.1 * Fm

        del_y = Fy / R1
        del_m = del_y + (Fm - Fy) / R2
        del_u = del_m + (Fm - Fr) / R3
        
        strut_area = t_inf * bm
        strut_length = ((bayWidth_along ** 2) + (bay_width_Z ** 2)) ** (1/2)

        cFy, cFu, cFr = -Fy / strut_area, -Fm / strut_area, - Fr / strut_area
        cdeltay, cdeltau, cdeltar = -del_y / strut_length, -del_m / strut_length, -del_u / strut_length
        tFy, tFu, tFr = -0.01 * cFy, -0.01 * cFu, -0.01 * cFr
        tdeltay, tdeltau, tdeltar = -0.01 * cdeltay, -0.01 * cdeltau, -0.01 * cdeltar

        pinchx, pinchy, beta = 0.9, 0.1, 0.1

        ops.uniaxialMaterial("Hysteretic", hys_Mat_tag, *[tFy, tdeltay], *[tFu, tdeltau], *[tFr, tdeltar], *[cFy, cdeltay], *[cFu, cdeltau], *[cFr, cdeltar], pinchx, pinchy, 0.0, 0.0, beta)
        
        return tdeltar, cdeltar, strut_area
    
    tdeltarY, cdeltarY, strut_areaY = calculate_strut_width(hys_Mat_tag_Y, Col_1_z, Col_1_y, bay_width_Y)      

    # --------------------------------------------------------------
    # Model
    # --------------------------------------------------------------

    NplaneX = NBayX + 1
    NplaneY = NBayY + 1
    NplaneZ = NBayZ + 1

    # Nodes --------------------------------------------------------------
    # structure nodes
    support_nodes = [] 
    nodes_forIDR = []
    for i in range(NplaneX):
        planeX = i + 1
        x = i * bay_width_X
        for j in range(NplaneY):
            planeY = j + 1
            y = j * bay_width_Y
            for k in range(NplaneZ):
                planeZ = k + 1
                z = k * bay_width_Z
                nodeTag = planeX * 100 + planeY * 10 + planeZ
                ops.node(nodeTag, x, y, z)
                if planeZ == 1:
                    support_nodes.append(nodeTag)
                    ops.fix(nodeTag, 1, 1, 1, 1, 1, 1)
                if planeX == 1 and planeY == 1:
                    nodes_forIDR.append(nodeTag)

    if rigidDiaphragm == 1:
        print("Rigid Diaphragm ON....")
        ops.constraints('Transformation')
        midX = NBayX * bay_width_X / 2     # mid-span X coordinate for rigid diaphragm
        midY = NBayY * bay_width_Y / 2     # mid-span Y coordinate for rigid diaphragm
        perp_direction = 3                 # perpendicular to plane of rigid diaphragm

        master_nodes = []
        for k in range(1, NplaneZ):
            planeZ = k + 1
            z = k * bay_width_Z

            master_nodeTag = planeZ + 9990
            ops.node(master_nodeTag, midX, midY, z)
            master_nodes.append(master_nodeTag)

            # Collecting Slave Nodes  
            slaveNodeTags = []
            for i in range(NplaneX):
                planeX = i + 1
                for j in range(NplaneY):
                    planeY = j + 1
                    slave_nodeTag = planeX * 100 + planeY * 10 + planeZ
                    slaveNodeTags.append(slave_nodeTag)
            ops.rigidDiaphragm(perp_direction, master_nodeTag, *slaveNodeTags)
            ops.fix(master_nodeTag, 0, 0, 1, 1, 1, 0)
            # print(master_nodeTag, *slaveNodeTags)
    else:
        print("Rigid Diaphragm OFF....")
        ops.constraints('Plain')

    # Sections, 1 cover, 2 core, 3 steel --------------------------------------------------------------

    # Section tags
    Beam_1_SecTag_Fiber = 11
    Col_1_SecTag_Fiber = 12
    Col_2_SecTag_Fiber = 13

    def Section_Builder ():

        def area(diameter):
            return (np.pi * diameter ** 2) / 4.0

        # Beam Type 1
        Beam_1_sec_name = 'Beam Type 1 Section'
        nBT_Beam_1 = 3       # no. of longitudinal-reinforcement bars on top layer || to local z axis
        nBM_Beam_1 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
        nBI_Beam_1 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
        nBB_Beam_1 = 3       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
        aBT_Beam_1 = area(16.0)         # area of top layer bars || to local z axis
        aBM_Beam_1 = area(16.0)         # area of mid layer bars || to local z axis
        aBI_Beam_1 = area(16.0)         # area of mid layer bars || to local y axis
        aBB_Beam_1 = area(16.0)         # area of bottom layer bars || to local z axis
        nfCore_y_Beam_1 = 6      # number of fibers in the core patch in local y axis
        nfCore_z_Beam_1 = 6      # number of fibers in the core patch in local z axis
        nfCover_y_Beam_1 = 6     # number of fibers in the cover patches with long sides || to local y axis
        nfCover_z_Beam_1 = 6     # number of fibers in the cover patches with long sides || to local z axis

        # Column Type 1
        Col_1_sec_name = 'Col Type 1 Section'
        nBT_Col_1 = 2       # no. of longitudinal-reinforcement bars on top layer || to local z axis
        nBM_Col_1 = 2       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
        nBI_Col_1 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
        nBB_Col_1 = 2       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
        aBT_Col_1 = area(16.0)         # area of top layer bars || to local z axis
        aBM_Col_1 = area(12.0)         # area of mid layer bars || to local z axis
        aBI_Col_1 = area(12.0)         # area of mid layer bars || to local y axis
        aBB_Col_1 = area(16.0)         # area of bottom layer bars || to local z axis
        nfCore_y_Col_1 = 6      # number of fibers in the core patch in local y axis
        nfCore_z_Col_1 = 6      # number of fibers in the core patch in local z axis
        nfCover_y_Col_1 = 6     # number of fibers in the cover patches with long sides || to local y axis
        nfCover_z_Col_1 = 6     # number of fibers in the cover patches with long sides || to local z axis

        # Column Type 2
        Col_2_sec_name = 'Col Type 2 Section'
        nBT_Col_2 = 2       # no. of longitudinal-reinforcement bars on top layer || to local z axis
        nBM_Col_2 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
        nBI_Col_2 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
        nBB_Col_2 = 2       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
        aBT_Col_2 = area(12.0)         # area of top layer bars || to local z axis
        aBM_Col_2 = area(12.0)         # area of mid layer bars || to local z axis
        aBI_Col_2 = area(12.0)         # area of mid layer bars || to local y axis
        aBB_Col_2 = area(12.0)         # area of bottom layer bars || to local z axis
        nfCore_y_Col_2 = 6      # number of fibers in the core patch in local y axis
        nfCore_z_Col_2 = 6      # number of fibers in the core patch in local z axis
        nfCover_y_Col_2 = 6     # number of fibers in the cover patches with long sides || to local y axis
        nfCover_z_Col_2 = 6     # number of fibers in the cover patches with long sides || to local z axis

        Section (Beam_1_SecTag_Fiber, Beam_1_sec_name,
                Beam_1_y, Beam_1_z, Beam_1_Cover, 
                nfCore_y_Beam_1, nfCore_z_Beam_1, 
                nfCover_y_Beam_1, nfCover_z_Beam_1, 
                nBT_Beam_1, nBM_Beam_1, nBI_Beam_1, nBB_Beam_1,
                aBT_Beam_1, aBM_Beam_1, aBI_Beam_1, aBB_Beam_1, 
                confined_concrete_tag, unconfined_concrete_tag, steel_tag)
        
        Section (Col_1_SecTag_Fiber, Col_1_sec_name,
                Col_1_y, Col_1_z, Col_1_Cover, 
                nfCore_y_Col_1, nfCore_z_Col_1, 
                nfCover_y_Col_1, nfCover_z_Col_1, 
                nBT_Col_1, nBM_Col_1, nBI_Col_1, nBB_Col_1,
                aBT_Col_1, aBM_Col_1, aBI_Col_1, aBB_Col_1, 
                confined_concrete_tag, unconfined_concrete_tag, steel_tag)
        
        Section (Col_2_SecTag_Fiber, Col_2_sec_name,
                Col_2_y, Col_2_z, Col_2_Cover, 
                nfCore_y_Col_2, nfCore_z_Col_2, 
                nfCover_y_Col_2, nfCover_z_Col_2, 
                nBT_Col_2, nBM_Col_2, nBI_Col_2, nBB_Col_2,
                aBT_Col_2, aBM_Col_2, aBI_Col_2, aBB_Col_2, 
                confined_concrete_tag, unconfined_concrete_tag, steel_tag)

    Section_Builder()

    # Elements --------------------------------------------------------------

    # Geometry transformations -----------------------
    Beam_X_TransfTag = 1
    Beam_Y_TransfTag = 2
    Col_TransfTag = 3

    #geomTransf(transfType, transfTag, *transfArgs)
    ops.geomTransf('Linear', Beam_X_TransfTag, 0, -1, 0)  
    ops.geomTransf('Linear', Beam_Y_TransfTag, 1, 0, 0)   
    ops.geomTransf('PDelta', Col_TransfTag, -1, 0, 0)   

    #  Integration setup -----------------------------
    Beam_1_IntTag = 1
    Col_1_IntTag = 2
    Col_2_IntTag = 3

    numIntPts_Beam = 3
    numIntPts_Col = 5

    ops.beamIntegration('Lobatto', Beam_1_IntTag, Beam_1_SecTag_Fiber, numIntPts_Beam)
    ops.beamIntegration('Lobatto', Col_1_IntTag, Col_1_SecTag_Fiber, numIntPts_Col)
    ops.beamIntegration('Lobatto', Col_2_IntTag, Col_2_SecTag_Fiber, numIntPts_Col)

    #  Elements setup -----------------------------

    Beam_1_mpul = Beam_1_y * Beam_1_z * gamma_conc / g
    Col_1_mpul = Col_1_y * Col_1_z * gamma_conc / g
    Col_2_mpul = Col_2_y * Col_2_z * gamma_conc / g

    # X_Beam elements 
    X_Beam_Tags = []
    for k in range(1, NplaneZ):
        startZ =  k + 1
        endZ = k + 1
        planeZ = k + 1
        for j in range(NplaneY):
            startY = j + 1
            endY = j + 1
            for i in range(NplaneX - 1):
                startX = i + 1
                endX = startX + 1
                XBeamTag = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + startZ * 10 + endZ
                startNode = startX * 100 + startY * 10 + startZ
                endNode = endX * 100 + endY * 10 + endZ

                ops.element('forceBeamColumn', XBeamTag, startNode, endNode, Beam_X_TransfTag, Beam_1_IntTag, '-mass', Beam_1_mpul)
                X_Beam_Tags.append(XBeamTag)

    # Y_Beam elements 
    Y_Beam_Tags = []
    for k in range(1, NplaneZ):
        startZ =  k + 1
        endZ = k + 1
        planeZ = k + 1
        for i in range(NplaneX):
            startX = i + 1
            endX = i + 1
            for j in range(NplaneY - 1):
                startY = j + 1
                endY = startY + 1
                YBeamTag = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + startZ * 10 + endZ
                startNode = startX * 100 + startY * 10 + startZ
                endNode = endX * 100 + endY * 10 + endZ

                ops.element('forceBeamColumn', YBeamTag, startNode, endNode, Beam_Y_TransfTag, Beam_1_IntTag, '-mass', Beam_1_mpul)
                Y_Beam_Tags.append(YBeamTag)

    Beam_Tags = X_Beam_Tags + Y_Beam_Tags

    # Column elements
    ground_floor_col_tags = []
    columns_by_floor = [[] for _ in range(NBayZ)]        # One list per floor
    Column_1_Tags = []
    Column_2_Tags = []

    for i in range(NplaneX):
        startX = i + 1
        endX = i + 1
        for j in range(NplaneY):
            startY = j + 1
            endY = j + 1
            for k in range(NplaneZ - 1):
                startZ = k + 1
                endZ = startZ + 1
                planeZ = k + 1
                ColTag = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + startZ * 10 + endZ
                startNode = startX * 100 + startY * 10 + startZ
                endNode = endX * 100 + endY * 10 + endZ
                columns_by_floor[k].append(ColTag)

                if planeZ == 1:
                    ground_floor_col_tags.append(ColTag)
                if planeZ == 1 or planeZ == 2:
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_1_IntTag, 'mass', Col_1_mpul)
                    Column_1_Tags.append(ColTag)
                else:
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_2_IntTag, 'mass', Col_2_mpul)
                    Column_2_Tags.append(ColTag)

    Column_Tags = Column_1_Tags + Column_2_Tags

    Element_Tags = Beam_Tags + Column_Tags

    def infill_along_Y():
        for i in range(NplaneX):
            startX = i + 1
            endX = i + 1

            if startX not in (1, NplaneX):
                startZ = 1
                endZ = startZ + 1
                for j in range(NplaneY - 1):
                    startY = j + 1
                    endY = startY + 1

                    startNode1 = startX * 100 + startY * 10 + startZ
                    endNode1 = endX * 100 + endY * 10 + endZ
                    strutTag1 = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + startZ * 10 + endZ

                    startNode2 = startX * 100 + startY * 10 + endZ
                    endNode2 = endX * 100 + endY * 10 + startZ
                    strutTag2 = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + endZ * 10 + startZ

                    ops.element('Truss', strutTag1, *[startNode1, endNode1], strut_areaY, hys_Mat_tag_Y)
                    ops.element('Truss', strutTag2, *[startNode2, endNode2], strut_areaY, hys_Mat_tag_Y)

            # if startX in (1, NplaneX):
            for k in range(1, NplaneZ - 1):
                startZ = k + 1
                endZ = startZ + 1
                for j in range(NplaneY - 1):
                    startY = j + 1
                    endY = startY + 1

                    startNode1 = startX * 100 + startY * 10 + startZ
                    endNode1 = endX * 100 + endY * 10 + endZ
                    strutTag1 = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + startZ * 10 + endZ

                    startNode2 = startX * 100 + startY * 10 + endZ
                    endNode2 = endX * 100 + endY * 10 + startZ
                    strutTag2 = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + endZ * 10 + startZ

                    ops.element('Truss', strutTag1, *[startNode1, endNode1], strut_areaY, hys_Mat_tag_Y)
                    ops.element('Truss', strutTag2, *[startNode2, endNode2], strut_areaY, hys_Mat_tag_Y)

    if infillIncusion == 0:
        print('NO infills applied...')
    elif infillIncusion == 2:
        print('Infills applied along Y Direction...')
        infill_along_Y()  # if time history is done in Y direction
    else:
        print('ERROR infill Direction...')

    # Gravity loads --------------------------------------------------------------

    Q_slab = gamma_conc * slab_thickness       # Self weight of Slab N per mm2
    Q_floor_finish = 1.0e-3                    # Floor finish load N per mm2  
    LL = 1.0e-3                                # Live load for all floors N per mm2

    TL = Q_slab + Q_floor_finish + LL          # Total load for all floors N per mm2

    if bay_width_Y > bay_width_X:
        if bay_width_Y/bay_width_X <= 2.0 :
            P1 = TL * (bay_width_X / 2) * (bay_width_Y - bay_width_X / 2) # N
            P2 = TL * (1/4) * (bay_width_X ** 2)                          # N
        else :
            P1 = TL * (bay_width_X * bay_width_Y) / 2
            P2 = 0
    else:
        if bay_width_X/bay_width_Y <= 2.0 :
            P2 = TL * (bay_width_Y / 2) * (bay_width_X - bay_width_Y / 2) # N
            P1 = TL * (1/4) * (bay_width_Y ** 2)                          # N
        else :
            P2 = TL * (bay_width_X * bay_width_Y) / 2
            P1 = 0

    # ---------------------------------
    O_YBeam = P1 / g        # External Load on Outside Y Beam in mass terms : N s2 / mm
    I_YBeam = 2 * P1 / g    # External Load on Inside Y Beam in mass terms : N s2 / mm

    O_XBeam = P2 / g        # External Load on Outside X Beam in mass terms : N s2 / mm
    I_XBeam = 2 * P2 / g    # External Load on Inside X Beam in mass terms : N s2 / mm

    Col = 0                 # External Load on Column in mass terms : N s2 / mm

    # Nodal Mass Distribution ----------------------------------------------------------------
    for i in range(NplaneX):
        planeX = i + 1
        for j in range(NplaneY):
            planeY = j + 1
            for k in range(1, NplaneZ):
                planeZ = k + 1
                nodeTag = planeX * 100 + planeY * 10 + planeZ
                if planeX in (1, NplaneX) and planeY in (1, NplaneY):
                    if planeZ == NplaneZ:
                        mass = (Col + O_XBeam + O_YBeam) / 2
                    else:
                        mass = Col + (O_XBeam + O_YBeam) / 2
                elif planeX in (1, NplaneX) and planeY not in (1, NplaneY):
                    if planeZ == NplaneZ:
                        mass = (Col + I_XBeam) / 2 + O_YBeam
                    else:
                        mass = Col + I_XBeam / 2 + O_YBeam
                elif planeX not in (1, NplaneX) and planeY in (1, NplaneY):
                    if planeZ == NplaneZ:
                        mass = (Col + I_YBeam) / 2 + O_XBeam
                    else:
                        mass = Col + O_XBeam + I_YBeam / 2
                else:
                # if planeX not in (1, NplaneX) and planeY not in (1, NplaneY):
                    if planeZ == NplaneZ:
                        mass = Col / 2 + I_XBeam + I_YBeam
                    else:
                        mass = Col + I_XBeam + I_YBeam
                ops.mass(nodeTag, mass, mass, 0.0, 0.0, 0.0, 0.0)

    # Eigenvalue Analysis --------------------------------------------------------------
    numModes = 5
    lambdas = ops.eigen(numModes)  # returns a list of eigenvalues

    omega = []
    frequencies = []
    periods = []

    for lam in lambdas:
        sqrt_lam = lam ** 0.5
        omega.append(sqrt_lam)
        frequencies.append(sqrt_lam / (2 * np.pi))
        periods.append((2 * np.pi) / sqrt_lam)

    print("Time Periods before application of UDL are:", [f"{p:.10f}" for p in periods])
    print("-------------------------------")

    # Application Of UDL in local coordinate axes --------------------------------------------------------------
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)

    P11 = P1 / bay_width_Y  # External Load on beams in Y Direction in N / mm
    P12 = P2 / bay_width_X  # External Load on beams in X Direction in N / mm
    P3 = gamma_conc * Beam_1_y * Beam_1_z      # Total Self weight of Beam 1 N / mm
    P5 = gamma_conc * Col_1_y * Col_1_z        # Total Self weight of Column 1 N / mm
    P6 = gamma_conc * Col_2_y * Col_2_z        # Total Self weight of Column 2 N / mm

    # print(P1, P2, P11, P12, P3, P4, P5, P6)

    def UDL_applier():
        # Beam 1 loading
        for tag in X_Beam_Tags:
            tag_str = str(tag).zfill(6)  # ensures it's 6 digits with leading zeros if needed
            starty = int(tag_str[2])
            if starty in (1, NplaneY):
                UDL = P12 + P3
            else:
                UDL = 2 * P12 + P3
            ops.eleLoad('-ele', tag, '-type', '-beamUniform', -UDL, 0.0, 0.0)

        for tag in Y_Beam_Tags:
            tag_str = str(tag).zfill(6)  # ensures it's 6 digits with leading zeros if needed
            startx = int(tag_str[0])
            if startx in (1, NplaneX):
                UDL = P11 + P3
            else:
                UDL = 2 * P11 + P3
            ops.eleLoad('-ele', tag, '-type', '-beamUniform', -UDL, 0.0, 0.0)

        for tag in Column_1_Tags:
            UDL = P5
            ops.eleLoad('-ele', tag, '-type', '-beamUniform', 0.0, 0.0, -UDL)

        for tag in Column_2_Tags:
            UDL = P6
            ops.eleLoad('-ele', tag, '-type', '-beamUniform', 0.0, 0.0, -UDL)

    UDL_applier()  # Call this function to apply the loads as UDL

    # Plotting the model --------------------------------------------------------------
    def Plotter():
        opsv.plot_model(node_labels = 1, element_labels = 0)     # 1 to see, 0 to hide
        plt.title("3D Model")

        opsv.plot_load(nep=10, sfac= 500, node_supports=True)
        plt.title("UDL applied")

        # Format all text labels to 2 decimal places
        for text in plt.gca().texts:
            try:
                value = float(text.get_text())
                text.set_text(f"{value:.2f}")
            except ValueError:
                pass  # Skip if not a number

        plt.show()

    # Plotter()

    # --------------------------------------------------------------
    # Gravity Analysis
    # --------------------------------------------------------------
    if rigidDiaphragm == 1:
        ops.constraints('Transformation')
    else:
        ops.constraints('Plain')

    ops.numberer('RCM')
    ops.system('BandGen')
    ops.test('NormDispIncr', 1e-8, 10)
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 0.001)
    ops.analysis('Static')

    ops.analyze(1)

    ops.loadConst('-time', 0.0)  # Set the time to zero an hold the loads constant

    # Plotting Mode Shapes and Deformed Shape 
    def ModeShapesPlot():
        opsv.plot_defo()
        plt.title("Deformed Shape")

        opsv.plot_mode_shape(1)
        plt.title("Mode 1")

        opsv.plot_mode_shape(2)
        plt.title("Mode 2")

        opsv.plot_mode_shape(3)
        plt.title("Mode 3")

        opsv.plot_mode_shape(4)
        plt.title("Mode 4")

        opsv.plot_mode_shape(5)
        plt.title("Mode 5")

        plt.show()

    # ModeShapesPlot()

    # --------------------------------------------------------------
    # Time history analysis
    # --------------------------------------------------------------
    print("Gravity Analysis Done.")

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

    if direction == 1:
        print("Time History Analysis in X Direction...")
    elif direction == 2:
        print("Time History Analysis in Y Direction...")
    else:
        print("ERROR Direction")

    # Recorders for Column Sections || Change to Elements for final version --------------------------------------------------------------

    for tag in Column_Tags:             # Change to Element_Tags for final version
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

    # Setup For Time History Analysis --------------------------------------------------------------

    # RAYLEIGH damping parameters (D = αM*M + βKcurr*Kcurrent + βKcomm*KlastCommit + βKinit*Kinitial)
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

    # Eigenvalue analysis before earthquake -----------------------------------------------------
    Initial_TimePeriods = EigenValues(5)
    print("Initial Time Periods : ", [f"{p:.10f}" for p in Initial_TimePeriods])
    output_array.extend(Initial_TimePeriods)

    # Transient Analysis -----------------------------------------------------
    tFinal = nPts * dt
    tCurrent = ops.getTime()
    ok = 0

    control_node = 9990 + NplaneZ     # node where displacement is read
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

    # Eigenvalue analysis after earthquake -----------------------------------------------------
    Final_TimePeriods = EigenValues(5)
    print("Final Time Periods : ", [f"{p:.10f}" for p in Final_TimePeriods])
    output_array.extend(Final_TimePeriods)

    # Maximum Induced Base Shear -----------------------------------------------------
    max_base_shear = max(np.abs(baseshear))
    print(f"Maximum Induced Base Shear = {max_base_shear:.4f} kN")
    output_array.append(max_base_shear)

    max_control_node_disp = max(np.abs(control_node_disp))
    print(f"Maximum Induced Control Node Displacement = {max_control_node_disp:.4f} mm")

    MIDRs = [max(drifts) for drifts in drifts_all_floors]
    max_index_MIDR = MIDRs.index(max(MIDRs))
    MIDR_1st_floor = MIDRs[0]
    MIDR_2nd_floor = MIDRs[1]
    MIDRall = max(MIDRs)
    output_array.append(MIDR_1st_floor)
    output_array.append(MIDR_2nd_floor)
    output_array.append(MIDRall)

    for i in range(NBayZ):
        print(f'MIDR for Floor {i+1} = {MIDRs[i] * 100:.4f} %')
    
    print("-------------------------------")
    # -----------------------------------------------------
    # Time History Output Analysis
    # -----------------------------------------------------

    ops.wipe()
    ops.model('BasicBuilder', '-ndm', 3, '-ndf', 6)

    materials_function()
    Section_Builder()

    direction = 2  # 1, 2 in X and Y Direction respectively

    mu = 15.0           # Target ductility for analysis
    numIncr = 100       # Number of analysis increment
    P = -1000.0         # Set reference axial load 

    if direction == 1:
        phiy, phiu, yieldM, ultM = MomentCurvature3D(Col_1_SecTag_Fiber, P, Col_1_y, Col_1_Cover, mu, numIncr, 'y', Fy_steel, E0_steel)
    elif direction == 2:
        phiy, phiu, yieldM, ultM = MomentCurvature3D(Col_1_SecTag_Fiber, P, Col_1_z, Col_1_Cover, mu, numIncr, 'z', Fy_steel, E0_steel)
    else:
        print("ERROR Direction.")

    if direction == 1:
        input_dir = f"/Users/niraj/Documents/openseespy/Groups/CCP/Output/sample_{sample_no}/Earthquake_{CarlSagan}/outputx"
    elif direction == 2:
        input_dir = f"/Users/niraj/Documents/openseespy/Groups/CCP/Output/sample_{sample_no}/Earthquake_{CarlSagan}/outputy"

    beta = 0.1
    Et = []
    Sum_Et = 0.0
    DI_Storey = []

    for floor in range(NBayZ):
        print(f'Analyzing Damage in Storey {floor + 1}')
        DI_Local = []
        for tag in columns_by_floor[floor]:          
            file_curv = [f"{input_dir}/ele{tag}_sec1_curv.out", f"{input_dir}/ele{tag}_sec2_curv.out", f"{input_dir}/ele{tag}_sec3_curv.out", f"{input_dir}/ele{tag}_sec4_curv.out", f"{input_dir}/ele{tag}_sec5_curv.out"]

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

            if phim >= phiy and phiu > phiy:
                Et.append(total_ET)
                Sum_Et += total_ET

                DI_l = ((phim - phiy) / (phiu - phiy)) + ((beta * total_ET) / (yieldM * phiu))
                DI_Local.append(DI_l)
                print(f"DI_Local of element {tag} = {DI_l * 100:.7f} %")
            else:
                print(f"DI_Local of element {tag} = {0 : .7f} %")

        if len(DI_Local) > 0:
            DI_floor = sum(d * e for d, e in zip(DI_Local, Et)) / Sum_Et
            print(f"DI for Storey {floor + 1} for Ground Motion {CarlSagan} = {DI_floor * 100:.7f} %")
        else:
            DI_floor = 0.
            print(f"Max induced curvature < Yield Curvature, so no damage for Storey {floor + 1}")
        DI_Storey.append(DI_floor)
        print("-------------------------------")

    DI_Global = max(DI_Storey)
    if DI_Global >= 1.0:
        DI_Global = 1.0
    print(f"Global Damage Index for Ground Motion {CarlSagan} = {DI_Global * 100:.7f} %")
    output_array.append(DI_Global)

    append_results(output_array)

if __name__ == "__main__":
    # Example: run all combinations of u and CarlSagan in parallel
    us = [128]  # or list(range(len(sample_no_data))) for all samples
    CarlSagans = [1,2,18]  # or list(range(len(GM_no_data))) for all ground motions

    tasks = [(u, CarlSagan) for u in us for CarlSagan in CarlSagans]

    with mp.Pool(processes=mp.cpu_count()) as pool:
        pool.starmap(run_analysis, tasks)