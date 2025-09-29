import openseespy.opensees as ops
import numpy as np
from dimensions import *

# ------------------------------------------------------------
# Material Properties
# ------------------------------------------------------------

gamma_conc = 2.4e-5       # N/mm^3 (for γ = 24 kN/m^3)
g = 9.81e3                # mm/s^2

unconfined_concrete_tag = 1     # unconfined concrete for cover
confined_concrete_tag = 2       # confined concrete for core
steel_tag = 3                   # reinforcement

# nominal concrete compressive strength
fc = -25.0              # CONCRETE Compressive Strength (+Tension, -Compression)
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
ftC = 1.3 * 3.13  # tensile strength +tension
ftU = 3.13  # tensile strength +tension
Ets = ftU / 0.002   # tension softening stiffness

# STEEL parameters for Steel02
Fy_steel = 415.0    # Yield stress (MPa)
E0_steel = 2.0e5    # Initial modulus (MPa)
Bs = 0.01           # strain-hardening ratio
params_steel = [20,0.925,0.15]             # control the transition from elastic to plastic branches

# uniaxial materials
# uniaxialMaterial('Concrete02', matTag, fpc, epsc0, fpcu, epsU, lambda, ft, Ets)
ops.uniaxialMaterial("Concrete02", unconfined_concrete_tag, fc1U, eps1U, fc2U, eps2U, lambda_u, ftU, Ets) # unconfined concrete for cover
ops.uniaxialMaterial("Concrete02", confined_concrete_tag, fc1C, eps1C, fc2C, eps2C, lambda_u, ftC, Ets) # confined concrete for core
ops.uniaxialMaterial("Steel02", steel_tag, Fy_steel, E0_steel, Bs, *params_steel) 

# --------------------------------------------------------------------------------------------------------

hys_Mat_tag_X = 4
hys_Mat_tag_Y = 5

def calculate_strut_width(hys_Mat_tag, dim_perp, dim_along, bayWidth_along):
    h_col = bay_width_Z - Beam_1_y
    h_inf = bay_width_Z - Beam_1_y
    E_fe = Ec
    E_me = 2300.0 # Mpa Modulus of elasticity of masonary
    I_col = dim_perp * (dim_along ** 3) / 12
    L_inf = bayWidth_along - dim_along
    t_inf = 230.0 # mm thickness of masonary wall

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

tdeltarX, cdeltarX, strut_areaX = calculate_strut_width(hys_Mat_tag_X, Col_1_y, Col_1_z, bay_width_X)    
tdeltarY, cdeltarY, strut_areaY = calculate_strut_width(hys_Mat_tag_Y, Col_1_z, Col_1_y, bay_width_Y)    