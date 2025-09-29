import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# 'IA', 'Dsig_(sec)',

# df = pd.read_csv('/Users/niraj/Documents/ML/datasets/SC1_CCP.csv')
# df = pd.read_csv('/Users/niraj/Documents/ML/datasets/SC1_NBC_205_1994.csv')
# df = pd.read_csv('/Users/niraj/Documents/ML/datasets/SC1_NBC_205_2012.csv') # don't drop 'Ab_(m2)'
# df = pd.read_csv('/Users/niraj/Documents/ML/datasets/SC1_NBC_105_2020.csv') # don't drop 'Ab_(m2)'
# df = pd.read_csv('/Users/niraj/Documents/ML/datasets/SC1_NBC_205_2024.csv') # don't drop 'Ab_(m2)'
df = pd.read_csv('/Users/niraj/Documents/ML/datasets/SC2_Compiled.csv') # don't drop 'fc_(MPa)', 'fy_(MPa)', 'Ab_(m2)', 'Ac_(m2)', 'Kfc', 'ρ'

# df = df.drop(columns=['Sample_no', 'RSN', 'fc_(MPa)', 'fy_(MPa)', 'Ac_(m2)', 
#                       'Kfc', 'ρ', 'IA', 'Dsig_(sec)',
#                       'T2_(s)', 'T3_(s)',
#                       'Final_T1 (s)', 'Final_T2 (s)', 'Final_T3 (s)', 
#                       'max_base_shear_kN',
#                       'MIDR_1st_floor', 'MIDR_2nd_floor', 'MIDR_3rd_floor', 'MIDR_4th_floor',
#                       'Max_Park_Ang_DI_storey', 'Park_Ang_DI'])

df = df.drop(columns=['Sample_no', 'RSN',
                      'T2_(s)', 'T3_(s)',
                      'Final_T1 (s)', 'Final_T2 (s)', 'Final_T3 (s)', 
                      'max_base_shear_kN',
                      'MIDR_1st_floor', 'MIDR_2nd_floor', 'MIDR_3rd_floor', 'MIDR_4th_floor',
                      'Max_Park_Ang_DI_storey', 'Park_Ang_DI'])

df.columns = [col.replace('_', ' ') for col in df.columns]
corr_matrix = df.corr()
plt.rcParams['font.family'] = 'Times New Roman' 
plt.rcParams['font.size'] = 7       # Base font size for general text
plt.rcParams['axes.labelsize'] = 7    # Axis labels
plt.rcParams['xtick.labelsize'] = 7   # X-axis tick labels
plt.rcParams['ytick.labelsize'] = 7   # Y-axis tick labels
plt.rcParams['axes.titlesize'] = 7    # Title size

fig, ax = plt.subplots(figsize=(9, 7)) 
fig.subplots_adjust(left=0.14, right=0.95, top=0.97, bottom=0.15)
ax = sns.heatmap(corr_matrix,
                 annot=True,
                 linewidth=0.0,
                 fmt=".2f",
                 cbar=1,
                 annot_kws={"fontsize": 6},
                 mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1),
                 alpha=0.94
                 );
plt.show()