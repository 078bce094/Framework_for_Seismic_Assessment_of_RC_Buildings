# source /Users/niraj/x86_env/bin/activate
import openseespy.opensees as ops
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
import numpy as np

ops.wipe()  

steel_tag_415 = 3
steel_tag_500 = 4

# STEEL parameters for Steel02
Fy_steel_415 = 415.0    # Yield stress (MPa)
Fy_steel_500 = 500.0    # Yield stress (MPa)
E0_steel = 2.0e5    # Initial modulus (MPa)
Bs = 0.01           # strain-hardening ratio
params_steel = [20,0.925,0.15]             # control the transition from elastic to plastic branches

ops.uniaxialMaterial("Steel02", steel_tag_415, Fy_steel_415, E0_steel, Bs, *params_steel) 
ops.uniaxialMaterial("Steel02", steel_tag_500, Fy_steel_500, E0_steel, Bs, *params_steel) 

# Steel02 material test clear model using ops.wipe() in case of malfunction
steel_materials = [steel_tag_415, steel_tag_500]

# Define strain history
strain_values_steel = np.concatenate([
    np.linspace(0, 0.01, 100),                   
    np.linspace(0.01, -0.002, 100),  
    np.linspace(-0.002, 0.03, 200),  
    np.linspace(0.03, -0.002, 100),                  
    np.linspace(-0.002, 0.04, 100),                  
    np.linspace(0.04, -0.002, 100),                  
    np.linspace(-0.002, 0.06, 100)                  
])

stress_steel_415 = []
strain_steel_415 = []

stress_steel_500 = []
strain_steel_500 = []

ops.testUniaxialMaterial(steel_tag_415)

# Obtain stress values for each strain value
for eps in strain_values_steel:
    ops.setStrain(eps)
    stress = ops.getStress()
    strain = ops.getStrain()
    stress_steel_415.append(stress)
    strain_steel_415.append(strain)

ops.testUniaxialMaterial(steel_tag_500)

# Obtain stress values for each strain value
for eps in strain_values_steel:
    ops.setStrain(eps)
    stress = ops.getStress()
    strain = ops.getStrain()
    stress_steel_500.append(stress)
    strain_steel_500.append(strain)

# Plotting both Steel02 Stress-Strain Curves
plt.figure(figsize=(8, 6))
plt.plot(strain_steel_415, stress_steel_415, label='Steel 415')
plt.plot(strain_steel_500, stress_steel_500, label='Steel 500')

# plt.title('Stress-Strain Curve for Steel02 Material')
plt.xlabel('Strain')
plt.ylabel('Stress (MPa)')

plt.xlim(-0.01, 0.06)
plt.ylim(-550.0, 700.0)

plt.legend()
plt.grid(True, which='both', color='grey', linewidth=0.25)
plt.tick_params(direction='in', top=True, right=True)

plt.axhline(0, color='black', linewidth=0.85)
plt.axvline(0, color='black', linewidth=0.85)

plt.tight_layout()
plt.show()

# # Plotting
# plt.figure()
# plt.plot(strain_steel, stress_steel)
# plt.title('Steel02 Stress-Strain Curve')
# plt.xlabel('Strain')    
# plt.ylabel('Stress')
# plt.axhline(0, color='red', linewidth=0.8)  # horizontal axis
# plt.axvline(0, color='red', linewidth=0.8)  # vertical axis
# plt.grid(True)
# plt.tight_layout()
# plt.show()