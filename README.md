This repository contains the codes I used in my paper,
Abstract:
Seismic fragility curves can help assess damage of similar structures, specified by a few number of structural features, and usually one ground motion (GM) feature. 
In Nepal, a wide range of construction practices have existed till date, 
and current standards require the reinforced concrete (RC) buildings to maintain structural integrity under application of the design spectrums for different soil types.
In this regard, 1942 low-rise RC building typologies representative of different construction practices have been modeled in OpenSees,
and they have been subjected to 28 soil-specific GMs-for nonlinear time history analysis (NLTHA) to estimate maximum inter-storey
drift ratio (MIDR). Correspondingly, distribution of damage across varying construction practices on different soil types has been
presented. Moreover, five practice-specific, and one generalized machine learning (ML) model has been developed that incorporates
both structural features (Beam and Column cross-sectional area, bay widths, inter-storey height, no of bays, no of storey, aspect ratio,
plinth area, fundamental time period, concrete compressive strength, yield strength of reinforcement bars, confinement factor and
reinforcement ratio) and seismic features (GM intensity measures, GM duration and frequency content, energy and damage potential
indicators) to estimate the damage level in terms of MIDR. Across the developed models, mean absolute error ranged from 0.0258 to
0.1506, while coefficient of determination (R2) varied from 98.92% to 99.80% indicating robust performance. Feature importance, and
their interdependence have been evaluated using Shapley values and SHAP dependence plot, resulting in identification of three most
mutually-interacting and influential features, GM mean period, predominant period and natural vibration period.
