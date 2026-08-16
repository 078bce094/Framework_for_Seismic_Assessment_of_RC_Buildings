# source /Users/niraj/x86_env/bin/activate

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

plt.rcParams['font.family'] = 'Times New Roman'

csv_data = """ConstructionPractice,Damage Grade,Soil Type A,Soil Type B,Soil Type C,Soil Type D
CCP,DG1,0,1,1,0
CCP,DG2,0,0,0,0
CCP,DG3,971,47,19,97
CCP,DG4,1403,1229,396,407
CCP,DG5,20,1117,1978,1890
NBC 205:1994,DG1,0,0,1,0
NBC 205:1994,DG2,0,0,0,4
NBC 205:1994,DG3,3271,528,200,591
NBC 205:1994,DG4,761,2883,1261,1215
NBC 205:1994,DG5,0,621,2570,2222
NBC 205:2012,DG1,0,0,1,0
NBC 205:2012,DG2,2,0,0,38
NBC 205:2012,DG3,1734,747,442,777
NBC 205:2012,DG4,0,942,868,636
NBC 205:2012,DG5,0,47,425,285
NBC 105:2020,DG1,5,4,1,1
NBC 105:2020,DG2,147,104,110,480
NBC 105:2020,DG3,3544,2340,1662,1724
NBC 105:2020,DG4,0,1248,1715,1315
NBC 105:2020,DG5,0,0,208,176
NBC 205:2024,DG1,0,0,4,4
NBC 205:2024,DG2,313,254,257,666
NBC 205:2024,DG3,1423,1341,1155,930
NBC 205:2024,DG4,0,141,320,136
NBC 205:2024,DG5,0,0,0,0
"""

df = pd.read_csv(io.StringIO(csv_data))

# Prepare data for grouped stacked bar plot
construction_practices = df['ConstructionPractice'].unique()
damage_grades = ['DG1', 'DG2', 'DG3', 'DG4', 'DG5']
# Soil_types = ['A', 'B', 'C', 'D']
Soil_types = ['Soil Type A', 'Soil Type B', 'Soil Type C', 'Soil Type D']
Soil_types_colors = {'Soil Type A': '#1f77b4', 'Soil Type B': '#ff7f0e', 'Soil Type C': '#2ca02c', 'Soil Type D': '#d62728'}

n_practices = len(construction_practices)
n_grades = len(damage_grades)
bar_width = 0.13
group_width = bar_width * n_grades + 0.26  # space between groups

fig, ax = plt.subplots(figsize=(10.7, 5))

x = np.arange(n_practices) * group_width - 0.26

for j, grade in enumerate(damage_grades):
    bottoms = np.zeros(n_practices)
    for i, practice in enumerate(construction_practices):
        row = df[(df['ConstructionPractice'] == practice) & (df['Damage Grade'] == grade)]
        if not row.empty:
            values = [(soil_type, row[soil_type].values[0]) for soil_type in Soil_types]
            values.sort(key=lambda x: x[1])  # sort by value
            xpos = x[i] + j * bar_width
            for k, (soil_type, val) in enumerate(values):
                ax.bar(xpos, val, bar_width, bottom=bottoms[i], color=Soil_types_colors[soil_type], edgecolor='grey',
                       label=soil_type if (j == 0 and i == 0 and k == 0) else None)
                bottoms[i] += val
                if val > 1:
                    center_height = bottoms[i] - val / 2
                    ax.text(xpos, center_height, str(val), ha='center', va='center', fontsize=5, color='white', rotation=90)


# Add minor ticks at the center of every damage grade
minor_tick_positions = []
for i in range(n_practices):
    for j in range(n_grades):
        minor_tick_positions.append(x[i] + j * bar_width)
ax.set_xticks(minor_tick_positions, minor=True)

# Set major ticks at the center of each construction practice group
practice_centers = [x[i] + (n_grades / 2 - 0.5) * bar_width for i in range(n_practices)]
ax.set_xticks(practice_centers)

ax.set_xticklabels(construction_practices, rotation=0, ha='center', fontsize=10)

for i, label in enumerate(ax.get_xticklabels()[:n_practices]):
    label.set_y(-0.09)  # Move practice labels further down
    label.set_rotation(0)
    
# ax.set_xlabel('Construction Practice', fontweight='bold', fontsize=14, labelpad=15)
ax.set_ylabel('Number of Damaged Samples', fontsize=14, labelpad=10, loc='center')
ax.yaxis.set_label_coords(-0.04, 0.4)
ax.set_yscale('log')
ax.set_ylim(0.5, 17000)
ax.set_yticks([1, 10, 100, 1000, 10000])
ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
ax.get_yaxis().set_minor_formatter(plt.NullFormatter())
ax.tick_params(axis='y', which='both', right=True, direction='in')
# ax.set_title('Building Damage by Construction Practice, Grade, and Soil Type', fontweight='bold', fontsize=16, pad=15)

ax.text(-0.26,0.73,'1',color='white',fontsize=5,rotation=90,ha='center',va='center')
ax.text(-0.26,1.43,'1',color='white',fontsize=5,rotation=90,ha='center',va='center')
ax.text(0.647,0.73,'1',color='white',fontsize=5,rotation=90,ha='center',va='center')
ax.text(1.56,0.73,'1',color='white',fontsize=5,rotation=90,ha='center',va='center')
ax.text(2.47,0.73,'1',color='white',fontsize=5,rotation=90,ha='center',va='center')
ax.text(2.47,1.37,'1',color='white',fontsize=5,rotation=90,ha='center',va='center')

# Add Damage Grade labels above each group
for i, practice in enumerate(construction_practices):
    for j, grade in enumerate(damage_grades):
        xpos = x[i] + j * bar_width
        ax.text(xpos, -0.03, grade, ha='center', va='top', fontsize=7, rotation=90, transform=ax.get_xaxis_transform())

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, edgecolor='grey', label=soil_type) for soil_type, color in Soil_types_colors.items()]
ax.legend(handles=legend_elements, bbox_to_anchor=(0.02, 0.95), loc='upper left', fontsize=7.5, frameon=False, ncol=1)

ax.grid(0)
# ax.grid(axis='y', linestyle='--', alpha=0.5, linewidth=0.4)
ax.set_axisbelow(True)
plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
plt.show()
