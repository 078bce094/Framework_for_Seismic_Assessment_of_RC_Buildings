# source /Users/niraj/x86_env/bin/activate 
# Bays and stories -------------------------------------------------------------   sample no 116
NBayX = 4  # number of bays in X direction
NBayY = 2  # number of bays in Y direction
NBayZ = 4  # number of bays in Z direction || no of stories

bay_width_X = 4500. 
bay_width_Y = 2600.  # bay width Y >= bay width X
bay_width_Z = 3200.

slab_thickness = 115.0    # mm

rigidDiaphragm = 0   # 1 = yes, 0 = no  NOTE : Turn off (0) when doing moment curvature analysis 
infillIncusion = 2   # 0 = no infills, 1 = infill in X direction only, 2 = infill in Y direction only, 3 = infill in both X and Y

# Section properties length in local y and z direction
# 1 type of Beam for each storey along X : Storey I, II = 1 : Storey III, IV = 2
Beam_1_y = 325.0
Beam_1_z = 230.0
Beam_1_Cover = 30.0

# 4 types of columns : 4-16 + 2-12, 4-12 : 1, 2
Col_1_y = 230.0
Col_1_z = 230.0
Col_1_Cover = 23.0

Col_2_y = 230.0
Col_2_z = 230.0
Col_2_Cover = 23.0