import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# ==============================
# USER INPUTS
# ==============================
input_csv = '/Users/niraj/Downloads/Projects/Project_Geo_Lab/Verification_Model/NBC_205_2024_results.csv' 
output_csv = "fragility_output_NBC_205_2024.csv" 

im_column = "PGA (g)"        # Intensity Measure
edp_column = "MIDR (%)"      # Engineering Demand Parameter

# Define Limit States (MIDR values in %)
limit_states = {
    "IO": 1.0, 
    "LS": 2.0, 
    "CP": 4.0
}

# ==============================
# 1. READ DATA
# ==============================
df = pd.read_csv(input_csv)

# ==============================
# 2. INTERPOLATION FUNCTION
# ==============================
def get_interpolated_exceedance(df, edp_col, im_col, threshold):
    """
    Finds the exact IM value where the EDP crosses the threshold for each RSN.
    """
    exceedance_ims = []

    for rsn, group in df.groupby("RSN"):
        # Sort by IM to ensure interpolation works correctly
        group = group.sort_values(im_col)
        
        # Only proceed if the ground motion actually exceeded the threshold
        if group[edp_col].max() >= threshold:
            # np.interp(target_x, x_values, y_values)
            # We want the IM (y) when EDP (x) reaches the threshold
            exact_im = np.interp(threshold, group[edp_col], group[im_col])
            exceedance_ims.append(exact_im)
            
    return np.array(exceedance_ims)

# Dictionary to store the results for each limit state
exceedance_data = {}

for ls_name, threshold in limit_states.items():
    exceedance_data[ls_name] = get_interpolated_exceedance(df, edp_column, im_column, threshold)

# ==============================
# 3. FIT LOGNORMAL PARAMETERS
# ==============================
def fit_lognormal(im_values):
    if len(im_values) == 0:
        return np.nan, np.nan
    log_im = np.log(im_values)
    mu = np.exp(np.mean(log_im))       # median (theta)
    beta = np.std(log_im, ddof=1)      # dispersion (beta)
    return mu, beta

params = {}
print("Lognormal Parameters (Interpolated):")
for ls_name, ims in exceedance_data.items():
    mu, beta = fit_lognormal(ims)
    params[ls_name] = (mu, beta)
    print(f"{ls_name}: μ = {mu:.3f}, β = {beta:.3f} (based on {len(ims)} records)")

# ==============================
# 4. GENERATE FRAGILITY CURVES
# ==============================
im_min = 0
im_max = 2.0
im_range = np.linspace(im_min, im_max, 1000)

def fragility_function(im, mu, beta):
    # Using small epsilon to avoid log(0)
    return norm.cdf((np.log(np.maximum(im, 1e-6)) - np.log(mu)) / beta)

curves = {}
for ls_name, (mu, beta) in params.items():
    curves[ls_name] = fragility_function(im_range, mu, beta)

# ==============================
# 5. EXPORT FRAGILITY DATA
# ==============================
export_dict = {im_column: im_range}
for ls_name, poe in curves.items():
    export_dict[f"PoE({ls_name})"] = poe

fragility_df = pd.DataFrame(export_dict)
fragility_df.to_csv(output_csv, index=False)
print(f"\nFragility data exported to: {output_csv}")

# ==============================
# 6. PLOT FRAGILITY CURVES
# ==============================
plt.figure(figsize=(10, 6))

colors = {"IO": "blue", "LS": "green", "CP": "red"}

for ls_name, poe in curves.items():
    plt.plot(im_range, poe, label=f"{ls_name} (Threshold: {limit_states[ls_name]}%)", 
             linewidth=2, color=colors.get(ls_name))

plt.xlabel(f"{im_column}")
plt.ylabel("Probability of Exceedance (P(D > C))")
plt.title("Fragility Curves")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.xlim(0, im_max)
plt.ylim(0, 1)

plt.tight_layout()
plt.show()