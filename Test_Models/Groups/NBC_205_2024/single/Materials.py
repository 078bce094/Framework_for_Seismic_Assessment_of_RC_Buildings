# source /Users/niraj/x86_env/bin/activate 
import openseespy.opensees as ops
import numpy as np
from dimensions import *

# ------------------------------------------------------------
# Material Properties
# ------------------------------------------------------------

gamma_conc = 2.5e-5       # N/mm^3 (for γ = 24 kN/m^3)
g = 9.81e3                # mm/s^2

unconfined_concrete_tag = 1     # unconfined concrete for cover
confined_concrete_tag = 2       # confined concrete for core
steel_tag = 3                   # reinforcement

# nominal concrete compressive strength
fc = -20.0              # CONCRETE Compressive Strength (+Tension, -Compression)
Ec = 5000 * (-fc)**0.5  # Concrete Elastic Modulus (the term in sqr root in Mpa)
Kfc = 1.75			    # ratio of confined to unconfined concrete strength
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
Fy_steel = 500.0    # Yield stress (MPa)
E0_steel = 2.0e5    # Initial modulus (MPa)
Bs = 0.01           # strain-hardening ratio
params_steel = [20,0.925,0.15]             # control the transition from elastic to plastic branches

# uniaxial materials
# uniaxialMaterial('Concrete02', matTag, fpc, epsc0, fpcu, epsU, lambda, ft, Ets)
ops.uniaxialMaterial("Concrete02", unconfined_concrete_tag, fc1U, eps1U, fc2U, eps2U, lambda_u, ftU, Ets) # unconfined concrete for cover
ops.uniaxialMaterial("Concrete02", confined_concrete_tag, fc1C, eps1C, fc2C, eps2C, lambda_u, ftC, Ets) # confined concrete for core
ops.uniaxialMaterial("Steel02", steel_tag, Fy_steel, E0_steel, Bs, *params_steel) 