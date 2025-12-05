import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
import matplotlib.pyplot as plt

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '../../'))
    adam_dir = os.path.join(project_root, 'data/adam')
    results_dir = os.path.join(project_root, 'results')
    
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        
    print("Loading AdaM data...")
    adsl = pd.read_csv(os.path.join(adam_dir, 'adsl.csv'))
    adlb = pd.read_csv(os.path.join(adam_dir, 'adlb.csv'))
    
    # --- Feature Engineering ---
    
    # 1. Subject Level Features
    df = adsl[['USUBJID', 'AGE', 'SEX', 'RACE', 'BMIBL', 'NHOSP', 'READM_FL']].copy()
    
    # Target
    df['Target'] = df['READM_FL'].apply(lambda x: 1 if x == 'Y' else 0)
    
    # Clean Demographics
    df['SEX'] = LabelEncoder().fit_transform(df['SEX'])
    df['RACE'] = LabelEncoder().fit_transform(df['RACE'])
    
    # Age cleaning (handle non-numeric if any, though our sim is clean)
    # Using 'AGE' from DM which might be empty string in our map if calculations failed, 
    # but let's assume we have birth dates in DM/ADSL. Actually our map left AGE blank in DM.
    # Let's re-calculate AGE from BRTHDTC if missing, or use simulated date.
    # For this demo, let's just synthesize Age if missing or use DOB.
    if df['AGE'].isnull().all() or (df['AGE'] == '').all():
        # Quick fix: Calculate approximate age from BRTHDTC
        # Format YYYY-MM-DD
        today = pd.to_datetime('today')
        dob = pd.to_datetime(adsl['BRTHDTC'])
        df['AGE_CALC'] = (today - dob).dt.days / 365.25
        df['AGE'] = df['AGE_CALC']
    
    df['AGE'] = df['AGE'].fillna(df['AGE'].mean())
    df['BMIBL'] = df['BMIBL'].fillna(df['BMIBL'].mean())
    
    # 2. Lab Features (Aggregate ADLB)
    # Pivot ADLB to get columns for each test
    # We want baseline or average values
    lab_pivot = adlb.pivot_table(index='USUBJID', columns='PARAMCD', values='AVAL', aggfunc='mean').reset_index()
    
    # Merge Labs
    df = df.merge(lab_pivot, on='USUBJID', how='left')
    
    # Fill missing labs with mean
    for col in df.columns:
        if df[col].isnull().any():
             df[col] = df[col].fillna(df[col].mean())
             
    # Prepare X and y
    feature_cols = [c for c in df.columns if c not in ['USUBJID', 'Target', 'READM_FL', 'AGE_CALC']]
    X = df[feature_cols]
    y = df['Target']
    
    print(f"Features: {feature_cols}")
    print(f"Target distribution: \n{y.value_counts()}")
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # --- Modeling ---
    print("Training Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = rf.predict(X_test_scaled)
    y_prob = rf.predict_proba(X_test_scaled)[:, 1]
    
    # --- Evaluation ---
    print("\nModel Evaluation:")
    print(classification_report(y_test, y_pred))
    auc = roc_auc_score(y_test, y_prob)
    print(f"ROC AUC: {auc:.4f}")
    
    # Feature Importance
    importances = pd.DataFrame({
        'Feature': feature_cols,
        'Importance': rf.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print("\nTop Predictors:")
    print(importances.head())
    
    # Save Results
    importances.to_csv(os.path.join(results_dir, 'feature_importance.csv'), index=False)
    print("Model training complete.")
