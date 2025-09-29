# Bays and stories -------------------------------------------------------------
NBayX = 2  # number of bays in X direction
NBayY = 3  # number of bays in Y direction
NBayZ = 3  # number of bays in Z direction || no of stories

bay_width_X = 3600. 
bay_width_Y = 3600.  # bay width Y >= bay width X
bay_width_Z = 3000.

slab_thickness = 115.0    # mm

rigidDiaphragm = 0   # 1 = yes, 0 = no  NOTE : Turn off (0) when doing moment curvature analysis 
infillIncusion = 0   # 0 = no infills, 1 = infill in X direction only, 2 = infill in Y direction only, 3 = infill in both X and Y

# Section properties length in local y and z direction
Beam_1_y = 350.0
Beam_1_z = 230.0
Beam_1_Cover = 35.0

Beam_2_y = 350.0
Beam_2_z = 230.0
Beam_2_Cover = 35.0

Col_1_y = 230.0
Col_1_z = 230.0
Col_1_Cover = 23.0

Col_2_y = 230.0
Col_2_z = 230.0
Col_2_Cover = 23.0