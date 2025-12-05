# EHR Data Analysis & CDISC Implementation Project

Electronic Health Records Data Analysis for Hospital Admissions and Patient Data.

A comprehensive introduction to Electronic Health Record (EHR) data analysis using Python. This project demonstrates a typical workflow, from simulating complex healthcare data to performing exploratory data analysis (EDA), implementing CDISC standards, and building machine learning models to predict critical patient outcomes.

## Why EHR Data Analysis?
Electronic Health Records (EHRs) are a rich source of information that can revolutionize healthcare. By analyzing EHR data, we can:
1. Identify patterns in diseases and treatments.
2. Predict patient risks (e.g., hospital readmission, mortality).
3. Optimize hospital operations and resource allocation.
4. Support clinical decision-making.
5. Advance medical research and public health initiatives.

## Technical Implementation Overview
This project demonstrates an end-to-end workflow for analyzing Electronic Health Record (EHR) data in a pharmaceutical/clinical research context. It showcases expertise in:
- **Data Generation**: Simulating realistic patient data.
- **CDISC Standards**: Implementing SDTM (Study Data Tabulation Model) and AdaM (Analysis Data Model) standards.
- **SAS Programming**: Providing professional SAS code assets for regulatory data submission.
- **Machine Learning**: Developing predictive models for hospital readmissions using Python.

## Project Structure
```
├── data/
│   ├── raw/       # Synthetic EHR data (CSV)
│   ├── sdtm/      # Mapped SDTM domains (DM, LB, VS, HO)
│   └── adam/      # Analysis Datasets (ADSL, ADLB)
├── scripts/
│   ├── data_gen/  # Data simulation scripts
│   ├── cdisc/     # Python implementation of CDISC mapping
│   └── modeling/  # Machine Learning analysis scripts
├── sas_code/      # SAS programs for SDTM/AdaM (Portfolio Assets)
├── results/       # Model performance metrics and plots
└── docs/          # Documentation
```

## Workflows

### 1. Data Generation
Run `scripts/data_gen/generate_data.py` to create synthetic patient records, encounters, labs, and vitals.

### 2. CDISC Standardization
The project maps raw data to standard CDISC domains:
- **SDTM**: DM (Demographics), LB (Laboratory), VS (Vital Signs), HO (Healthcare Occurrences).
- **AdaM**: ADSL (Subject-Level), ADLB (Lab Analysis).
Run `scripts/cdisc/map_to_sdtm.py` and `scripts/cdisc/map_to_adam.py`.

### 3. Predictive Modeling
A Random Forest model predicts the risk of 30-day hospital readmission based on demographics, baseline vitals, and lab values.
Run `scripts/modeling/train_model.py`.

## Key Technologies
- **Python**: pandas, numpy, scikit-learn
- **Standards**: CDISC SDTM IG 3.2, AdaM IG 1.1
- **SAS**: Code provided for industry-standard compliance
