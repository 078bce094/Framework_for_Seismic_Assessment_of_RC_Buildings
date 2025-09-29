# source /Users/niraj/x86_env/bin/activate 
# Bays and stories -------------------------------------------------------------
NBayX = 6  # number of bays in X direction
NBayY = 2  # number of bays in Y direction
NBayZ = 3  # number of bays in Z direction || no of stories

bay_width_X = 2600. 
bay_width_Y = 2600.  # bay width Y >= bay width X
bay_width_Z = 3100.

slab_thickness = 115.0    # mm

rigidDiaphragm = 1   # 1 = yes, 0 = no  NOTE : Turn off (0) when doing moment curvature analysis 

# Section properties length in local y and z direction
# 1 type of Beam for each storey along X : Storey I, II, III = 1, 2, 3
Beam_1_y = 325.0
Beam_1_z = 230.0
Beam_1_Cover = 35.0

Beam_2_y = 325.0
Beam_2_z = 230.0
Beam_2_Cover = 35.0

Beam_3_y = 325.0
Beam_3_z = 230.0
Beam_3_Cover = 35.0

# 1 type of Beam for each storey along Y : Storey I, II, III = 1, 2, 3
Beam_4_y = 325.0
Beam_4_z = 230.0
Beam_4_Cover = 35.0

Beam_5_y = 325.0
Beam_5_z = 230.0
Beam_5_Cover = 35.0

Beam_6_y = 325.0
Beam_6_z = 230.0
Beam_6_Cover = 35.0

# 3 types of columns : 4-16, 4-12, 8-12 : 1, 2, 3
Col_1_y = 270.0
Col_1_z = 270.0
Col_1_Cover = 30.0

Col_2_y = 230.0
Col_2_z = 230.0
Col_2_Cover = 25.0

Col_3_y = 230.0
Col_3_z = 230.0
Col_3_Cover = 25.0