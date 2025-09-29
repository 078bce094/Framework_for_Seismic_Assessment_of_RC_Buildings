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
Beam_3_SecTag = 3

Beam_4_SecTag = 4
Beam_5_SecTag = 5
Beam_6_SecTag = 6

Col_1_SecTag = 7
Col_2_SecTag = 8
Col_3_SecTag = 9

def Section_Builder ():

    def area(diameter):
        return (np.pi * diameter ** 2) / 4.0

    Beam_1_sec_name = 'Beam Along X, Storey I Section'
    Beam_2_sec_name = 'Beam Along X, Storey II Section'
    Beam_3_sec_name = 'Beam Along X, Storey III Section'

    Beam_4_sec_name = 'Beam Along Y, Storey I Section'
    Beam_5_sec_name = 'Beam Along Y, Storey II Section'
    Beam_6_sec_name = 'Beam Along Y, Storey III Section'

    if bay_width_X <= 3000.0:

        nBT_Beam_1, nBM_Beam_1, nBIU_Beam_1, nBID_Beam_1, nBB_Beam_1  = 2, 0, 1, 1, 2           
        aBT_Beam_1, aBM_Beam_1, aBIU_Beam_1, aBID_Beam_1, aBB_Beam_1 = area(16.0), area(12.0), area(12.0), area(12.0), area(16.0) 
        Section (Beam_1_SecTag, Beam_1_sec_name,
            Beam_1_y, Beam_1_z, Beam_1_Cover, 
            6, 6, 6, 6, 
            nBT_Beam_1, nBM_Beam_1, nBIU_Beam_1, nBID_Beam_1, nBB_Beam_1,
            aBT_Beam_1, aBM_Beam_1, aBIU_Beam_1, aBID_Beam_1, aBB_Beam_1,
            confined_concrete_tag, unconfined_concrete_tag, steel_tag)

        nBT_Beam_2, nBM_Beam_2, nBIU_Beam_2, nBID_Beam_2, nBB_Beam_2  = 2, 0, 1, 1, 2           
        aBT_Beam_2, aBM_Beam_2, aBIU_Beam_2, aBID_Beam_2, aBB_Beam_2 = area(12.0), area(12.0), area(16.0), area(12.0), area(12.0) 

        nBT_Beam_3, nBM_Beam_3, nBIU_Beam_3, nBID_Beam_3, nBB_Beam_3  = 2, 0, 1, 0, 2           
        aBT_Beam_3, aBM_Beam_3, aBIU_Beam_3, aBID_Beam_3, aBB_Beam_3 = area(12.0), area(10.0), area(10.0), area(10.0), area(12.0) 

    elif 3500.0 >= bay_width_X > 3000.0:

        nBT_Beam_1, nBM_Beam_1, nBIU_Beam_1, nBID_Beam_1, nBB_Beam_1  = 2, 0, 1, 1, 2           
        aBT_Beam_1, aBM_Beam_1, aBIU_Beam_1, aBID_Beam_1, aBB_Beam_1 = area(16.0), area(12.0), area(16.0), area(16.0), area(16.0) 
        Section (Beam_1_SecTag, Beam_1_sec_name,
            Beam_1_y, Beam_1_z, Beam_1_Cover, 
            6, 6, 6, 6, 
            nBT_Beam_1, nBM_Beam_1, nBIU_Beam_1, nBID_Beam_1, nBB_Beam_1,
            aBT_Beam_1, aBM_Beam_1, aBIU_Beam_1, aBID_Beam_1, aBB_Beam_1,
            confined_concrete_tag, unconfined_concrete_tag, steel_tag)

        nBT_Beam_2, nBM_Beam_2, nBIU_Beam_2, nBID_Beam_2, nBB_Beam_2  = 4, 0, 0, 1, 2           
        aBT_Beam_2, aBM_Beam_2, aBIU_Beam_2, aBID_Beam_2, aBB_Beam_2 = area(12.0), area(12.0), area(12.0), area(16.0), area(12.0) 

        nBT_Beam_3, nBM_Beam_3, nBIU_Beam_3, nBID_Beam_3, nBB_Beam_3  = 2, 0, 1, 1, 2           
        aBT_Beam_3, aBM_Beam_3, aBIU_Beam_3, aBID_Beam_3, aBB_Beam_3 = area(12.0), area(10.0), area(10.0), area(10.0), area(12.0)

    elif 4000.0 >= bay_width_X > 3500.0:
        # nBT, nBTM, nBID, nBB, aBT, aBTM, aBID, aBB :  Beam 1 is type 2
        nBT_Beam_1, nBTM_Beam_1, nBID_Beam_1, nBB_Beam_1  = 2, 2, 0, 3           
        aBT_Beam_1, aBTM_Beam_1, aBID_Beam_1, aBB_Beam_1 = area(16.0), area(12.0), area(16.0), area(16.0) 
        Section_type2 (Beam_1_SecTag, Beam_1_sec_name,
            Beam_1_y, Beam_1_z, Beam_1_Cover, 
            6, 6, 6, 6, 
            nBT_Beam_1, nBTM_Beam_1, nBID_Beam_1, nBB_Beam_1,
            aBT_Beam_1, aBTM_Beam_1, aBID_Beam_1, aBB_Beam_1,
            confined_concrete_tag, unconfined_concrete_tag, steel_tag)

        nBT_Beam_2, nBM_Beam_2, nBIU_Beam_2, nBID_Beam_2, nBB_Beam_2  = 2, 0, 1, 1, 2           
        aBT_Beam_2, aBM_Beam_2, aBIU_Beam_2, aBID_Beam_2, aBB_Beam_2 = area(16.0), area(12.0), area(12.0), area(10.0), area(16.0) 

        nBT_Beam_3, nBM_Beam_3, nBIU_Beam_3, nBID_Beam_3, nBB_Beam_3  = 3, 0, 0, 1, 2           
        aBT_Beam_3, aBM_Beam_3, aBIU_Beam_3, aBID_Beam_3, aBB_Beam_3 = area(12.0), area(12.0), area(10.0), area(10.0), area(12.0)
    
    else :
        # nBT1, nBT2, nBIU, nBID, nBB, aBT1, aBT2, aBIU, aBID, aBB : Beam 1 is type 1
        nBT1_Beam_1, nBT2_Beam_1, nBIU_Beam_1, nBID_Beam_1, nBB_Beam_1  = 2, 2, 1, 0, 3           
        aBT1_Beam_1, aBT2_Beam_1, aBIU_Beam_1, aBID_Beam_1, aBB_Beam_1 = area(16.0), area(12.0), area(12.0), area(12.0), area(16.0) 
        Section_type1 (Beam_1_SecTag, Beam_1_sec_name,
        Beam_1_y, Beam_1_z, Beam_1_Cover, 
        6, 6, 6, 6, 
        nBT1_Beam_1, nBT2_Beam_1, nBIU_Beam_1, nBID_Beam_1, nBB_Beam_1,
        aBT1_Beam_1, aBT2_Beam_1, aBIU_Beam_1, aBID_Beam_1, aBB_Beam_1,
        confined_concrete_tag, unconfined_concrete_tag, steel_tag)

        nBT_Beam_2, nBM_Beam_2, nBIU_Beam_2, nBID_Beam_2, nBB_Beam_2  = 3, 0, 0, 1, 2           
        aBT_Beam_2, aBM_Beam_2, aBIU_Beam_2, aBID_Beam_2, aBB_Beam_2 = area(16.0), area(12.0), area(12.0), area(12.0), area(16.0) 

        nBT_Beam_3, nBM_Beam_3, nBIU_Beam_3, nBID_Beam_3, nBB_Beam_3  = 3, 0, 0, 0, 3           
        aBT_Beam_3, aBM_Beam_3, aBIU_Beam_3, aBID_Beam_3, aBB_Beam_3 = area(12.0), area(10.0), area(10.0), area(10.0), area(12.0)

    Section (Beam_2_SecTag, Beam_2_sec_name,
              Beam_2_y, Beam_2_z, Beam_2_Cover, 
              6, 6, 6, 6, 
              nBT_Beam_2, nBM_Beam_2, nBIU_Beam_2, nBID_Beam_2, nBB_Beam_2,
              aBT_Beam_2, aBM_Beam_2, aBIU_Beam_2, aBID_Beam_2, aBB_Beam_2,
              confined_concrete_tag, unconfined_concrete_tag, steel_tag)

    Section (Beam_3_SecTag, Beam_3_sec_name,
              Beam_3_y, Beam_3_z, Beam_3_Cover, 
              6, 6, 6, 6, 
              nBT_Beam_3, nBM_Beam_3, nBIU_Beam_3, nBID_Beam_3, nBB_Beam_3,
              aBT_Beam_3, aBM_Beam_3, aBIU_Beam_3, aBID_Beam_3, aBB_Beam_3,
              confined_concrete_tag, unconfined_concrete_tag, steel_tag)
    
    if bay_width_Y <= 3000.0:

        nBT_Beam_4, nBM_Beam_4, nBIU_Beam_4, nBID_Beam_4, nBB_Beam_4  = 2, 0, 1, 1, 2           
        aBT_Beam_4, aBM_Beam_4, aBIU_Beam_4, aBID_Beam_4, aBB_Beam_4 = area(16.0), area(12.0), area(12.0), area(12.0), area(16.0) 
        Section (Beam_4_SecTag, Beam_4_sec_name,
            Beam_4_y, Beam_4_z, Beam_4_Cover, 
            6, 6, 6, 6, 
            nBT_Beam_4, nBM_Beam_4, nBIU_Beam_4, nBID_Beam_4, nBB_Beam_4,
            aBT_Beam_4, aBM_Beam_4, aBIU_Beam_4, aBID_Beam_4, aBB_Beam_4,
            confined_concrete_tag, unconfined_concrete_tag, steel_tag)

        nBT_Beam_5, nBM_Beam_5, nBIU_Beam_5, nBID_Beam_5, nBB_Beam_5  = 2, 0, 1, 1, 2           
        aBT_Beam_5, aBM_Beam_5, aBIU_Beam_5, aBID_Beam_5, aBB_Beam_5 = area(12.0), area(12.0), area(16.0), area(12.0), area(12.0) 

        nBT_Beam_6, nBM_Beam_6, nBIU_Beam_6, nBID_Beam_6, nBB_Beam_6  = 2, 0, 1, 0, 2           
        aBT_Beam_6, aBM_Beam_6, aBIU_Beam_6, aBID_Beam_6, aBB_Beam_6 = area(12.0), area(10.0), area(10.0), area(10.0), area(12.0) 

    elif 3500.0 >= bay_width_Y > 3000.0:

        nBT_Beam_4, nBM_Beam_4, nBIU_Beam_4, nBID_Beam_4, nBB_Beam_4  = 2, 0, 1, 1, 2           
        aBT_Beam_4, aBM_Beam_4, aBIU_Beam_4, aBID_Beam_4, aBB_Beam_4 = area(16.0), area(12.0), area(16.0), area(16.0), area(16.0) 
        Section (Beam_4_SecTag, Beam_4_sec_name,
            Beam_4_y, Beam_4_z, Beam_4_Cover, 
            6, 6, 6, 6, 
            nBT_Beam_4, nBM_Beam_4, nBIU_Beam_4, nBID_Beam_4, nBB_Beam_4,
            aBT_Beam_4, aBM_Beam_4, aBIU_Beam_4, aBID_Beam_4, aBB_Beam_4,
            confined_concrete_tag, unconfined_concrete_tag, steel_tag)

        nBT_Beam_5, nBM_Beam_5, nBIU_Beam_5, nBID_Beam_5, nBB_Beam_5  = 4, 0, 0, 1, 2           
        aBT_Beam_5, aBM_Beam_5, aBIU_Beam_5, aBID_Beam_5, aBB_Beam_5 = area(12.0), area(12.0), area(12.0), area(16.0), area(12.0) 

        nBT_Beam_6, nBM_Beam_6, nBIU_Beam_6, nBID_Beam_6, nBB_Beam_6  = 2, 0, 1, 1, 2           
        aBT_Beam_6, aBM_Beam_6, aBIU_Beam_6, aBID_Beam_6, aBB_Beam_6 = area(12.0), area(10.0), area(10.0), area(10.0), area(12.0)

    elif 4000.0 >= bay_width_Y > 3500.0:
        # nBT, nBTM, nBID, nBB, aBT, aBTM, aBID, aBB :  Beam 1 is type 2
        nBT_Beam_4, nBTM_Beam_4, nBID_Beam_4, nBB_Beam_4  = 2, 2, 0, 3           
        aBT_Beam_4, aBTM_Beam_4, aBID_Beam_4, aBB_Beam_4 = area(16.0), area(12.0), area(16.0), area(16.0) 
        Section_type2 (Beam_4_SecTag, Beam_4_sec_name,
            Beam_4_y, Beam_4_z, Beam_4_Cover, 
            6, 6, 6, 6, 
            nBT_Beam_4, nBTM_Beam_4, nBID_Beam_4, nBB_Beam_4,
            aBT_Beam_4, aBTM_Beam_4, aBID_Beam_4, aBB_Beam_4,
            confined_concrete_tag, unconfined_concrete_tag, steel_tag)

        nBT_Beam_5, nBM_Beam_5, nBIU_Beam_5, nBID_Beam_5, nBB_Beam_5  = 2, 0, 1, 1, 2           
        aBT_Beam_5, aBM_Beam_5, aBIU_Beam_5, aBID_Beam_5, aBB_Beam_5 = area(16.0), area(12.0), area(12.0), area(10.0), area(16.0) 

        nBT_Beam_6, nBM_Beam_6, nBIU_Beam_6, nBID_Beam_6, nBB_Beam_6  = 3, 0, 0, 1, 2           
        aBT_Beam_6, aBM_Beam_6, aBIU_Beam_6, aBID_Beam_6, aBB_Beam_6 = area(12.0), area(12.0), area(10.0), area(10.0), area(12.0)
    
    else :
        # nBT1, nBT2, nBIU, nBID, nBB, aBT1, aBT2, aBIU, aBID, aBB : Beam 1 is type 1
        nBT1_Beam_4, nBT2_Beam_4, nBIU_Beam_4, nBID_Beam_4, nBB_Beam_4  = 2, 2, 1, 0, 3           
        aBT1_Beam_4, aBT2_Beam_4, aBIU_Beam_4, aBID_Beam_4, aBB_Beam_4 = area(16.0), area(12.0), area(12.0), area(12.0), area(16.0) 
        Section_type1 (Beam_4_SecTag, Beam_4_sec_name,
        Beam_4_y, Beam_4_z, Beam_4_Cover, 
        6, 6, 6, 6, 
        nBT1_Beam_4, nBT2_Beam_4, nBIU_Beam_4, nBID_Beam_4, nBB_Beam_4,
        aBT1_Beam_4, aBT2_Beam_4, aBIU_Beam_4, aBID_Beam_4, aBB_Beam_4,
        confined_concrete_tag, unconfined_concrete_tag, steel_tag)

        nBT_Beam_5, nBM_Beam_5, nBIU_Beam_5, nBID_Beam_5, nBB_Beam_5  = 3, 0, 0, 1, 2           
        aBT_Beam_5, aBM_Beam_5, aBIU_Beam_5, aBID_Beam_5, aBB_Beam_5 = area(16.0), area(12.0), area(12.0), area(12.0), area(16.0) 

        nBT_Beam_6, nBM_Beam_6, nBIU_Beam_6, nBID_Beam_6, nBB_Beam_6  = 3, 0, 0, 0, 3           
        aBT_Beam_6, aBM_Beam_6, aBIU_Beam_6, aBID_Beam_6, aBB_Beam_6 = area(12.0), area(10.0), area(10.0), area(10.0), area(12.0)

    Section (Beam_5_SecTag, Beam_5_sec_name,
              Beam_5_y, Beam_5_z, Beam_5_Cover, 
              6, 6, 6, 6, 
              nBT_Beam_5, nBM_Beam_5, nBIU_Beam_5, nBID_Beam_5, nBB_Beam_5,
              aBT_Beam_5, aBM_Beam_5, aBIU_Beam_5, aBID_Beam_5, aBB_Beam_5,
              confined_concrete_tag, unconfined_concrete_tag, steel_tag)

    Section (Beam_6_SecTag, Beam_6_sec_name,
              Beam_6_y, Beam_6_z, Beam_6_Cover, 
              6, 6, 6, 6, 
              nBT_Beam_6, nBM_Beam_6, nBIU_Beam_6, nBID_Beam_6, nBB_Beam_6,
              aBT_Beam_6, aBM_Beam_6, aBIU_Beam_6, aBID_Beam_6, aBB_Beam_6,
              confined_concrete_tag, unconfined_concrete_tag, steel_tag)

    # Column Type 1
    Col_1_sec_name = 'Col Type 1 Section : 4-16'
    nBT_Col_1 = 2       # no. of longitudinal-reinforcement bars on top layer || to local z axis
    nBM_Col_1 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
    nBIU_Col_1 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBID_Col_1 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBB_Col_1 = 2       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
    aBT_Col_1 = area(16.0)         # area of top layer bars || to local z axis
    aBM_Col_1 = area(16.0)         # area of mid layer bars || to local z axis
    aBIU_Col_1 = area(16.0)         # area of mid layer bars || to local y axis
    aBID_Col_1 = area(16.0)         # area of mid layer bars || to local y axis
    aBB_Col_1 = area(16.0)         # area of bottom layer bars || to local z axis

    # Column Type 2
    Col_2_sec_name = 'Col Type 2 Section : 4-12'
    nBT_Col_2 = 2       # no. of longitudinal-reinforcement bars on top layer || to local z axis
    nBM_Col_2 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
    nBIU_Col_2 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBID_Col_2 = 0       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBB_Col_2 = 2       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
    aBT_Col_2 = area(12.0)         # area of top layer bars || to local z axis
    aBM_Col_2 = area(12.0)         # area of mid layer bars || to local z axis
    aBIU_Col_2 = area(12.0)         # area of mid layer bars || to local y axis
    aBID_Col_2 = area(12.0)         # area of mid layer bars || to local y axis
    aBB_Col_2 = area(12.0)         # area of bottom layer bars || to local z axis

    # Column Type 3
    Col_3_sec_name = 'Col Type 3 Section : 8-12'
    nBT_Col_3 = 2       # no. of longitudinal-reinforcement bars on top layer || to local z axis
    nBM_Col_3 = 2       # no. of longitudinal-reinforcement bars on mid layer || to local z axis
    nBIU_Col_3 = 1       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBID_Col_3 = 1       # no. of longitudinal-reinforcement bars on mid layer || to local y axis
    nBB_Col_3 = 2       # no. of longitudinal-reinforcement bars on bottom layer || to local z axis
    aBT_Col_3 = area(12.0)         # area of top layer bars || to local z axis
    aBM_Col_3 = area(12.0)         # area of mid layer bars || to local z axis
    aBIU_Col_3 = area(12.0)         # area of mid layer bars || to local y axis
    aBID_Col_3 = area(12.0)         # area of mid layer bars || to local y axis
    aBB_Col_3 = area(12.0)         # area of bottom layer bars || to local z axis
    
    Section (Col_1_SecTag, Col_1_sec_name,
              Col_1_y, Col_1_z, Col_1_Cover, 
              6, 6, 6, 6, 
              nBT_Col_1, nBM_Col_1, nBIU_Col_1, nBID_Col_1, nBB_Col_1,
              aBT_Col_1, aBM_Col_1, aBIU_Col_1, aBID_Col_1, aBB_Col_1, 
              confined_concrete_tag, unconfined_concrete_tag, steel_tag)
    
    Section (Col_2_SecTag, Col_2_sec_name,
              Col_2_y, Col_2_z, Col_2_Cover, 
              6, 6, 6, 6, 
              nBT_Col_2, nBM_Col_2, nBIU_Col_2, nBID_Col_2, nBB_Col_2,
              aBT_Col_2, aBM_Col_2, aBIU_Col_2, aBID_Col_2, aBB_Col_2, 
              confined_concrete_tag, unconfined_concrete_tag, steel_tag)
    
    Section (Col_3_SecTag, Col_3_sec_name,
              Col_3_y, Col_3_z, Col_3_Cover, 
              6, 6, 6, 6, 
              nBT_Col_3, nBM_Col_3, nBIU_Col_3, nBID_Col_3, nBB_Col_3,
              aBT_Col_3, aBM_Col_3, aBIU_Col_3, aBID_Col_3, aBB_Col_3, 
              confined_concrete_tag, unconfined_concrete_tag, steel_tag)
    
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

# Integration setup -----------------------------

#beamIntegration('Lobatto', tag, secTag, N)
Beam_1_IntTag = 1
Beam_2_IntTag = 2
Beam_3_IntTag = 3
Beam_4_IntTag = 4
Beam_5_IntTag = 5
Beam_6_IntTag = 6

Col_1_IntTag = 7
Col_2_IntTag = 8
Col_3_IntTag = 9

numIntPts_Beam = 3
numIntPts_Col = 5

ops.beamIntegration('Lobatto', Beam_1_IntTag, Beam_1_SecTag, numIntPts_Beam)
ops.beamIntegration('Lobatto', Beam_2_IntTag, Beam_2_SecTag, numIntPts_Beam)
ops.beamIntegration('Lobatto', Beam_3_IntTag, Beam_3_SecTag, numIntPts_Beam)
ops.beamIntegration('Lobatto', Beam_4_IntTag, Beam_4_SecTag, numIntPts_Beam)
ops.beamIntegration('Lobatto', Beam_5_IntTag, Beam_5_SecTag, numIntPts_Beam)
ops.beamIntegration('Lobatto', Beam_6_IntTag, Beam_6_SecTag, numIntPts_Beam)

ops.beamIntegration('Lobatto', Col_1_IntTag, Col_1_SecTag, numIntPts_Col)
ops.beamIntegration('Lobatto', Col_2_IntTag, Col_2_SecTag, numIntPts_Col)
ops.beamIntegration('Lobatto', Col_3_IntTag, Col_3_SecTag, numIntPts_Col)

#  Elements setup -----------------------------

Beam_mpul = Beam_1_y * Beam_1_z * gamma_conc / g   # Dimensions of every beam is same
Col_1_mpul = Col_1_y * Col_1_z * gamma_conc / g
Col_2_mpul = Col_2_y * Col_2_z * gamma_conc / g
Col_3_mpul = Col_3_y * Col_3_z * gamma_conc / g

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
            if planeZ == 2:   # storey I
                ops.element('forceBeamColumn', XBeamTag, startNode, endNode, Beam_X_TransfTag, Beam_1_IntTag, '-mass', Beam_mpul)
            elif planeZ == 3: # storey II
                ops.element('forceBeamColumn', XBeamTag, startNode, endNode, Beam_X_TransfTag, Beam_2_IntTag, '-mass', Beam_mpul)
            else: # storey III
                ops.element('forceBeamColumn', XBeamTag, startNode, endNode, Beam_X_TransfTag, Beam_3_IntTag, '-mass', Beam_mpul)
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
            if planeZ == 2:     # storey I
                ops.element('forceBeamColumn', YBeamTag, startNode, endNode, Beam_Y_TransfTag, Beam_4_IntTag, '-mass', Beam_mpul)
            elif planeZ == 3:   # storey II
                ops.element('forceBeamColumn', YBeamTag, startNode, endNode, Beam_Y_TransfTag, Beam_5_IntTag, '-mass', Beam_mpul)
            else:
                ops.element('forceBeamColumn', YBeamTag, startNode, endNode, Beam_Y_TransfTag, Beam_6_IntTag, '-mass', Beam_mpul)
            Y_Beam_Tags.append(YBeamTag)

Beam_tags = X_Beam_Tags + Y_Beam_Tags

# Column elements
ground_floor_col_tags = []
Column_1_Tags = []
Column_2_Tags = []
Column_3_Tags = []
for i in range(NplaneX):
    startX = i + 1
    endX = i + 1
    planeX = i + 1
    for j in range(NplaneY):
        startY = j + 1
        endY = j + 1
        planeY = j + 1
        for k in range(NplaneZ - 1):
            startZ = k + 1
            endZ = startZ + 1
            planeZ = k + 1
            ColTag = startX * 100000 + endX * 10000 + startY * 1000 + endY * 100 + startZ * 10 + endZ
            startNode = startX * 100 + startY * 10 + startZ
            endNode = endX * 100 + endY * 10 + endZ
            if planeZ == 1:
                if planeX in (1, NplaneX) and planeY in (1, NplaneY):   # corner
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_1_IntTag, 'mass', Col_1_mpul)
                    Column_1_Tags.append(ColTag)
                elif planeX not in (1, NplaneX) and planeY not in (1, NplaneY):  # interior
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_3_IntTag, 'mass', Col_3_mpul)
                    Column_3_Tags.append(ColTag)
                else:   # face
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_1_IntTag, 'mass', Col_1_mpul)
                    Column_1_Tags.append(ColTag)
                ground_floor_col_tags.append(ColTag)
            elif planeZ == 2:
                if planeX in (1, NplaneX) and planeY in (1, NplaneY):   # corner
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_1_IntTag, 'mass', Col_1_mpul)
                    Column_1_Tags.append(ColTag)
                elif planeX not in (1, NplaneX) and planeY not in (1, NplaneY):  # interior
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_3_IntTag, 'mass', Col_3_mpul)
                    Column_3_Tags.append(ColTag)
                else:   # face
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_1_IntTag, 'mass', Col_1_mpul)
                    Column_1_Tags.append(ColTag)
            else:
                if planeX in (1, NplaneX) and planeY in (1, NplaneY):   # corner
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_1_IntTag, 'mass', Col_1_mpul)
                    Column_1_Tags.append(ColTag)
                elif planeX not in (1, NplaneX) and planeY not in (1, NplaneY):  # interior
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_2_IntTag, 'mass', Col_2_mpul)
                    Column_2_Tags.append(ColTag)
                else:   # face
                    ops.element('forceBeamColumn', ColTag, startNode, endNode, Col_TransfTag, Col_2_IntTag, 'mass', Col_2_mpul)
                    Column_2_Tags.append(ColTag)

Column_Tags = Column_1_Tags + Column_2_Tags + Column_3_Tags

# --------------------------------------------------------------------------------
# Gravity loads
# --------------------------------------------------------------------------------

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
P3 = gamma_conc * Beam_1_y * Beam_1_z      # Total Self weight of Beam N / mm
P5 = gamma_conc * Col_1_y * Col_1_z        # Total Self weight of Column 1 N / mm
P6 = gamma_conc * Col_2_y * Col_2_z        # Total Self weight of Column 2 N / mm
P7 = gamma_conc * Col_3_y * Col_3_z        # Total Self weight of Column 3 N / mm

def UDL_applier():
    # Beam X loading
    for tag in X_Beam_Tags:
        tag_str = str(tag).zfill(6)  # ensures it's 6 digits with leading zeros if needed
        starty = int(tag_str[2])
        if starty in (1, NplaneY):
            UDL = P12 + P3
        else:
            UDL = 2 * P12 + P3
        ops.eleLoad('-ele', tag, '-type', '-beamUniform', -UDL, 0.0, 0.0)
    # Beam Y Loading
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

    for tag in Column_3_Tags:
        UDL = P7
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

    plt.show()

# Plotter()