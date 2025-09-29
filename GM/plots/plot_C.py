# source /Users/niraj/x86_env/bin/activate 

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
from scipy.signal import detrend
from scipy.interpolate import interp1d
import os

# ========== SETTINGS ==========
original_dir = "/Users/niraj/Documents/GM/C/original_C"
matched_dir = "/Users/niraj/Documents/GM/C"
target_spectrum_path = "/Users/niraj/Documents/GM/target_spectrum/SoilTypeC_Elastic_Spectrum.txt"
damping = 0.05
periods = np.arange(0.01, 4.01, 0.01)

# ========== READ AT2 ==========
def read_at2(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    dt_line = next(line for line in lines if "DT=" in line)
    dt = float(dt_line.split('=')[2].split()[0])
    data_lines = lines[4:]
    data = ' '.join(data_lines).split()
    accel = np.array([float(val) for val in data])
    return accel, dt

# ========== READ MATCHED TXT ==========
def read_matched(file_path):
    data = np.loadtxt(file_path, skiprows=5)
    accel = data[:, 1]
    dt = data[1, 0] - data[0, 0]
    return accel, dt

# ========== READ TARGET SPECTRUM ==========
def read_target_spectrum(path):
    T, Sa = np.loadtxt(path, unpack=True)
    return T, Sa



def compute_response_spectrum(accel, dt, periods, damping=0.05):
    """
    Computes the response spectrum of a ground motion using the Newmark-Beta method.
    This implementation uses the unconditionally stable average acceleration scheme.

    Args:
        accel (np.ndarray): Array of ground acceleration values (in g).
        dt (float): Time step of the acceleration record.
        periods (np.ndarray): Array of periods for which to compute the spectral acceleration.
        damping (float): Damping ratio (e.g., 0.05 for 5%).

    Returns:
        np.ndarray: Array of spectral acceleration values (Sa) in g.
    """
    # Newmark-Beta method parameters for the unconditionally stable
    # constant average acceleration method.
    gamma = 0.5
    beta = 0.25

    # Detrend the acceleration time series to remove baseline drift
    accel = detrend(accel)
    
    Sa = []
    for T in periods:
        if T == 0:
            Sa.append(np.max(np.abs(accel)))
            continue

        omega = 2 * np.pi / T
        m = 1.0
        k = omega**2 * m
        c = 2 * damping * omega * m

        # Initialize displacement, velocity, and acceleration
        u, v, a = 0.0, 0.0, 0.0
        # Set initial acceleration: a_0 = (-m*ag_0 - c*v_0 - k*u_0) / m
        a = -accel[0] 
        
        u_hist = []

        # Pre-calculate constants for the integration loop to improve efficiency
        a1 = (m / (beta * dt**2)) + (c * gamma / (beta * dt))
        a2 = (m / (beta * dt)) + c * (gamma / beta - 1)
        a3 = m * (1 / (2 * beta) - 1) + c * dt * (gamma / (2 * beta) - 1)
        
        k_eff = k + a1 # Effective stiffness

        for ag in accel:
            # Calculate effective force at the current step
            p_eff = -m * ag + a1 * u + a2 * v + a3 * a
            
            # Solve for displacement at the current step
            u_new = p_eff / k_eff
            
            # Update acceleration and velocity for the current step based on u_new
            a_new = (u_new - u) / (beta * dt**2) - v / (beta * dt) - (1 / (2 * beta) - 1) * a
            v_new = v + a * (1 - gamma) * dt + a_new * gamma * dt
            
            # Update state for the next iteration
            u, v, a = u_new, v_new, a_new
            
            u_hist.append(u)

        umax = max(abs(np.array(u_hist)))
        # Append Pseudo-Spectral Acceleration (PSA), which is standard practice
        Sa.append(omega**2 * umax)
        
    return np.array(Sa)

# ========== LOAD ALL FILES ==========
original_files = sorted([f for f in os.listdir(original_dir) if f.endswith(".AT2")])
matched_files = sorted([f for f in os.listdir(matched_dir) if f.endswith(".txt") and f.startswith("RSN_")])

Sa_original_all = []
Sa_matched_all = []

print("--------------------------------------------------------------------------")

print("Computing response spectra for original ground motions...")
for file in original_files:
    accel, dt = read_at2(os.path.join(original_dir, file))
    Sa = compute_response_spectrum(accel, dt, periods, damping)
    Sa_original_all.append(Sa)

print("--------------------------------------------------------------------------")

print("Computing response spectra for matched ground motions...")
for file in matched_files:
    accel, dt = read_matched(os.path.join(matched_dir, file))
    Sa = compute_response_spectrum(accel, dt, periods, damping)
    Sa_matched_all.append(Sa)

Sa_original_all = np.array(Sa_original_all)
Sa_matched_all = np.array(Sa_matched_all)
mean_orig = np.mean(Sa_original_all, axis=0)
mean_match = np.mean(Sa_matched_all, axis=0)

# ========== LOAD TARGET ==========
T_target, Sa_target = read_target_spectrum(target_spectrum_path)
# target_interp = interp1d(T_target, Sa_target, kind='linear', fill_value='extrapolate')
# Sa_target_interp = target_interp(periods)

# ========== PLOTTING ==========
fig, axs = plt.subplots(1, 2, figsize=(14, 6))

# Plot Original
for Sa in Sa_original_all:
    axs[0].plot(periods, Sa, color='gray', alpha = 0.5, linewidth = 0.9)
axs[0].plot(T_target, Sa_target, color='red', lw = 1.5, label='Target spectrum Soil Type C')
# axs[0].plot(periods, Sa_target_interp, color='red', lw = 1.5, label='Target spectrum Soil Type A')
axs[0].plot(periods, mean_orig, color='green', lw = 1.2, label='Mean spectrum original')
axs[0].set_xlabel('Period (sec)')
axs[0].set_ylabel('Spectral Acceleration (g)')
axs[0].legend()

# Plot (b) Matched
for Sa in Sa_matched_all:
    axs[1].plot(periods, Sa, color='gray', alpha = 0.5, linewidth = 0.9)
axs[1].plot(T_target, Sa_target, color='red', lw = 1.5, label='Target spectrum Soil Type C')
# axs[1].plot(periods, Sa_target_interp, color='red', lw = 1.5, label='Target spectrum Soil Type A')
axs[1].plot(periods, mean_match, color='green', lw = 1.2, label='Mean spectrum matched')
axs[1].set_xlabel('Period (sec)')
axs[1].set_ylabel('Spectral Acceleration (g)')
axs[1].legend()


global_max_y_buffered = 1.2
max_period = 4

# Adjust axis spine positions and limits
for ax in axs:
    ax.spines['left'].set_position(('data', 0))
    ax.spines['bottom'].set_position(('data', 0))
    
    # Align the period 4 to the right line by setting the right xlim explicitly
    ax.set_xlim(left=0, right=max_period) # Set right to the maximum period value
    
    # Make the y axis range same on both axis
    ax.set_ylim(bottom=0, top=global_max_y_buffered)

    # Set bounds for the spines so they do not extend beyond the data limits
    ax.spines['left'].set_bounds(0, global_max_y_buffered) # Use buffered max_y
    ax.spines['bottom'].set_bounds(0, max_period) # Use max_period for x-axis bounds

    # If you want the right spine to align with the end of the x-axis
    ax.spines['right'].set_position(('data', max_period)) # Align right spine with max_period
    ax.spines['right'].set_bounds(0, global_max_y_buffered) # Set its bounds
    ax.spines['top'].set_position(('data', global_max_y_buffered)) # Align top spine with max_y
    ax.spines['top'].set_bounds(0, max_period) # Set its bounds

for ax in axs:
    ax.tick_params(direction='in', top=True, right=True)
    legend = ax.legend(frameon=False) # Keep legend frame off

plt.tight_layout()
plt.show()

print("--------------------------------------------------------------------------")