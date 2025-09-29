# source /Users/niraj/x86_env/bin/activate 

import numpy as np
from scipy.fft import fft, fftfreq

def calculate_mean_period(accel_data, dt):
    """
    Calculates the Mean Period (Tm) of a ground motion.

    Args:
        accel_data (np.ndarray): Array of acceleration time series.
        dt (float): Time step of the acceleration data.

    Returns:
        float: Mean Period (Tm) in seconds.
    """
    n = len(accel_data)
    if n == 0:
        return np.nan

    # Compute Fourier amplitudes and frequencies
    # Using rfft for real input, which is more efficient
    fourier_amps = np.abs(fft(accel_data))[:n//2] # Take only positive frequency components
    frequencies = fftfreq(n, d=dt)[:n//2]        # Corresponding frequencies

    # Filter for the typical frequency range (0.25 Hz to 20 Hz)
    # Ensure Nyquist frequency is respected if it's lower than 20 Hz
    nyquist_freq = 0.5 / dt
    lower_freq_bound = 0.25
    upper_freq_bound = min(20.0, nyquist_freq * 0.99) # Avoid being exactly at Nyquist

    valid_indices = np.where((frequencies > lower_freq_bound) & (frequencies < upper_freq_bound))[0]

    if len(valid_indices) == 0:
        # Fallback if no frequencies in range (e.g., very short signal or strange dt)
        # This might indicate an issue or require different bounds
        # For robustness, could use all available positive frequencies if this happens
        # For now, let's try to use available positive frequencies excluding DC if no valid indices
        alt_indices = np.where(frequencies > 1e-6)[0] # Exclude DC component
        if len(alt_indices) == 0:
            return np.nan
        # print(f"Warning: No frequencies in range ({lower_freq_bound:.2f}Hz - {upper_freq_bound:.2f}Hz). Using available positive frequencies.")
        valid_indices = alt_indices


    Ci_sq = fourier_amps[valid_indices]**2
    fi = frequencies[valid_indices]
    omega_i = 2 * np.pi * fi

    # Avoid division by zero for omega_i if any frequency is zero (though filtered)
    # However, fi > lower_freq_bound > 0, so omega_i will be > 0
    
    sum_Ci_sq_div_omega = np.sum(Ci_sq / omega_i)
    sum_Ci_sq = np.sum(Ci_sq)

    if sum_Ci_sq == 0:
        return np.nan # Avoid division by zero if signal has no energy in the band

    Tm = 2 * np.pi * (sum_Ci_sq_div_omega / sum_Ci_sq)
    return Tm

eq_data_dir = "/Users/niraj/Documents/GM"

for variable in [139, 334, 410, 496, 949, 960, 962,
                 990, 998, 1045, 1052, 2476, 2510, 2990, 
                 3282, 3319, 3749, 4199, 4455, 4458, 4863, 
                 5117, 5259, 5470, 5665, 5676, 5814, 32852]:
    
    GM_input_file = f"{eq_data_dir}/RSN_{variable}.txt"

    # Initialize list for load_factors
    load_factors = []

    # Read and parse the file
    with open(GM_input_file, "r") as f:
        lines = f.readlines()

    # Extract time step from the line containing "Time Step"
    for line in lines:
        if "Time Step" in line:
            dt = float(line.strip().split(":")[1].split()[0])
            break

    # Skip lines until you reach the actual data
    data_start_index = next(i for i, line in enumerate(lines) if "Time(sec)" in line) + 1

    # Read acceleration values
    for line in lines[data_start_index:]:
        if line.strip():  # skip empty lines
            parts = line.strip().split()
            if len(parts) >= 2:
                acc = float(parts[1])
                load_factors.append(acc)

    # Final time
    tFinal = dt * len(load_factors)
    print("RSN:", variable)
    print("dt:", dt)
    print("tFinal:", tFinal)
    print("Number of points:", len(load_factors))

    tm_value = calculate_mean_period(load_factors, dt)
    print(f"Mean Period (Tm): {tm_value:.4f} s")

    print("----------------------")