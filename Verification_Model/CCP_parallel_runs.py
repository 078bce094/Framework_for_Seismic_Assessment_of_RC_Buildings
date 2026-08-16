import numpy as np
import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt
import csv

# -------------------------------------------------------------
# inputs
# -------------------------------------------------------------

samples_data_file = r'D:\Niraj\Verification_Model\CCP_samples.csv'
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

IM_data_file = r'D:\Niraj\Verification_Model\IM_Parameters_Matched.csv'
IM_data = np.genfromtxt(IM_data_file, delimiter=',', skip_header=1)

GM_no_data = IM_data[:,0]    # RSN
GM_PGA_data = IM_data[:,3]   # PGA

# -------------------------------------------------------------
# outputs
# -------------------------------------------------------------

output_csv_file = r'D:\Niraj\Verification_Model\CCP_results.csv'

# Output data column titles
headers = [ 'RSN', 'PGA (g)', 'MIDR (%)']

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

# initialize_csv()

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

# ---------------------------------------------------------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------------------------------------------------------
def run_analysis(u, pga, CarlSagan):
    print('-------------------------------------------------------')

    output_array = []

    RSN = int(GM_no_data[CarlSagan])
    output_array.append(RSN)
    output_array.append(pga)

    original_pga = GM_PGA_data[CarlSagan]
    factor = (pga * 9810) / original_pga

    print(f"Analyzing sample no : {int(sample_no_data[u])}, GM : {RSN}, PGA : {pga}")

    direction = 2    # 1, 2 in X and Y Direction respectively

    # Read Earthquake Data --------------------------------------------------------------
    GM_input_file = rf'D:\Niraj\GM\All\RSN_{RSN}.txt'
    
    # Initialize list for load_factors
    load_factors = []

    # Read and parse the file
    with open(GM_input_file, "r") as f:
        lines = f.readlines()

    # Extract time step from the line containing "Time Step"
    for line in lines:
        if "Time Step" in line:
            dt = float(line.strip().split(":")[1].split()[0])
            break

    # Skip lines until you reach the actual data
    data_start_index = next(i for i, line in enumerate(lines) if "Time(sec)" in line) + 1

    # Read acceleration values
    for line in lines[data_start_index:]:
        if line.strip():  # skip empty lines
            parts = line.strip().split()
            if len(parts) >= 2:
                acc = float(parts[1])
                load_factors.append(acc)

    # Final time
    tFinal = dt * len(load_factors)
    # print(f"RSN: {RSN}, dt: {dt}, tFinal: {tFinal:.7f}, nPts: {len(load_factors)}")


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
    Kfc = 1.20			    # ratio of confined to unconfined concrete strength
    Kres = 0.1			    # ratio of residual/ultimate to maximum stress
    lambda_u = 0.1          # ratio between unloading slope at $eps2 and initial slope $Ec

    # unconfined concrete (U) : compressive stress-strain properties
    fc1U = fc               # (todeschini parabolic model), maximum compressive stress
    eps1U = -0.002          # strain at maximum compressive stress
    fc2U = Kres * fc1U      # ultimate compressive stress
    eps2U = -0.02           # strain at ultimate compressive stress

    # confined concrete (C) : compressive stress-strain properties
    fc1C = Kfc * fc1U           # (mander model), maximum compressive stress
    eps1C  = max(eps1U * (1 + 5 * (Kfc - 1)), -0.006)    # strain at maximum compressive stress
    # eps1C = min(eps1U * (1 + 5 * (Kfc - 1)), 0.006)     # strain at maximum compressive stress
    fc2C = Kres * fc1C          # ultimate compressive stress
    eps2C = 10 * eps1C          # strain at ultimate compressive stress

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
        # print("Rigid Diaphragm ON....")
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
        # print("Rigid Diaphragm OFF....")
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
    # ops.geomTransf('Linear', Col_TransfTag, -1, 0, 0)   

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
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_1_IntTag, '-mass', Col_1_mpul)
                    Column_1_Tags.append(ColTag)
                else:
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_2_IntTag, '-mass', Col_2_mpul)
                    Column_2_Tags.append(ColTag)

    Column_Tags = Column_1_Tags + Column_2_Tags

    Element_Tags = Beam_Tags + Column_Tags

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

    if int(CarlSagan) == 0 and pga == 0.1:
        print(periods)

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
    ops.test('NormDispIncr', 1e-5, 1000)
    # ops.test('EnergyIncr', 5.0e-4,  100 )
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 1.0)
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

    # --------------------------------------------------------------
    # Analysis by floor
    # --------------------------------------------------------------

    # ops.wipeAnalysis()

    ops.rayleigh(alphaM, betaKcurr, betaKinit, betaKcomm)       # apply Rayleigh damping

    ops.timeSeries('Path', 200, '-dt', dt, '-values', *load_factors, '-factor', factor)   # tag = 200
    ops.pattern('UniformExcitation',  200,   direction,  '-accel', 200)

    ops.constraints('Transformation')
    ops.test('NormDispIncr', 1.0e-6, 50)
    # ops.test('EnergyIncr', 5.0e-4,  50 )
    ops.algorithm('Newton')
    ops.numberer('RCM')
    ops.system('BandGen')
    ops.integrator('Newmark',  0.5,  0.25 )
    ops.analysis('Transient')

    # Transient Analysis -----------------------------------------------------
    # tFinal = nPts * dt
    tCurrent = ops.getTime()
    ok = 0

    time = []
    baseshear = []
    drifts_all_floors = [[] for _ in range(NBayZ)]        # One list per floor

    while ok == 0 and tCurrent < tFinal: 
        ok = ops.analyze(1, 0.001)

        if ok != 0:
            print("regular newton failed ... trying ModifiedNewton...")
            ops.test('NormDispIncr', 5.0e-4,  100, 0)
            ops.algorithm('ModifiedNewton')
            ok = ops.analyze( 1, 0.0005)
            if ok == 0:
                # print("ModifiedNewton worked .. back to regular newton")
                ops.test('EnergyIncr', 5.0e-4,  50 )
                ops.algorithm('Newton')
            else:
                # print("ModifiedNewton failed ... trying Broyden...")
                ops.algorithm('Broyden')
                ok = ops.analyze( 1, .0001)
            if ok == 0:
                # print("Broyden worked .. back to regular newton")
                ops.algorithm('Newton')
            else:
                # print("Broyden failed ... trying NewtonLineSearch...")
                ops.algorithm('NewtonLineSearch')
                ok = ops.analyze( 1, .0001)
            if ok == 0:
                # print("NewtonLineSearch worked .. back to regular newton")
                ops.algorithm('Newton')
            else:
                # print("NewtonLineSearch failed ... trying KrylovNewton...")
                ops.algorithm('KrylovNewton')
                ok = ops.analyze( 1, .0001)
            if ok == 0:
                # print("KrylovNewton worked .. back to regular newton")
                ops.algorithm('Newton')
            # else:
            #     print('Analysis Not Successful..')

        tCurrent = ops.getTime()
        time.append(tCurrent)
        ops.reactions()
        basereac = sum(ops.nodeReaction(n, direction) for n in support_nodes)
        baseshear.append(basereac / 1000)

        for temp_floor in range(NBayZ):
            base_node = nodes_forIDR[temp_floor]   
            top_node = nodes_forIDR[temp_floor + 1]    

            base_disp = ops.nodeDisp(base_node, direction)
            top_disp = ops.nodeDisp(top_node, direction)

            drift = abs(top_disp - base_disp) / bay_width_Z
            drifts_all_floors[temp_floor].append(drift)

    MIDRs = [max(drifts) for drifts in drifts_all_floors]

    MIDRall = max(MIDRs)

    current_MIDR = MIDRall * 100

    output_array.append(round((MIDRall * 100),3))

    ops.loadConst('-time', 0.0)
    ops.remove('recorders') 

    append_results(output_array)

    return current_MIDR


# ---------------------------------------------------------------------------------------------------------------------------
# Control Center
# ---------------------------------------------------------------------------------------------------------------------------

sample_number = 244
PGA_factors = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]

complete_samples_data = r'D:\Niraj\Verification_Model\CCP_results.csv'
completed_data = np.genfromtxt(complete_samples_data, delimiter=',', skip_header=1)

completed_pairs = set(
    zip(
        completed_data[:, 0].astype(int),
        completed_data[:, 1]
    )
)

for CarlSagan in range(len(GM_no_data)):

    current_RSN = int(GM_no_data[CarlSagan])

    print(f"\nStarting IDA for RSN {current_RSN}")

    for pga_factor in PGA_factors:

        if (current_RSN, pga_factor) in completed_pairs:
            print(f"RSN {current_RSN}, PGA factor {pga_factor} already completed. Skipping...")
            continue

        # Run analysis
        last_MIDR = run_analysis(sample_number, pga_factor, CarlSagan)

        print(f"RSN {current_RSN}, PGA factor {pga_factor:.1f}, MIDR = {last_MIDR:.3f}%")

        if last_MIDR >= 4.0:
            print(f"Collapse reached (MIDR = {last_MIDR:.3f}%). Moving to next ground motion.")
            break

