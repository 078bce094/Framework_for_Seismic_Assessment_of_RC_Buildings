# source /Users/niraj/x86_env/bin/activate
import openseespy.opensees as ops
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation

ops.wipe()  
from Materials import * 

# ------------------------------------------------------------
# Testing Materials
# ------------------------------------------------------------

# Concrete02 material test

concrete_tag = [unconfined_concrete_tag, confined_concrete_tag]

for concrete_tag in concrete_tag:
    ops.testUniaxialMaterial(concrete_tag)

    # Define strain history
    strain_values_concrete = np.concatenate([
        np.linspace(0, 0.002 * 1.5, 100),   # Tension increase 0.002 by 20%
        np.linspace(0, eps2U, 100),         # Compression
        np.linspace(eps2U, 0, 100),         # Unloading to zero
        np.linspace(0, eps2U * 1.5, 100)    # Reloading to 20% beyond ultimate
    ])

    stress_concrete = []
    strain_concrete = []

    # Obtain stress values for each strain value
    for eps in strain_values_concrete:
        ops.setStrain(eps)
        stress = ops.getStress()
        strain = ops.getStrain()
        stress_concrete.append(stress)
        strain_concrete.append(strain)

    # Plotting
    plt.figure()
    plt.plot(strain_concrete, stress_concrete)
    plt.title(f'Concrete02 Stress-Strain Curve {concrete_tag}')
    plt.xlabel('Strain')
    plt.ylabel('Stress')
    plt.axhline(0, color='red', linewidth=0.8)  # horizontal axis
    plt.axvline(0, color='red', linewidth=0.8)  # vertical axis
    plt.grid(True)
    plt.tight_layout()

# Steel02 material test clear model using ops.wipe() in case of malfunction

ops.testUniaxialMaterial(steel_tag)

# Define strain history
yield_strain = Fy_steel / E0_steel 
strain_values_steel = np.concatenate([
    np.linspace(0, yield_strain * 10, 100),                   # From zero go up to 10 times yield strain
    np.linspace(yield_strain * 10, -yield_strain * 10, 200),  # From there go to -10 times yield strain
    np.linspace(-yield_strain * 10, yield_strain * 10, 200),  # From there go to 10 times yield strain
    np.linspace(yield_strain * 10, 0, 100)                    # From there go to zero
])

stress_steel = []
strain_steel = []

# Obtain stress values for each strain value
for eps in strain_values_steel:
    ops.setStrain(eps)
    stress = ops.getStress()
    strain = ops.getStrain()
    stress_steel.append(stress)
    strain_steel.append(strain)

# Plotting
plt.figure()
plt.plot(strain_steel, stress_steel)
plt.title('Steel02 Stress-Strain Curve')
plt.xlabel('Strain')    
plt.ylabel('Stress')
plt.axhline(0, color='red', linewidth=0.8)  # horizontal axis
plt.axvline(0, color='red', linewidth=0.8)  # vertical axis
plt.grid(True)
plt.tight_layout()
plt.show()

# # Hysteretic material test clear model using ops.wipe() in case of malfunction

hys_Mat_tag = [hys_Mat_tag_X, hys_Mat_tag_Y]

for Mat_tag in hys_Mat_tag:
    ops.testUniaxialMaterial(Mat_tag)

    # Define strain history
    if Mat_tag == hys_Mat_tag_X:
        strain_values_hys = np.concatenate([
            np.linspace(0, tdeltarX * 1.2, 100),
            np.linspace(0, cdeltarX * 1.2, 100)])
    else:
        strain_values_hys = np.concatenate([
        np.linspace(0, tdeltarY * 1.2, 100),
        np.linspace(0, cdeltarY * 1.2, 100)])

    stress_hys = []
    strain_hys = []

    # Obtain stress values for each strain value
    for eps in strain_values_hys:
        ops.setStrain(eps)
        stress = ops.getStress()
        strain = ops.getStrain()
        stress_hys.append(stress)
        strain_hys.append(strain)

    # Plotting
    plt.figure()
    plt.plot(strain_hys, stress_hys)
    plt.title('Hysteretic Material Stress-Strain Curve')
    plt.xlabel('Strain')    
    plt.ylabel('Stress')
    plt.axhline(0, color='red', linewidth=0.8)  # horizontal axis
    plt.axvline(0, color='red', linewidth=0.8)  # vertical axis
    plt.grid(True)
    plt.tight_layout()
    plt.show()




















# Animate ---------------------------------------------

# fig, ax = plt.subplots()
# ax.set_xlim(min(strain_concrete), max(strain_concrete))
# ax.set_ylim(min(stress_concrete) * 1.1, max(stress_concrete) * 1.1)
# ax.set_title('Concrete02 Stress-Strain Curve')
# ax.set_xlabel('Strain')
# ax.set_ylabel('Stress')
# ax.axhline(0, color='red', linewidth=0.8)  # horizontal axis
# ax.axvline(0, color='red', linewidth=0.8)  # vertical axis
# ax.grid(True)

# line, = ax.plot([], [], lw=2)  # initially empty

# def animate(i):
#     line.set_data(strain_concrete[:i], stress_concrete[:i])
#     return line,

# ani = animation.FuncAnimation(fig, animate, frames=len(strain_concrete), interval=10, blit=True)

# plt.tight_layout()
# plt.show()

# fig, ax = plt.subplots()
# ax.set_xlim(min(strain_steel), max(strain_steel))
# ax.set_ylim(min(stress_steel) * 1.1, max(stress_steel) * 1.1)
# ax.set_title('Steel02 Stress-Strain Curve')
# ax.set_xlabel('Strain')
# ax.set_ylabel('Stress')
# ax.axhline(0, color='red', linewidth=0.8)  # horizontal axis
# ax.axvline(0, color='red', linewidth=0.8)  # vertical axis
# ax.grid(True)

# line, = ax.plot([], [], lw=2)

# def animate(i):
#     line.set_data(strain_steel[:i], stress_steel[:i])
#     return line,

# ani = animation.FuncAnimation(fig, animate, frames=len(strain_steel), interval=10, blit=True)

# plt.tight_layout()
# plt.show()