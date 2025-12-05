/* --------------------------------------------------------------------------
   Program: adam_adsl.sas
   Purpose: Create ADSL (Subject-Level Analysis Dataset)
   Author: EHR Data Analyst
   Date: 2025-05-01
   -------------------------------------------------------------------------- */

libname sdtm "path/to/sdtm";
libname adam "path/to/adam";

/* Get Source Data */
data dm;
    set sdtm.dm;
run;

data ho;
    set sdtm.ho;
run;

data vs;
    set sdtm.vs;
run;

/* --------------------------------------------------------------------------
   Derivations
   -------------------------------------------------------------------------- */

/* 1. Calculate Hospitalization Counts */
proc sql;
    create table hosp_counts as
    select USUBJID, count(*) as NHOSP
    from ho
    group by USUBJID;
quit;

/* 2. Flag Readmissions */
proc sql;
    create table readmissions as
    select distinct USUBJID, 'Y' as READM_FL
    from ho
    where HOTERM = 'READMITTED';
quit;

/* 3. Get Baseline BMI */
/* Sort by date first to get earliest */
proc sort data=vs out=vs_sorted;
    by USUBJID VSDTC;
    where VSTESTCD = 'BMI';
run;

data baseline_bmi;
    set vs_sorted;
    by USUBJID;
    if first.USUBJID;
    BMIBL = VSSTRESN;
    keep USUBJID BMIBL;
run;

/* Merge into ADSL */
data adsl;
    merge dm(in=a)
          hosp_counts(in=b)
          readmissions(in=c)
          baseline_bmi(in=d);
    by USUBJID;
    if a;
    
    /* Handle missings */
    if NHOSP = . then NHOSP = 0;
    if READM_FL = '' then READM_FL = 'N';
    
    /* Population Flags */
    SAFFL = 'Y';
    ITTFL = 'Y';
    
    /* Treatment Groups */
    TRT01P = 'Standard of Care';
    TRT01A = 'Standard of Care';
    
    /* Format dates if needed */
    format BMIBL 8.1;
run;

/* Save ADSL */
proc sort data=adsl out=adam.adsl;
    by USUBJID;
run;


/* QA Check */
proc means data=adam.adsl n mean min max;
    var NHOSP BMIBL;
    title "Summary Stats for ADSL";
run;

proc freq data=adam.adsl;
    tables READM_FL SAFFL / missing;
run;
