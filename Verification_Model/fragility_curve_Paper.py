import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm

# ==============================
# USER INPUTS
# ==============================
output_csv = "fragility_output_Paper.csv"   # where to save the data

# Define lognormal parameters (mu = median, beta = dispersion)
# from the given table
damage_state_params = {
    "IO": (0.29, 0.38),
    "LS": (0.63, 0.70),
    "CP": (1.29, 0.83),
}

# Intensity measure range
im_min = 0.0
im_max = 2.0
im_range = np.linspace(im_min, im_max, 1000)

# ==============================
# FRAGILITY FUNCTION
# ==============================
def fragility_function(im, mu, beta):
    """Lognormal CDF for probability of exceedance."""
    # avoid log(0) by using a small epsilon
    return norm.cdf((np.log(np.maximum(im, 1e-6)) - np.log(mu)) / beta)

# ==============================
# GENERATE CURVES
# ==============================
curves = {}
for ls_name, (mu, beta) in damage_state_params.items():
    curves[ls_name] = fragility_function(im_range, mu, beta)

# ==============================
# EXPORT FRAGILITY DATA
# ==============================
export_dict = {"IM": im_range}
for ls_name, poe in curves.items():
    export_dict[f"PoE({ls_name})"] = poe

fragility_df = pd.DataFrame(export_dict)
fragility_df.to_csv(output_csv, index=False)
print(f"Fragility data exported to: {output_csv}")

# ==============================
# PLOT FRAGILITY CURVES
# ==============================
plt.figure(figsize=(10, 6))

colors = {"IO": "blue", "LS": "green", "CP": "red"}

for ls_name, poe in curves.items():
    plt.plot(im_range, poe, label=f"{ls_name} (μ={damage_state_params[ls_name][0]:.2f}, ζ={damage_state_params[ls_name][1]:.2f})", 
             linewidth=2, color=colors.get(ls_name))

plt.xlabel("PGA (g)")   # or whatever IM you are using
plt.ylabel("Probability of Exceedance (P(D > C))")
plt.title("Fragility Curves from Experimental Data")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.xlim(im_min, im_max)
plt.ylim(0, 1)
plt.tight_layout()
plt.show()