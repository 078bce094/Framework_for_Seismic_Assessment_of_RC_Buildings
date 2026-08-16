import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.lines import Line2D
rcParams['font.family'] = 'Times New Roman'

df = pd.read_csv('/Users/niraj/Downloads/Projects/Project_Geo_Lab/Verification_Model/Combined.csv')

pga = df["PGA (g)"]

columns = {
    "IO CCP": "PoE (IO CCP)",
    "IO Experimental": "PoE (IO Experimental)",
    "IO NBC 205 2024": "PoE (IO NBC 205 2024)",
    
    "LS CCP": "PoE (LS CCP)",
    "LS Experimental": "PoE (LS Experimental)",
    "LS NBC 205 2024": "PoE (LS NBC 205 2024)",
    
    "CP CCP": "PoE (CP CCP)",
    "CP Experimental": "PoE (CP Experimental)",
    "CP NBC 205 2024": "PoE (CP NBC 205 2024)",
}

plt.figure(figsize=(10, 7))

plt.plot(pga, df[columns["IO CCP"]], color="tab:blue", linewidth=1.75, linestyle=(0, (5, 2)))
plt.plot(pga, df[columns["IO Experimental"]], color="tab:orange", linewidth=1.75, linestyle=(0, (5, 2)))
plt.plot(pga, df[columns["IO NBC 205 2024"]], color="tab:green", linewidth=1.75, linestyle=(0, (5, 2)))

plt.plot(pga, df[columns["LS CCP"]], color="tab:blue", linewidth=1.75, label="CCP")
plt.plot(pga, df[columns["LS Experimental"]], color="tab:orange", linewidth=1.75, label="Post 2015 earthquake Observational")
plt.plot(pga, df[columns["LS NBC 205 2024"]], color="tab:green", linewidth=1.75, label="NBC 205 2024")

plt.plot(pga, df[columns["CP CCP"]], color="tab:blue", linewidth=1.75, linestyle=(0, (3, 1, 1, 1)))
plt.plot(pga, df[columns["CP Experimental"]], color="tab:orange", linewidth=1.75, linestyle=(0, (3, 1, 1, 1)))
plt.plot(pga, df[columns["CP NBC 205 2024"]], color="tab:green", linewidth=1.75, linestyle=(0, (3, 1, 1, 1)))

plt.xlabel("PGA (g)", fontsize=15)
plt.ylabel("Probability of Exceedance", fontsize=15)
plt.tick_params(direction='in', right=True, labelsize=15)
plt.axvline(0.35, color='tab:red', linestyle=(0, (1, 1)), linewidth=1.25)
plt.title("Fragility Curves", fontsize=15)
plt.xlim(0, 2)
plt.ylim(0, 1)
plt.grid(True, linewidth=0.7, alpha=0.7)
# Existing handles for retrofit type (color)
handles, labels = plt.gca().get_legend_handles_labels()

# Proxy artists for performance level (line style)
line_type_handles = [
    Line2D([0], [0], color='black', linewidth=1.75, linestyle=(0, (5, 2)), label='IO'),
    Line2D([0], [0], color='black', linewidth=1.75, linestyle='-',  label='LS'),
    Line2D([0], [0], color='black', linewidth=1.75, linestyle=(0, (3, 1, 1, 1)),  label='CP'),
    Line2D([0], [0], color='tab:red', linewidth=1.25, linestyle=(0, (1, 1)), label='Design PGA (0.35g)'),
]

plt.legend(handles=handles + line_type_handles, fontsize=15)

plt.tight_layout()
plt.show()