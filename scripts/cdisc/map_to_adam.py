import pandas as pd
import numpy as np
import os
from datetime import datetime

def create_adsl(dm_df, ho_df, vs_df):
    """
    Creates ADSL (Subject-Level Analysis Dataset).
    One record per subject.
    """
    adsl = dm_df.copy()
    
    # Calculate Age (if not already strictly defined in DM, here we just use what mapped)
    # Assume AGE is populated or we recalculate. For this sim, we already mapped it but let's just ensure relevant columns.
    
    # Derivations
    # 1. Number of hospitalizations (from HO)
    if not ho_df.empty:
        hosp_counts = ho_df.groupby('USUBJID').size().reset_index(name='NHOSP')
        adsl = adsl.merge(hosp_counts, on='USUBJID', how='left')
        adsl['NHOSP'] = adsl['NHOSP'].fillna(0).astype(int)
        
        # 2. Flag for Readmission (Any 'READMITTED' in HOTERM)
        readmits = ho_df[ho_df['HOTERM'] == 'READMITTED']['USUBJID'].unique()
        adsl['READM_FL'] = np.where(adsl['USUBJID'].isin(readmits), 'Y', 'N')
        
    else:
        adsl['NHOSP'] = 0
        adsl['READM_FL'] = 'N'

    # 3. Baseline BMI (from VS)
    if not vs_df.empty:
        # Get first BMI measurement
        bmi_data = vs_df[vs_df['VSTESTCD'] == 'BMI'].sort_values('VSDTC')
        baseline_bmi = bmi_data.drop_duplicates('USUBJID', keep='first')[['USUBJID', 'VSSTRESN']]
        baseline_bmi = baseline_bmi.rename(columns={'VSSTRESN': 'BMIBL'})
        adsl = adsl.merge(baseline_bmi, on='USUBJID', how='left')
    
    # Analysis Population Flags
    adsl['SAFFL'] = 'Y' # Safety Population
    adsl['ITTFL'] = 'Y' # Intent-to-Treat
    
    # Analysis Variables
    adsl['TRT01P'] = 'Standard of Care'
    adsl['TRT01A'] = 'Standard of Care'
    
    # Rename/Select columns for ADSL compliance (Simplified)
    # Keep core DM + new ADSL vars
    cols = ['STUDYID', 'USUBJID', 'SUBJID', 'SITEID', 'AGE', 'SEX', 'RACE', 'ARM', 'SAFFL', 'ITTFL', 'TRT01P', 'NHOSP', 'READM_FL', 'BMIBL', 'BRTHDTC']
    # Use existing columns, fill missing
    for c in cols:
        if c not in adsl.columns:
            adsl[c] = ''
            
    return adsl[cols]

def create_adlb(lb_df, adsl_df):
    """
    Creates ADLB (Analysis Dataset for Lab Data).
    """
    # Start with LB domain
    adlb = lb_df.copy()
    
    # Merge ADSL info (TRT01P, etc.)
    adlb = adlb.merge(adsl_df[['USUBJID', 'TRT01P', 'SAFFL']], on='USUBJID', how='left')
    
    # Derivations
    # 1. Analysis Value (AVAL)
    # Ensure numeric
    adlb['AVAL'] = pd.to_numeric(adlb['LBSTRESN'], errors='coerce')
    adlb['PARAM'] = adlb['LBTEST']
    adlb['PARAMCD'] = adlb['LBTESTCD']
    
    # 2. Analysis Unit
    adlb['AVALU'] = adlb['LBSTRESU']
    
    # 3. Change from Baseline
    # Sort by date
    adlb = adlb.sort_values(['USUBJID', 'PARAMCD', 'LBDTC'])
    
    # For this simulation, let's assume the first record is baseline
    adlb['BASE'] = adlb.groupby(['USUBJID', 'PARAMCD'])['AVAL'].transform('first')
    
    # Change from baseline
    adlb['CHG'] = adlb['AVAL'] - adlb['BASE']
    
    # Percentage Change
    adlb['PCHG'] = (adlb['CHG'] / adlb['BASE']) * 100
    
    # Flags
    adlb['ANL01FL'] = 'Y' # Flag for analysis
    
    return adlb

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../'))
    sdtm_dir = os.path.join(project_root, 'data/sdtm')
    adam_dir = os.path.join(project_root, 'data/adam')
    
    print("Loading SDTM data...")
    dm = pd.read_csv(os.path.join(sdtm_dir, 'dm.csv'))
    lb = pd.read_csv(os.path.join(sdtm_dir, 'lb.csv'))
    vs = pd.read_csv(os.path.join(sdtm_dir, 'vs.csv'))
    ho = pd.read_csv(os.path.join(sdtm_dir, 'ho.csv'))
    
    print("Creating ADSL...")
    adsl = create_adsl(dm, ho, vs)
    adsl.to_csv(os.path.join(adam_dir, 'adsl.csv'), index=False)
    
    print("Creating ADLB...")
    adlb = create_adlb(lb, adsl)
    adlb.to_csv(os.path.join(adam_dir, 'adlb.csv'), index=False)
    
    print("AdaM creation complete. Saved to data/adam/")
