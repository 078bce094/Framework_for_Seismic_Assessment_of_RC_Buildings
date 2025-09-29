import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Times New Roman'
import seaborn as sns
import matplotlib.gridspec as gridspec
from io import StringIO

# Raw data
data = """
Construction Practices,ML Models,RMSE Test,MAE Test,R2 Test
SC1 CCP,RandomForest,0.321987,0.205789,0.982771
SC1 CCP,XGBoost,0.313165,0.204808,0.983702
SC1 CCP,LightGBM,0.333323,0.23958,0.981536
SC1 CCP,CatBoost,0.294092,0.19966,0.985627
SC1 NBC 205:1994,RandomForest,0.218497,0.103339,0.983262
SC1 NBC 205:1994,XGBoost,0.217776,0.11666,0.983373
SC1 NBC 205:1994,LightGBM,0.24292,0.152461,0.979311
SC1 NBC 205:1994,CatBoost,0.20969,0.11553,0.984584
SC1 NBC 205:2012,RandomForest,0.069525,0.045001,0.995328
SC1 NBC 205:2012,XGBoost,0.069791,0.049819,0.995292
SC1 NBC 205:2012,LightGBM,0.095142,0.070224,0.991251
SC1 NBC 205:2012,CatBoost,0.072389,0.052381,0.994935
SC1 NBC 105:2020,RandomForest,0.067838,0.036239,0.9916
SC1 NBC 105:2020,XGBoost,0.072418,0.044461,0.990428
SC1 NBC 105:2020,LightGBM,0.08619,0.059694,0.986441
SC1 NBC 105:2020,CatBoost,0.071966,0.04685,0.990547
SC1 NBC 205:2024,RandomForest,0.047875,0.032044,0.988629
SC1 NBC 205:2024,XGBoost,0.048552,0.034226,0.988305
SC1 NBC 205:2024,LightGBM,0.050783,0.037458,0.987206
SC1 NBC 205:2024,CatBoost,0.046961,0.034524,0.989059
SC2,RandomForest,0.15628,0.081405,0.993055
SC2,XGBoost,0.195191,0.127718,0.989166
SC2,LightGBM,0.238432,0.161812,0.983835
SC2,CatBoost,0.186356,0.123939,0.990125
"""

# Load data
df = pd.read_csv(StringIO(data))

# Pivot for each metric
df_rmse = df.pivot(index="Construction Practices", columns="ML Models", values="RMSE Test")
df_mae = df.pivot(index="Construction Practices", columns="ML Models", values="MAE Test")
df_r2 = df.pivot(index="Construction Practices", columns="ML Models", values="R2 Test")

# Set up figure with subplots
fig = plt.figure(figsize=(15, 4))
spec = gridspec.GridSpec(ncols=3, nrows=1, figure=fig)

# Heatmap for RMSE
ax0 = fig.add_subplot(spec[0])
sns.heatmap(df_rmse, annot=True, fmt=".4f", cmap="OrRd", ax=ax0, cbar_kws={'label': 'RMSE'}, annot_kws={"size": 9})
# ax0.set_title("RMSE Heatmap")
ax0.tick_params(axis='both', labelsize=10)
ax0.set_ylabel("Construction Practices", fontsize=12)
ax0.set_xlabel("")
ax0.set_yticklabels(ax0.get_yticklabels(), rotation=0)

# Heatmap for MAE
ax1 = fig.add_subplot(spec[1])
sns.heatmap(df_mae, annot=True, fmt=".4f", cmap="YlGnBu", ax=ax1, cbar_kws={'label': 'MAE'}, annot_kws={"size": 9})
# ax1.set_title("MAE Heatmap")
ax1.tick_params(axis='both', labelsize=10)
# ax1.set_ylabel("Construction Practices", fontsize=12)
ax1.set_ylabel("", labelpad=0)
ax1.set_xlabel("ML Models", fontsize=12)
ax1.set_yticklabels(ax1.get_yticklabels(), rotation=0)

# Heatmap for R2
ax2 = fig.add_subplot(spec[2])
sns.heatmap(df_r2, annot=True, fmt=".4f", cmap="YlOrBr", ax=ax2, cbar_kws={'label': 'R²'}, annot_kws={"size": 9})
# ax2.set_title("R² Heatmap")
ax2.tick_params(axis='both', labelsize=10)
# ax2.set_ylabel("Construction Practices", fontsize=12)
ax2.set_ylabel("", labelpad=0)
ax2.set_xlabel("")
ax2.set_yticklabels(ax2.get_yticklabels(), rotation=0)

# Layout
plt.tight_layout()
plt.show()