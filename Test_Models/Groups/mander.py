# source /Users/niraj/x86_env/bin/activate 

import numpy as np

def calculate_confined_concrete(b, h, cover, s, tie_diameter, num_legs, f_co, f_yt):
    """
    Calculate confined concrete properties using Mander's model.

        b (float): Column width (mm)
        h (float): Column depth (mm)
        cover (float): Concrete cover (mm)
        s (float): Tie spacing (mm)
        tie_diameter (float): Diameter of ties (mm)
        num_legs (int): Number of tie legs
        f_co (float): Unconfined concrete strength (MPa)
        f_yt (float): Yield strength of ties (MPa)

    """

    # 1. Core dimensions
    d_c = h - 2 * cover  # Depth of confined core
    b_c = b - 2 * cover  # Width of confined core
    
    # 2. Tie area calculation
    A_sh = num_legs * (np.pi * (tie_diameter ** 2) / 4)  # mm²
    
    # 3. Confinement effectiveness factor (k_e)
    term1 = 1 - ((s - tie_diameter) / (2 * d_c))
    term2 = 1 - ((s - tie_diameter) / (2 * b_c))
    k_e = term1 * term2
    # k_e = 0.5

    if 0.4 < k_e < 0.6:
        print(f'{k_e} under range of 0.4 to 0.6')
    else:
        print(f'{k_e} not in range of 0.4 to 0.6')
        # k_e = 0.6

    # 4. Lateral confining stress (f'_l)
    f_l = k_e * (A_sh * f_yt) / (s * d_c)
    
    # 5. Confined concrete strength (Mander's equation)
    ratio = 7.94 * f_l / f_co
    f_cc = f_co * (-1.254 + 2.254 * np.sqrt(1 + ratio) - 2 * f_l / f_co)

    confinement_factor = f_cc / f_co
    
    # 6. Confined concrete strain
    eps_co = 0.002  # Default unconfined strain
    eps_cc = min(eps_co * (1 + 5 * (f_cc / f_co - 1)), 0.006)     # 0.004 - 0.006 in mander's model

    print(f_cc, eps_cc)

    confinement_factor_strain = eps_cc / eps_co
    
    return confinement_factor, confinement_factor_strain

# # Usage for CCP
# b = 230     # mm (column width)
# h = 230     # mm (column depth)
# cover = 23  # mm
# s = 125     # mm (tie spacing)
# tie_diameter = 6  # mm
# num_legs = 2
# f_co = 15   # MPa
# f_yt = 415  # MPa

# # Usage for NBC 205:1994
# b = 270     # mm (column width)
# h = 270     # mm (column depth)
# cover = 30  # mm
# s = 125     # mm (tie spacing)
# tie_diameter = 6  # mm
# num_legs = 2
# f_co = 15   # MPa
# f_yt = 415  # MPa

# # Usage for NBC 205:2012
# b = 300     # mm (column width)
# h = 300     # mm (column depth)
# cover = 30  # mm
# s = 125     # mm (tie spacing)
# tie_diameter = 8  # mm
# num_legs = 2
# f_co = 20   # MPa
# f_yt = 415  # MPa

# # Usage for NBC 105:2020
# b = 320     # mm (column width)
# h = 320     # mm (column depth)
# cover = 35  # mm
# s = 125     # mm (tie spacing)
# tie_diameter = 8  # mm
# num_legs = 4
# f_co = 25   # MPa
# f_yt = 500  # MPa

# Usage for NBC 205:2024
b = 350     # mm (column width)
h = 350     # mm (column depth)
cover = 40  # mm
s = 125     # mm (tie spacing)
tie_diameter = 8  # mm
num_legs = 4
f_co = 20   # MPa
f_yt = 500  # MPa

K_fc, K_eps = calculate_confined_concrete(b, h, cover, s, tie_diameter, num_legs, f_co, f_yt)

print(f'Confinement Factor: {K_fc}')
print(f'Confinement Factor Strain: {K_eps}')