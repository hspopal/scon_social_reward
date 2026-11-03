#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 13:32:25 2023

@author: hpopal
"""

import os
import sys
import glob
import pandas as pd
import numpy as np

#from nilearn.glm.first_level import make_first_level_design_matrix
#from nilearn.plotting import plot_design_matrix
#import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")

##########################################################################
# Set up
##########################################################################

# Take script inputs
#subj = 'SCN_'+str(sys.argv[1])
#task = 'SR'

# For beta testings
subj = 'SCN_101'
task = 'SR'

# Set BIDS project directory
bids_dir = '/data/neuron/SCN/SR/'
os.chdir(bids_dir)

# Set output directory
data_dir = bids_dir + 'derivatives/task_socialreward/data/' + subj + '/'
outp_dir = bids_dir + 'derivatives/SR_univariate-afni/' + 'sub-' + subj + '/'

# If subject directory does not exist in output directory, create it
if not os.path.exists(outp_dir):
    os.makedirs(outp_dir)
    
##########################################################################
# Set scan specific paramters
##########################################################################

tr = 1.25  # repetition time is 1 second
n_scans = 241  # the acquisition comprises 128 scans
frame_times = np.arange(n_scans) * tr  # here are the corresponding frame times


##########################################################################
# Create design matrix
##########################################################################

# Set Up Events File

# Import task output
task_outp_files = glob.glob(data_dir+'*-errors.csv')

events_all = []

for n_run in range(len(task_outp_files)):
    # Find run number
    run_str = task_outp_files[n_run].split('-errors.csv')[0][-1]
    
    
    task_outp = pd.read_csv(task_outp_files[n_run])
    
    # Filter for relevant columns
    task_outp_fltr = task_outp[['ConditionName', 'ItemStart', 'ItemDur',
                                'FirstButtonPressTime',
                                'FeedbackStart', 'FeedbackDur', 'Correct_RT', 
                                'redcap_v_task']]
    
    # Create the events dataframe with the appropriate columns
    decision_trials = [list(task_outp_fltr['ConditionName']),
                       list(task_outp_fltr['ItemStart']),
                       list(task_outp_fltr['ItemDur'])]
    
    decision_df = pd.DataFrame(np.array(decision_trials).T, 
                          columns=['trial_type', 'onset', 'duration'])
    
    response_trials = [len(list(task_outp_fltr['FirstButtonPressTime'])) * ['ButtonPress'],
                       list(task_outp_fltr['FirstButtonPressTime']),
                       len(list(task_outp_fltr['FirstButtonPressTime'])) * [0]]
    
    response_df = pd.DataFrame(np.array(response_trials).T, 
                          columns=['trial_type', 'onset', 'duration'])
    
    feedback_trials = [list(task_outp_fltr['ConditionName']+'-fb'), 
                       list(task_outp_fltr['FeedbackStart']),
                       list(task_outp_fltr['FeedbackDur'])]
    
    feedback_df = pd.DataFrame(np.array(feedback_trials).T, 
                          columns=['trial_type', 'onset', 'duration'])
    
    # Merge dataframes for combined decision and feedback trial events
    events = pd.concat([decision_df, feedback_df], ignore_index=True)
    
    # Convert columns to numeric
    events['onset'] = pd.to_numeric(events['onset'])
    events['duration'] = pd.to_numeric(events['duration'])
    
    # Add missing fixation conditions
    # This will be done by adding the duration of one trial to the onset time, and
    # if that number is much less than the next onset, a fixation will be added
    
    # Sort events by onset time
    events = events.sort_values(by=['onset'], ignore_index=True)
    
    # Loop through each trial
    for n in range(len(events)):
        # Add duration to onset
        total_trial_time = events.loc[n,'onset'] + events.loc[n,'duration']
        
        # Check to see if it is much different from the next onset
        fix_after_trial = events.loc[n+1,'onset'] - total_trial_time
        if fix_after_trial > 0.1:
            # Add new fixation trial at the end of the df
            events.loc[len(events.index)] = ['fixation', total_trial_time, 
                                             fix_after_trial] 
    
    events = pd.concat([events, response_df], ignore_index=True)
    
    # Export events file
    event_file_name = 'sub-'+subj.replace('_','')+'_task-'+task+'_run-'+run_str+'_desc-events'
    events.to_csv(outp_dir + event_file_name + '.csv', index=False)
    
    events_all.append(events)    
    


import csv

events_afni = {}

#unique_conds = events_all[0]['trial_type'].unique()

#for cond in unique_conds:
#    events_afni[cond] = pd.DataFrame()

for n_run in range(len(events_all)):
    # Convert to AFNI 1D file
    
    temp_events = events_all[n_run]    
    
    unique_conds = events_all[0]['trial_type'].unique()
    
    for cond in unique_conds:
        temp_cond_df = temp_events[temp_events['trial_type'] == cond]
        
        temp_outp = list(temp_cond_df['onset'])

        with open(outp_dir+cond+'.1D', 'a', newline='') as f:
            #writer = csv.writer(f)
            f.write(' '.join(str(i) for i in temp_outp)+'\n')
        

