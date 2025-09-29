import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Times New Roman'
import seaborn as sns
import matplotlib.gridspec as gridspec
from io import StringIO

# Raw data
data = """
Construction Practices,ML Models,RMSE Test,MAE Test,R2 Test
SC1 CCP,RandomForest,0.319915,0.205643,0.982992
SC1 CCP,XGBoost,0.275982,0.172689,0.987342
SC1 CCP,LightGBM,0.274692,0.186291,0.98746
SC1 CCP,CatBoost,0.236555,0.150648,0.990701
SC1 NBC 205:1994,RandomForest,0.215712,0.101711,0.983686
SC1 NBC 205:1994,XGBoost,0.184364,0.064851,0.988083
SC1 NBC 205:1994,LightGBM,0.190037,0.073204,0.987339
SC1 NBC 205:1994,CatBoost,0.175569,0.056431,0.989193
SC1 NBC 205:2012,RandomForest,0.068474,0.044648,0.995468
SC1 NBC 205:2012,XGBoost,0.05638,0.032425,0.996928
SC1 NBC 205:2012,LightGBM,0.05132,0.031398,0.997454
SC1 NBC 205:2012,CatBoost,0.044932,0.029499,0.998049
SC1 NBC 105:2020,RandomForest,0.06698,0.035641,0.991811
SC1 NBC 105:2020,XGBoost,0.057695,0.027871,0.993924
SC1 NBC 105:2020,LightGBM,0.058486,0.032538,0.993756
SC1 NBC 105:2020,CatBoost,0.052313,0.025801,0.995005
SC1 NBC 205:2024,RandomForest,0.046819,0.031584,0.989125
SC1 NBC 205:2024,XGBoost,0.037996,0.025928,0.992838
SC1 NBC 205:2024,LightGBM,0.045154,0.032598,0.989885
SC1 NBC 205:2024,CatBoost,0.038861,0.027243,0.992508
SC2,RandomForest,0.167999,0.092302,0.991975
SC2,XGBoost,0.123529,0.059719,0.995661
SC2,LightGBM,0.138554,0.079639,0.994541
SC2,CatBoost,0.115205,0.064115,0.996226
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