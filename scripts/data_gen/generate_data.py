import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
import random

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_patient_demographics(n_patients=1000):
    ids = [str(uuid.uuid4())[:8].upper() for _ in range(n_patients)]
    genders = np.random.choice(['M', 'F'], n_patients, p=[0.48, 0.52])
    
    # Generate dates of birth (age 18 to 90)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90*365)
    dobs = []
    for _ in range(n_patients):
        random_days = random.randint(18*365, 90*365)
        dob = end_date - timedelta(days=random_days)
        dobs.append(dob.strftime('%Y-%m-%d'))
        
    races = np.random.choice(
        ['WHITE', 'BLACK OR AFRICAN AMERICAN', 'ASIAN', 'OTHER'], 
        n_patients, 
        p=[0.6, 0.2, 0.1, 0.1]
    )
    
    df = pd.DataFrame({
        'patient_id': ids,
        'gender': genders,
        'dob': dobs,
        'race': races
    })
    return df

def generate_encounters(patients_df):
    encounters = []
    
    for _, patient in patients_df.iterrows():
        # Random number of encounters per patient (0 to 3)
        n_encounters = np.random.choice([0, 1, 2, 3], p=[0.2, 0.4, 0.3, 0.1])
        
        current_date = datetime.strptime(patient['dob'], '%Y-%m-%d') + timedelta(days=18*365) 
        if current_date > datetime.now():
            current_date = datetime.now() - timedelta(days=365)

        for _ in range(n_encounters):
            # Admission date
            days_forward = random.randint(1, 365*2) # Spread over 2 years
            admission_date = current_date + timedelta(days=days_forward)
            if admission_date > datetime.now():
                break
                
            los = random.randint(1, 14) # Length of stay
            discharge_date = admission_date + timedelta(days=los)
            
            outcome = np.random.choice(
                ['DISCHARGED', 'TRANSFERRED', 'DEATH', 'READMITTED'], 
                p=[0.8, 0.1, 0.05, 0.05]
            )
            
            encounters.append({
                'patient_id': patient['patient_id'],
                'encounter_id': str(uuid.uuid4())[:8].upper(),
                'admission_date': admission_date.strftime('%Y-%m-%d'),
                'discharge_date': discharge_date.strftime('%Y-%m-%d'),
                'outcome': outcome,
                'diagnosis_code': np.random.choice(['I10', 'E11', 'J18', 'I50', 'N17'], p=[0.3, 0.3, 0.2, 0.1, 0.1]) # hypertension, diabetes, pneumonia, heart failure, acute kidney failure
            })
            current_date = discharge_date
            
    return pd.DataFrame(encounters)

def generate_labs(encounters_df):
    labs_data = []
    
    for _, encounter in encounters_df.iterrows():
        # Generate random labs for each encounter
        n_labs = random.randint(1, 3)
        admission_date = datetime.strptime(encounter['admission_date'], '%Y-%m-%d')
        
        for _ in range(n_labs):
            lab_date = admission_date + timedelta(days=random.randint(0, 2))
            
            # Glucose
            labs_data.append({
                'patient_id': encounter['patient_id'],
                'encounter_id': encounter['encounter_id'],
                'date': lab_date.strftime('%Y-%m-%d'),
                'test_name': 'Glucose',
                'result_value': round(np.random.normal(100, 20), 1),
                'unit': 'mg/dL'
            })
            
            # Creatinine
            labs_data.append({
                'patient_id': encounter['patient_id'],
                'encounter_id': encounter['encounter_id'],
                'date': lab_date.strftime('%Y-%m-%d'),
                'test_name': 'Creatinine',
                'result_value': round(np.random.normal(1.0, 0.3), 2),
                'unit': 'mg/dL'
            })
            
    return pd.DataFrame(labs_data)

def generate_vitals(encounters_df):
    vitals_data = []
    
    for _, encounter in encounters_df.iterrows():
        admission_date = datetime.strptime(encounter['admission_date'], '%Y-%m-%d')
        
        # Initial vitals
        vitals_data.append({
            'patient_id': encounter['patient_id'],
            'encounter_id': encounter['encounter_id'],
            'date': admission_date.strftime('%Y-%m-%d'),
            'measure': 'Systolic BP',
            'value': int(np.random.normal(120, 15)),
            'unit': 'mmHg'
        })
        
        vitals_data.append({
            'patient_id': encounter['patient_id'],
            'encounter_id': encounter['encounter_id'],
            'date': admission_date.strftime('%Y-%m-%d'),
            'measure': 'Diastolic BP',
            'value': int(np.random.normal(80, 10)),
            'unit': 'mmHg'
        })
        
        vitals_data.append({
            'patient_id': encounter['patient_id'],
            'encounter_id': encounter['encounter_id'],
            'date': admission_date.strftime('%Y-%m-%d'),
            'measure': 'BMI',
            'value': round(np.random.normal(25, 5), 1),
            'unit': 'kg/m2'
        })
        
    return pd.DataFrame(vitals_data)

if __name__ == "__main__":
    print("Generating synthetic EHR data...")
    
    import os

    # Determine base path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up two levels: scripts/data_gen/ -> scripts/ -> root/
    project_root = os.path.abspath(os.path.join(script_dir, '../../'))
    output_dir = os.path.join(project_root, 'data/raw')
    
    print(f"Saving data to: {output_dir}")
    
    patients = generate_patient_demographics(1000)
    patients.to_csv(os.path.join(output_dir, 'patients.csv'), index=False)
    print(f"Generated {len(patients)} patients.")
    
    encounters = generate_encounters(patients)
    encounters.to_csv(os.path.join(output_dir, 'encounters.csv'), index=False)
    print(f"Generated {len(encounters)} encounters.")
    
    labs = generate_labs(encounters)
    labs.to_csv(os.path.join(output_dir, 'labs.csv'), index=False)
    print(f"Generated {len(labs)} lab results.")
    
    vitals = generate_vitals(encounters)
    vitals.to_csv(os.path.join(output_dir, 'vitals.csv'), index=False)
    print(f"Generated {len(vitals)} vital sign records.")
    
    print("Data generation complete.")
