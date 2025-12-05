import pandas as pd
import numpy as np
import os
from datetime import datetime

def map_dm(patients_df):
    """
    Maps patient demographics to SDTM DM domain.
    """
    dm = pd.DataFrame()
    dm['STUDYID'] = 'EHR_PROJECT_001'
    dm['DOMAIN'] = 'DM'
    dm['USUBJID'] = 'EHR-001-' + patients_df['patient_id']
    dm['SUBJID'] = patients_df['patient_id']
    dm['RFSTDTC'] = '' # Reference Start Date (First admission? To be populated if needed)
    dm['RFENDTC'] = '' # Reference End Date
    dm['SITEID'] = '001'
    dm['AGE'] = '' # To be calculated relative to RFSTDTC or collection date
    dm['AGEU'] = 'YEARS'
    dm['SEX'] = patients_df['gender']
    dm['RACE'] = patients_df['race']
    dm['ETHNIC'] = '' # Not generated
    dm['ARMCD'] = 'SCRN' # Screening
    dm['ARM'] = 'Screening'
    dm['ACTARMCD'] = 'SCRN'
    dm['ACTARM'] = 'Screening'
    dm['COUNTRY'] = 'USA'
    dm['BRTHDTC'] = patients_df['dob']
    
    return dm

def map_lb(labs_df, patients_df):
    """
    Maps lab results to SDTM LB domain.
    """
    # Merge to get USUBJID
    labs = labs_df.merge(patients_df[['patient_id']], on='patient_id', how='left')
    labs['USUBJID'] = 'EHR-001-' + labs['patient_id']
    
    lb = pd.DataFrame()
    lb['STUDYID'] = 'EHR_PROJECT_001'
    lb['DOMAIN'] = 'LB'
    lb['USUBJID'] = labs['USUBJID']
    lb['LBSEQ'] = labs.groupby('USUBJID').cumcount() + 1
    lb['LBTESTCD'] = labs['test_name'].str.upper().str[:8] # Shorten for code
    lb['LBTEST'] = labs['test_name']
    lb['LBCAT'] = 'CHEMISTRY'
    lb['LBORRES'] = labs['result_value']
    lb['LBORRESU'] = labs['unit']
    lb['LBORNrLO'] = '' # Reference ranges could be added
    lb['LBORNrHI'] = ''
    lb['LBSTRESC'] = labs['result_value']
    lb['LBSTRESN'] = labs['result_value']
    lb['LBSTRESU'] = labs['unit']
    lb['LBDTC'] = labs['date']
    lb['VISITNUM'] = 1 # Approximation
    lb['VISIT'] = 'UNSCHEDULED'
    
    return lb

def map_vs(vitals_df, patients_df):
    """
    Maps vital signs to SDTM VS domain.
    """
    vs_data = vitals_df.merge(patients_df[['patient_id']], on='patient_id', how='left')
    vs_data['USUBJID'] = 'EHR-001-' + vs_data['patient_id']
    
    vs = pd.DataFrame()
    vs['STUDYID'] = 'EHR_PROJECT_001'
    vs['DOMAIN'] = 'VS'
    vs['USUBJID'] = vs_data['USUBJID']
    vs['VSSEQ'] = vs_data.groupby('USUBJID').cumcount() + 1
    
    # Map test codes
    code_map = {
        'Systolic BP': 'SYSBP', 
        'Diastolic BP': 'DIABP', 
        'BMI': 'BMI'
    }
    vs['VSTESTCD'] = vs_data['measure'].map(code_map)
    vs['VSTEST'] = vs_data['measure']
    vs['VSORRES'] = vs_data['value']
    vs['VSORRESU'] = vs_data['unit']
    vs['VSSTRESC'] = vs_data['value']
    vs['VSSTRESN'] = vs_data['value']
    vs['VSSTRESU'] = vs_data['unit']
    vs['VSDTC'] = vs_data['date']
    
    return vs

def map_ho(encounters_df, patients_df):
    """
    Maps healthcare encounters to a custom HO domain (Healthcare Occurrences) or similar.
    CDISC often uses HO for "Healthcare Encounters".
    """
    ho_data = encounters_df.merge(patients_df[['patient_id']], on='patient_id', how='left')
    ho_data['USUBJID'] = 'EHR-001-' + ho_data['patient_id']
    
    ho = pd.DataFrame()
    ho['STUDYID'] = 'EHR_PROJECT_001'
    ho['DOMAIN'] = 'HO'
    ho['USUBJID'] = ho_data['USUBJID']
    ho['HOSEQ'] = ho_data.groupby('USUBJID').cumcount() + 1
    ho['HODECOD'] = 'INPATIENT STAY'
    ho['HOTERM'] = ho_data['outcome'] # e.g. DISCHARGED, READMITTED
    ho['HOSTDTC'] = ho_data['admission_date']
    ho['HOENDTC'] = ho_data['discharge_date']
    ho['HOSTDY'] = '' # Calculation requiring RFSTDTC
    
    # Store diagnosis in a supplemetary domain or just keep here for simplicity in this demo
    ho['HOCAT'] = ho_data['diagnosis_code'] 
    
    return ho


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../'))
    raw_dir = os.path.join(project_root, 'data/raw')
    sdtm_dir = os.path.join(project_root, 'data/sdtm')
    
    print("Loading raw data...")
    patients = pd.read_csv(os.path.join(raw_dir, 'patients.csv'))
    encounters = pd.read_csv(os.path.join(raw_dir, 'encounters.csv'))
    labs = pd.read_csv(os.path.join(raw_dir, 'labs.csv'))
    vitals = pd.read_csv(os.path.join(raw_dir, 'vitals.csv'))
    
    print("Mapping to SDTM DM...")
    dm = map_dm(patients)
    dm.to_csv(os.path.join(sdtm_dir, 'dm.csv'), index=False)
    
    print("Mapping to SDTM LB...")
    lb = map_lb(labs, patients)
    lb.to_csv(os.path.join(sdtm_dir, 'lb.csv'), index=False)
    
    print("Mapping to SDTM VS...")
    vs = map_vs(vitals, patients)
    vs.to_csv(os.path.join(sdtm_dir, 'vs.csv'), index=False)
    
    print("Mapping to SDTM HO (Encounters)...")
    ho = map_ho(encounters, patients)
    ho.to_csv(os.path.join(sdtm_dir, 'ho.csv'), index=False)
    
    print("SDTM mapping complete. Saved to data/sdtm/")
