print("------------------------------------------------------------")
# source /Users/niraj/x86_env/bin/activate 

import openseespy.opensees as ops
import numpy as np
import matplotlib.pyplot as plt
import opsvis as opsv

from dimensions import *

ops.wipe()
ops.model('BasicBuilder', '-ndm', 3, '-ndf', 6)

#----------------------------------------------------------------------------------
# Geometry, Dimensions And Units (mm, s, N) , Global axes X, Y, Z (vertical) 
#----------------------------------------------------------------------------------
# Nomenclature  
# plane = coordinate (i, j, k) +1
# Node numbering : (X plane) (Y plane) (Z plane)
# Element numbering : (start X plane) (end X plane) (start Y plane) (end Y plane) (start Z plane) (end Z plane)
# Rigid diaphragm node numbering || Master Nodes : 9990 + Z plane

NplaneX = NBayX + 1
NplaneY = NBayY + 1
NplaneZ = NBayZ + 1

# --------------------------------------------------------------------------------
# Nodes
# --------------------------------------------------------------------------------

# structure nodes-----------------
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

# --------------------------------------------------------------------------------
# Sections, 1 cover, 2 core, 3 steel
# --------------------------------------------------------------------------------

from Materials import *
from FiberSectionBuilder import *

# Section tags
Beam_1_SecTag = 1
Beam_2_SecTag = 2
Col_1_SecTag = 3
Col_2_SecTag = 4

Beam_1_SecTag_Fiber = 11
Beam_2_SecTag_Fiber = 12
Col_1_SecTag_Fiber = 13
Col_2_SecTag_Fiber = 14

TorsionSecTag = 21    # NOTE Torsion is not used in the code, just for reference

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

    # Beam Type 2
    Beam_2_sec_name = 'Beam Type 2 Section'
    nBT_Beam_2 = 3       # no. of longitudinal-reinforcement bars on top layer || to local z axis
    nBM_Beam_2 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
    nBI_Beam_2 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBB_Beam_2 = 3       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
    aBT_Beam_2 = area(12.0)         # area of top layer bars || to local z axis
    aBM_Beam_2 = area(12.0)         # area of mid layer bars || to local z axis
    aBI_Beam_2 = area(12.0)         # area of mid layer bars || to local y axis
    aBB_Beam_2 = area(12.0)         # area of bottom layer bars || to local z axis
    nfCore_y_Beam_2 = 6      # number of fibers in the core patch in local y axis
    nfCore_z_Beam_2 = 6      # number of fibers in the core patch in local z axis
    nfCover_y_Beam_2 = 6     # number of fibers in the cover patches with long sides || to local y axis
    nfCover_z_Beam_2 = 6     # number of fibers in the cover patches with long sides || to local z axis

    # Column Type 1
    Col_1_sec_name = 'Col Type 1 Section'
    nBT_Col_1 = 3       # no. of longitudinal-reinforcement bars on top layer || to local z axis
    nBM_Col_1 = 2       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
    nBI_Col_1 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBB_Col_1 = 3       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
    aBT_Col_1 = area(16.0)         # area of top layer bars || to local z axis
    aBM_Col_1 = area(16.0)         # area of mid layer bars || to local z axis
    aBI_Col_1 = area(16.0)         # area of mid layer bars || to local y axis
    aBB_Col_1 = area(16.0)         # area of bottom layer bars || to local z axis
    nfCore_y_Col_1 = 6      # number of fibers in the core patch in local y axis
    nfCore_z_Col_1 = 6      # number of fibers in the core patch in local z axis
    nfCover_y_Col_1 = 6     # number of fibers in the cover patches with long sides || to local y axis
    nfCover_z_Col_1 = 6     # number of fibers in the cover patches with long sides || to local z axis

    # Column Type 2
    Col_2_sec_name = 'Col Type 2 Section'
    nBT_Col_2 = 3       # no. of longitudinal-reinforcement bars on top layer || to local z axis
    nBM_Col_2 = 2       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
    nBI_Col_2 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBB_Col_2 = 3       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
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
    
    Section (Beam_2_SecTag_Fiber, Beam_2_sec_name,
              Beam_2_y, Beam_2_z, Beam_2_Cover, 
              nfCore_y_Beam_2, nfCore_z_Beam_2, 
              nfCover_y_Beam_2, nfCover_z_Beam_2, 
              nBT_Beam_2, nBM_Beam_2, nBI_Beam_2, nBB_Beam_2,
              aBT_Beam_2, aBM_Beam_2, aBI_Beam_2, aBB_Beam_2, 
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

    # ops.uniaxialMaterial("Elastic", TorsionSecTag, 1.0e6) # torsion section
    # # section('Aggregator', secTag, *mats, '-section', sectionTag)
    # ops.section('Aggregator', Beam_1_SecTag, TorsionSecTag, 'T', '-section', Beam_1_SecTag_Fiber)
    # ops.section('Aggregator', Beam_2_SecTag, TorsionSecTag, 'T', '-section', Beam_2_SecTag_Fiber)
    # ops.section('Aggregator', Col_1_SecTag, TorsionSecTag, 'T', '-section', Col_1_SecTag_Fiber)
    # ops.section('Aggregator', Col_2_SecTag, TorsionSecTag, 'T', '-section', Col_2_SecTag_Fiber)

Section_Builder()

# --------------------------------------------------------------------------------
# Elements
# --------------------------------------------------------------------------------

# Geometry transformations -----------------------
Beam_X_TransfTag = 1
Beam_Y_TransfTag = 2
Col_TransfTag = 3 

#geomTransf(transfType, transfTag, *transfArgs)
ops.geomTransf('Linear', Beam_X_TransfTag, 0, -1, 0)  
ops.geomTransf('Linear', Beam_Y_TransfTag, 1, 0, 0)   
ops.geomTransf('PDelta', Col_TransfTag, -1, 0, 0)   

#  Integration setup -----------------------------

#beamIntegration('Lobatto', tag, secTag, N)
Beam_1_IntTag = 1
Beam_2_IntTag = 2
Col_1_IntTag = 3
Col_2_IntTag = 4

numIntPts_Beam = 3
numIntPts_Col = 5

ops.beamIntegration('Lobatto', Beam_1_IntTag, Beam_1_SecTag_Fiber, numIntPts_Beam)
ops.beamIntegration('Lobatto', Beam_2_IntTag, Beam_2_SecTag_Fiber, numIntPts_Beam)
ops.beamIntegration('Lobatto', Col_1_IntTag, Col_1_SecTag_Fiber, numIntPts_Col)
ops.beamIntegration('Lobatto', Col_2_IntTag, Col_2_SecTag_Fiber, numIntPts_Col)

#  Elements setup -----------------------------

Beam_1_mpul = Beam_1_y * Beam_1_z * gamma_conc / g
Beam_2_mpul = Beam_2_y * Beam_2_z * gamma_conc / g
Col_1_mpul = Col_1_y * Col_1_z * gamma_conc / g
Col_2_mpul = Col_2_y * Col_2_z * gamma_conc / g

# X_Beam elements 
X_Beam_1_Tags = []
X_Beam_2_Tags = []
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
            if planeZ == 2:
                ops.element('forceBeamColumn', XBeamTag, startNode, endNode, Beam_X_TransfTag, Beam_1_IntTag, '-mass', Beam_1_mpul)
                X_Beam_1_Tags.append(XBeamTag)
            else:
                ops.element('forceBeamColumn', XBeamTag, startNode, endNode, Beam_X_TransfTag, Beam_2_IntTag, '-mass', Beam_2_mpul)
                X_Beam_2_Tags.append(XBeamTag)

# Y_Beam elements 
Y_Beam_1_Tags = []
Y_Beam_2_Tags = []
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
            if planeZ == 2:
                ops.element('forceBeamColumn', YBeamTag, startNode, endNode, Beam_Y_TransfTag, Beam_1_IntTag, '-mass', Beam_1_mpul)
                Y_Beam_1_Tags.append(YBeamTag)
            else:
                ops.element('forceBeamColumn', YBeamTag, startNode, endNode, Beam_Y_TransfTag, Beam_2_IntTag, '-mass', Beam_2_mpul)
                Y_Beam_2_Tags.append(YBeamTag)

Beam_1_Tags = X_Beam_1_Tags + Y_Beam_1_Tags
Beam_2_Tags = X_Beam_2_Tags + Y_Beam_2_Tags
Beam_tags = Beam_1_Tags + Beam_1_Tags

# Column elements
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
            if planeZ == 1:
                ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_1_IntTag, 'mass', Col_1_mpul)
                Column_1_Tags.append(ColTag)
            else:
                ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_2_IntTag, 'mass', Col_2_mpul)
                Column_2_Tags.append(ColTag)

Column_Tags = Column_1_Tags + Column_2_Tags

# print(f'Beam 1 X : {X_Beam_1_Tags}')
# print(f'Beam 1 Y : {Y_Beam_1_Tags}')
# print(f'Beam 2 X : {X_Beam_2_Tags}')
# print(f'Beam 2 Y : {Y_Beam_2_Tags}')
# print(f'Column 1 : {Column_1_Tags}')
# print(f'Column 2 : {Column_2_Tags}')

# --------------------------------------------------------------------------------
# Gravity loads
# --------------------------------------------------------------------------------

Q_slab = gamma_conc * slab_thickness       # Self weight of Slab N per mm2
Q_floor_finish = 1.0e-3                    # Floor finish load N per mm2  
LL = 1.0e-3                                # Live load for all floors N per mm2

TL = Q_slab + Q_floor_finish + LL          # Total load for all floors N per mm2

if bay_width_Y/bay_width_X <= 2.0 :
    P1 = TL * (bay_width_X / 2) * (bay_width_Y - bay_width_X / 2) # N
    P2 = TL * (1/4) * (bay_width_X ** 2)                          # N
else :
    P1 = TL * (bay_width_X * bay_width_Y) / 2
    P2 = 0
# ---------------------------------
O_YBeam = P1 / g        # External Load on Outside Y Beam in mass terms : N s2 / mm
I_YBeam = 2 * P1 / g    # External Load on Inside Y Beam in mass terms : N s2 / mm

O_XBeam = P2 / g        # External Load on Outside X Beam in mass terms : N s2 / mm
I_XBeam = 2 * P2 / g    # External Load on Inside X Beam in mass terms : N s2 / mm

Col = 0                 # External Load on Column in mass terms : N s2 / mm

# Nodal Mass Distribution ----------------------------------------------------------------
# if rigidDiaphragm == 1:
#     for master_nodeTag in master_nodes:
#         mass = TL * NBayX * bay_width_X * NBayY * bay_width_Y / g
#         ops.mass(master_nodeTag, mass, mass, 0.0, 0.0, 0.0, 1.0e3)
# else:
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
            ops.mass(nodeTag, mass, mass, 0.0, 0.0, 0.0, 1.0e3)

# --------------------------------------------------------------------------------
# Eigenvalue Analysis 
# --------------------------------------------------------------------------------
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

print("Time Periods are:", [f"{p:.10f}" for p in periods])

# --------------------------------------------------------------------------------
# Application Of UDL in local coordinate axes 
# --------------------------------------------------------------------------------
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

P11 = P1 / bay_width_Y  # External Load on beams in Y Direction in N / mm
P12 = P2 / bay_width_X  # External Load on beams in X Direction in N / mm
P3 = gamma_conc * Beam_1_y * Beam_1_z      # Total Self weight of Beam 1 N / mm
P4 = gamma_conc * Beam_2_y * Beam_2_z      # Total Self weight of Beam 2 N / mm
P5 = gamma_conc * Col_1_y * Col_1_z        # Total Self weight of Column 1 N / mm
P6 = gamma_conc * Col_2_y * Col_2_z        # Total Self weight of Column 2 N / mm

# print(P1, P2, P11, P12, P3, P4, P5, P6)

def UDL_applier():
    # Beam 1 loading
    for tag in X_Beam_1_Tags:
        tag_str = str(tag).zfill(6)  # ensures it's 6 digits with leading zeros if needed
        starty = int(tag_str[2])
        if starty in (1, NplaneY):
            UDL = P12 + P3
        else:
            UDL = 2 * P12 + P3
        ops.eleLoad('-ele', tag, '-type', '-beamUniform', -UDL, 0.0, 0.0)

    for tag in Y_Beam_1_Tags:
        tag_str = str(tag).zfill(6)  # ensures it's 6 digits with leading zeros if needed
        startx = int(tag_str[0])
        if startx in (1, NplaneX):
            UDL = P11 + P3
        else:
            UDL = 2 * P11 + P3
        ops.eleLoad('-ele', tag, '-type', '-beamUniform', -UDL, 0.0, 0.0)

    # Beam 2 loading
    for tag in X_Beam_2_Tags:
        tag_str = str(tag).zfill(6)  # ensures it's 6 digits with leading zeros if needed
        starty = int(tag_str[2])
        if starty in (1, NplaneY):
            UDL = P12 + P4
        else:
            UDL = 2 * P12 + P4
        ops.eleLoad('-ele', tag, '-type', '-beamUniform', -UDL, 0.0, 0.0)

    for tag in Y_Beam_2_Tags:
        tag_str = str(tag).zfill(6)  # ensures it's 6 digits with leading zeros if needed
        startx = int(tag_str[0])
        if startx in (1, NplaneX):
            UDL = P11 + P4
        else:
            UDL = 2 * P11 + P4
        ops.eleLoad('-ele', tag, '-type', '-beamUniform', -UDL, 0.0, 0.0)

    for tag in Column_1_Tags:
        UDL = P5
        ops.eleLoad('-ele', tag, '-type', '-beamUniform', 0.0, 0.0, -UDL)

    for tag in Column_2_Tags:
        UDL = P6
        ops.eleLoad('-ele', tag, '-type', '-beamUniform', 0.0, 0.0, -UDL)

UDL_applier()  # Call this function to apply the loads as UDL

# --------------------------------------------------------------------------------
# Plotting the model
# --------------------------------------------------------------------------------

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

    ele_shapes = {**{i: ['rect', [Beam_1_z, Beam_1_z]] for i in Beam_1_Tags}, 
                **{i: ['rect', [Beam_2_z, Beam_2_z]] for i in Beam_2_Tags},
                **{i: ['rect', [Col_1_z, Col_1_y]] for i in Column_1_Tags},
                **{i: ['rect', [Col_2_z, Col_2_y]] for i in Column_2_Tags}  
                }
    opsv.plot_extruded_shapes_3d(ele_shapes)
    plt.title("Extruded Shape 3D")

    plt.show()

# Plotter()