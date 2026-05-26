# Machine Learning-Based Framework for Real-Time Seismic Damage Assessment of RC Buildings

## Overview
This repository contains the data pipeline, finite element simulation architecture, and machine learning models for the first large-scale, data-driven seismic vulnerability framework developed for Nepal's building stock. By integrating automated nonlinear structural simulations with advanced gradient boosting and deep learning algorithms, this framework enables real-time regional damage assessment and post-earthquake decision-making.

This research paper has been submitted to ***Advances in Structural Engineering*** (Manuscript ID: ASE-26-0085).

## Methodology & Framework Pipeline
1. **Automated FE Modeling:** Programmed an OpenSeesPy pipeline to model **1,900+ RC buildings** representing diverse Nepalese construction paradigms (Non-engineered, NBC 205:1994, NBC 205:2012, NBC 105:2020, and NBC 205:2024).
2. **High-Throughput Simulation:** Executed Nonlinear Time-History Analyses (NLTHA) using site-specific local soil spectra, generating an engineering dataset of **54,000+ structural response vectors**.
3. **Machine Learning Architecture:** Trained and optimized predictive models (`XGBoost`, `LightGBM`, `CatBoost`, `PyTorch`) utilizing `Optuna` for automated hyperparameter tuning.
4. **Explainable AI:** Applied SHAP (SHapley Additive exPlanations) analysis to quantify structural feature importances and interpret physical damage drivers.

## Key Insights & Structural Takeaways
* Developed a highly accurate tool for instantaneous damage estimation following a national seismic event.
* SHAP analysis isolated the **mean period**, **predominant period**, and **natural vibration period** of the structure as critical interacting features governing damage levels.
* Exposed vulnerable structural thresholds and systemic shortcomings in existing building practices across different local soil types.

## Tech Stack
* **Structural Simulation:** `OpenSeesPy`
* **Machine Learning & Deep Learning:** `scikit-learn`, `PyTorch`, `XGBoost`, `LightGBM`, `CatBoost`
* **Hyperparameter Optimization:** `Optuna`
* **Model Explainability:** `SHAP`
* **Data Science Infrastructure:** `NumPy`, `Pandas`, `SciPy`, `Matplotlib`, `Seaborn`, `Opsvis`

## Contact & Collaboration
* **Primary Researcher:** Niraj Kumar Yadav (078bce094.niraj@pcampus.edu.np)
* **Supervisor:** Dr. Kshitiz C. Shrestha
Contact via email for the developed dataset, and/or collaboration on future work of this project.
