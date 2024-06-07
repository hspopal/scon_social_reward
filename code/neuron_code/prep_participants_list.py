#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 15:48:10 2024

@author: hpopal
"""

import os
import sys
import glob
import pandas as pd
import numpy as np
from datetime import datetime, date 




# Set BIDS project directory
bids_dir = '/data/neuron/SCN/SR/'
os.chdir(bids_dir)


# Find participant fmriprep output directories
fmriprep_files = os.listdir(bids_dir+'derivatives/fmriprep/')
fmriprep_subjs = [x for x in fmriprep_files if '.html' not in x]
fmriprep_subjs.sort()


# Import Redcap demographics info
redcap_info = pd.read_csv(glob.glob(os.path.join(bids_dir, 'derivatives',
                                                 'SCONNChildPacket-Id*.csv'))[0])

# Identify relevent columns in the Redcap dataframe
relv_cols = ['record_id', 'child_gender_lab_entered', 'child_birthday',
             'date_of_visit', 'group']

redcap_info_fltr = redcap_info[relv_cols]

# Capitalize subject name to standardize
redcap_info_fltr['record_id'] = redcap_info_fltr['record_id'].str.upper()


# Filter to only capture subjects with fmriprep data

# Create a copy of the redcap data
fmriprep_demo = redcap_info_fltr.copy()

# Rename subject IDs to match fmripre IDs
fmriprep_demo['record_id'] = 'sub-' + fmriprep_demo['record_id']
fmriprep_demo['record_id'] = fmriprep_demo['record_id'].str.replace('_', '', 
                                                                    regex=True)

# Filter
fmriprep_demo = fmriprep_demo[fmriprep_demo['record_id'].isin(fmriprep_subjs)]

# Fill nan with empty strings
fmriprep_demo = fmriprep_demo.fillna('')

# Calculate age
fmriprep_demo['age'] = ''

for n in fmriprep_demo.index:
    # Select the birth date
    date_birth_str = fmriprep_demo.loc[n, 'child_birthday']
    
    if len(date_birth_str.split('/')[-1]) == 2:
        date_birth = datetime.strptime(date_birth_str, 
                                   "%m/%d/%y").date()
    elif len(date_birth_str.split('/')[-1]) == 4:
        date_birth = datetime.strptime(date_birth_str, 
                                   "%m/%d/%Y").date()
    else:
        continue
        
        
    # Select the birth date
    date_study_str = fmriprep_demo.loc[n, 'date_of_visit']    
    date_study_str = date_study_str.split(' + ')[0]
    
    if len(date_study_str.split('/')[-1]) == 2:
        date_study = datetime.strptime(date_study_str, 
                                   "%m/%d/%y").date()
    elif len(date_study_str.split('/')[-1]) == 4:
        date_study = datetime.strptime(date_study_str, 
                                   "%m/%d/%Y").date()
    else:
        continue
    
    
    
    # Subtract to find the age in days and divide by number of days in year
    # accounting for leap years
    age = (date_study - date_birth).days / 365.25
    
    # Round and input into demo dataframe
    fmriprep_demo.loc[n, 'age'] = round(age, 2)
  

# Rename columns
fmriprep_demo = fmriprep_demo.rename(columns={'record_id': 'participant_id', 
                                              'child_gender_lab_entered': 'gender'})

# Filter for only relevent columns
outp_cols = ['participant_id', 'age', 'gender', 'group']

fmriprep_demo[outp_cols].to_csv(bids_dir+'/participants.tsv', sep='\t', 
                                index=False)




