/* --------------------------------------------------------------------------
   Program: sdtm_dm.sas
   Purpose: Create SDTM DM (Demographics) domain from raw patient data
   Author: EHR Data Analyst
   Date: 2025-05-01
   -------------------------------------------------------------------------- */

libname sdtm "path/to/sdtm";
libname raw "path/to/raw";

/* Load raw data */
data patients;
    set raw.patients;
run;

/* Map to SDTM DM */
data dm_mapped;
    set patients;
    
    /* Fixed study variables */
    STUDYID = "EHR_PROJECT_001";
    DOMAIN  = "DM";
    
    /* Subject Identifiers */
    USUBJID = catx("-", "EHR-001", patient_id);
    SUBJID  = patient_id;
    SITEID  = "001";
    
    /* Demographics */
    SEX     = gender;
    RACE    = race;
    COUNTRY = "USA";
    
    /* Dates */
    /* Assuming input date format YYYY-MM-DD */
    BRTHDTC = dob;
    
    /* Arm/Group Assignment */
    ARMCD   = "SCRN";
    ARM     = "Screening";
    ACTARMCD= "SCRN";
    ACTARM  = "Screening";
    
    /* Age Calculation (Reference to Collection Date) */
    /* Placeholder for first collection date logic */
    rfstdtc_date = input(scan(dob,1,'T'), yymmdd10.);
    current_date = today();
    AGE = floor((intck('month', rfstdtc_date, current_date) - (day(current_date) < day(rfstdtc_date))) / 12);
    AGEU    = "YEARS";
    
    /* Keep only required variables */
    keep STUDYID DOMAIN USUBJID SUBJID SITEID BRTHDTC SEX RACE AGE AGEU ARM ARMCD ACTARM ACTARMCD COUNTRY;
run;

/* Sort and Save */
proc sort data=dm_mapped out=sdtm.dm;
    by USUBJID;
run;

/* QA Check */
proc freq data=sdtm.dm;
    tables SEX RACE ARM / missing;
    title "Frequency check for DM variables";
run;
