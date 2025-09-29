# source /Users/niraj/x86_env/bin/activate 
# Bays and stories -------------------------------------------------------------   sample no 83
NBayX = 6  # number of bays in X direction
NBayY = 2  # number of bays in Y direction
NBayZ = 3  # number of bays in Z direction || no of stories

bay_width_X = 3000. 
bay_width_Y = 3000.  # bay width Y >= bay width X
bay_width_Z = 3100.

slab_thickness = 125.0    # mm

rigidDiaphragm = 0   # 1 = yes, 0 = no  NOTE : Turn off (0) when doing moment curvature analysis 

# Section properties length in local y and z direction
# 1 type of Beam for each storey along X : Storey I, II, III = 1, 2, 3
Beam_1_y = 355.0
Beam_1_z = 250.0
Beam_1_Cover = 25.0

Beam_2_y = 355.0
Beam_2_z = 250.0
Beam_2_Cover = 25.0

Beam_3_y = 355.0
Beam_3_z = 250.0
Beam_3_Cover = 25.0

# 1 type of Beam for each storey along Y : Storey I, II, III = 1, 2, 3
Beam_4_y = 355.0
Beam_4_z = 250.0
Beam_4_Cover = 25.0

Beam_5_y = 355.0
Beam_5_z = 250.0
Beam_5_Cover = 25.0

Beam_6_y = 355.0
Beam_6_z = 250.0
Beam_6_Cover = 25.0

# 4 types of columns : 8-20, 4-20 + 4-16, 8-16, 4-16 + 4-12 : 1, 2, 3, 4
Col_1_y = 350.0
Col_1_z = 350.0
Col_1_Cover = 40.0

Col_2_y = 350.0
Col_2_z = 350.0
Col_2_Cover = 40.0

Col_3_y = 350.0
Col_3_z = 350.0
Col_3_Cover = 40.0

Col_4_y = 350.0
Col_4_z = 350.0
Col_4_Cover = 40.0