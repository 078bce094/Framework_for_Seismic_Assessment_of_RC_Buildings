# source /Users/niraj/x86_env/bin/activate 

import matplotlib.pyplot as plt
import numpy as np

def Elastic_site_spectra(Ch_T, Z, I):
    C_T = Ch_T * Z * I
    return C_T

def shape_factor(t, Ta, Tc, alpha, K):
    if t < Ta:
        Ch_T = 1 + (alpha - 1) * (t / Ta)  # for t < Ta
    elif Ta <= t <= Tc:
        Ch_T = alpha   # for Tc < t < Tc
    else:
        Ch_T = alpha * (K + (1 - K) * ((Tc / t) ** 2)) * ((Tc / t) ** 2) # for Tc < t < 6s

    return Ch_T

# For Soil Type A
Ta_A = 0.1  # s
Tc_A = 0.5  # s
alpha_A = 2.5
K_A = 1.8
Z_A = 0.35
I_A = 1

# For Soil Type B
Ta_B = 0.1  # s
Tc_B = 0.7  # s
alpha_B = 2.5
K_B = 1.8
Z_B = 0.35
I_B = 1

# For Soil Type C
Ta_C = 0.1  # s
Tc_C = 1.0  # s
alpha_C = 2.5
K_C = 1.8
Z_C = 0.35
I_C = 1

# For Soil Type D
Ta_D = 0.5  # s
Tc_D = 2.0  # s
alpha_D = 2.25
K_D = 0.8
Z_D = 0.35
I_D = 1

# Define time range for periods (0.01s to 6s)
t_values = np.arange(0., 6.0, 0.01)

Ch_T_values_A = [shape_factor(t, Ta_A, Tc_A, alpha_A, K_A) for t in t_values]
C_T_values_A = [Elastic_site_spectra(Ch_T, Z_A, I_A) for Ch_T in Ch_T_values_A]

Ch_T_values_B = [shape_factor(t, Ta_B, Tc_B, alpha_B, K_B) for t in t_values]
C_T_values_B = [Elastic_site_spectra(Ch_T, Z_B, I_B) for Ch_T in Ch_T_values_B]

Ch_T_values_C = [shape_factor(t, Ta_C, Tc_C, alpha_C, K_C) for t in t_values]
C_T_values_C = [Elastic_site_spectra(Ch_T, Z_C, I_C) for Ch_T in Ch_T_values_C]

Ch_T_values_D = [shape_factor(t, Ta_D, Tc_D, alpha_D, K_D) for t in t_values]
C_T_values_D = [Elastic_site_spectra(Ch_T, Z_D, I_D) for Ch_T in Ch_T_values_D]

# Plotting
plt.figure()
plt.plot(t_values, C_T_values_A, label='Soil Type A')
plt.plot(t_values, C_T_values_B, label='Soil Type B')
plt.plot(t_values, C_T_values_C, label='Soil Type C')
plt.plot(t_values, C_T_values_D, label='Soil Type D')
plt.title('Elastic Site Spectra for different Soil Types')
plt.xlabel('Time Period (s)')
plt.ylabel('Spectral Acceleration Coefficient (C_T)')
plt.grid(1)
plt.legend()
plt.tight_layout()
plt.show()

# with open("SoilTypeA_Elastic_Spectrum.txt", "w") as f:
#     for t, C_T in zip(t_values, C_T_values_A):
#         f.write(f"{t:.3f} {C_T:.4f}\n")
# with open("SoilTypeB_Elastic_Spectrum.txt", "w") as f:
#     for t, C_T in zip(t_values, C_T_values_B):
#         f.write(f"{t:.3f} {C_T:.4f}\n")
# with open("SoilTypeC_Elastic_Spectrum.txt", "w") as f:
#     for t, C_T in zip(t_values, C_T_values_C):
#         f.write(f"{t:.3f} {C_T:.4f}\n")
# with open("SoilTypeD_Elastic_Spectrum.txt", "w") as f:
#     for t, C_T in zip(t_values, C_T_values_D):
#         f.write(f"{t:.3f} {C_T:.4f}\n")