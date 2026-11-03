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

subj_num = str(sys.argv[1])

# For beta testings
#subj_num = '101'
subj_id_raw = 'SCN_'+subj_num
subj_id_bids = 'sub-SCN'+subj_num
task = 'SR'

# Set BIDS project directory
bids_dir = '/data/neuron/SCN/SR/'
os.chdir(bids_dir)

# Set output directory
data_dir = bids_dir + 'derivatives/rl_modeling/event_files/' + subj_id_raw + '/'
outp_dir = bids_dir + 'derivatives/rl_modeling/' + subj_id_bids + '/'

# If subject directory does not exist in output directory, create it
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    
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


for n_run in range(len(task_outp_files)):
    # Find run number
    run_str = task_outp_files[n_run].split('-errors.csv')[0][-1]
    rl_outp_file = glob.glob(bids_dir+'derivatives/rl_modeling/subject_model_fits/'+subj_id_bids+'/*Model 4*run-'+run_str+'.csv')[0]

    
    task_outp = pd.read_csv(task_outp_files[n_run])
    rl_outp = pd.read_csv(rl_outp_file)
    
    # Filter for relevant columns
    task_outp_fltr = task_outp[['ConditionName', 'ItemStart', 'ItemDur',
                                'ParticipantsFirstAnswer', 'FirstButtonPressTime',
                                'FeedbackStart', 'FeedbackDur', 'Correct_RT', 
                                'redcap_v_task']]
    task_outp_fltr['RPE'] = rl_outp['RPE'].copy()
    
    # Create the events dataframe with the appropriate columns
    decision_trials = [list(task_outp_fltr['ConditionName']),
                       list(task_outp_fltr['ItemStart']),
                       list(task_outp_fltr['ItemDur'])]
    
    decision_df = pd.DataFrame(np.array(decision_trials).T, 
                          columns=['trial_type', 'onset', 'duration'])
    
    response_trials = [list(task_outp_fltr['ParticipantsFirstAnswer']),
                       list(task_outp_fltr['FirstButtonPressTime']),
                       len(list(task_outp_fltr['FirstButtonPressTime'])) * [0]]
    
    response_df = pd.DataFrame(np.array(response_trials).T, 
                          columns=['trial_type', 'onset', 'duration'])
    
    # Remove trials with no button press
    response_df = response_df[~response_df['onset'].str.contains('nan')]
    response_df = response_df[~response_df['trial_type'].str.contains('nan')]
    
    feedback_trials = [list(task_outp_fltr['ConditionName']+'-fb'), 
                       list(task_outp_fltr['FeedbackStart']),
                       list(task_outp_fltr['FeedbackDur']),
                       list(task_outp_fltr['RPE'])]
    
    feedback_df = pd.DataFrame(np.array(feedback_trials).T, 
                          columns=['trial_type', 'onset', 'duration', 'RPE'])
    
    error_filter = task_outp_fltr[task_outp_fltr['redcap_v_task'] == 1]
    experror_trials = [len(error_filter) * 2 * ['error'], 
                       list(error_filter['ItemStart']) + list(error_filter['FeedbackStart']),
                       list(error_filter['ItemDur']) + list(error_filter['FeedbackDur'])]

    
    experror_df = pd.DataFrame(np.array(experror_trials).T, 
                          columns=['trial_type', 'onset', 'duration'])
    
    
    # Merge dataframes for combined decision and feedback trial events
    events = pd.concat([decision_df, feedback_df, experror_df], 
                       ignore_index=True)
    
    # Convert columns to numeric
    events['onset'] = pd.to_numeric(events['onset'])
    events['duration'] = pd.to_numeric(events['duration'])
    #events['error'] = pd.to_numeric(events['error'])
    events['RPE'] = pd.to_numeric(events['RPE'])
    
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
                                             fix_after_trial, 0] 
    
    events = pd.concat([events, response_df], ignore_index=True)
    
    events['onset'] = pd.to_numeric(events['onset'])
    events['duration'] = pd.to_numeric(events['duration'])
    
    
    # Replace empty RPE (NaN) with 0
    #events['error'] = events['error'].fillna(0)
    events['RPE'] = events['RPE'].fillna(0)
    
    # Create a duration for button presses
    events.loc[events['trial_type'] == 'ButtonPress', 'duration'] = 0.1
    
    # Export events file
    event_file_name = subj_id_bids+'_task-'+task+'_run-'+run_str+'_desc-events'
    events.to_csv(data_dir + event_file_name + '.csv', index=False)

    




