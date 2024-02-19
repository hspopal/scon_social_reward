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
subj = 'SCN_'+str(sys.argv[1])
#task = 'SR'

# For beta testings
#subj = 'SCN_101'
task = 'SR'

# Set BIDS project directory
bids_dir = '/data/neuron/SCN/SR/'
os.chdir(bids_dir)

# Set output directory
data_dir = bids_dir + 'derivatives/task_socialreward/data/' + subj + '/'
#outp_dir = bids_dir + 'derivatives/SR_first_level/' + 'sub-' + subj + '/'

# If subject directory does not exist in output directory, create it
#if not os.path.exists(outp_dir):
#    os.makedirs(outp_dir)
    
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
    
    
    task_outp = pd.read_csv(task_outp_files[n_run])
    
    # Filter for relevant columns
    task_outp_fltr = task_outp[['ConditionName', 'ItemStart', 'ItemDur',
                                'FeedbackStart', 'FeedbackDur', 'Correct_RT', 
                                'redcap_v_task']]
    
    # Create the events dataframe with the appropriate columns
    decision_trials = [list(task_outp_fltr['ConditionName']),
                       list(task_outp_fltr['ItemStart']),
                       list(task_outp_fltr['ItemDur'])]
    
    decision_df = pd.DataFrame(np.array(decision_trials).T, 
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
    
    # Export events file
    event_file_name = 'sub-'+subj.replace('_','')+'_task-'+task+'_run-'+run_str+'_desc-events'
    events.to_csv(data_dir + event_file_name + '.csv', index=False)

    
    """
    # Set up confounds
    confounds_files = glob.glob(os.path.join(bids_dir, 
                                'derivatives','fmriprep', 'sub-SCN101',
                                'func','*task-'+task+'_run-'+run_str+'_desc-confounds_timeseries.tsv'))
    confounds = pd.read_csv(confounds_files[0], sep='\t')
    
    motion = confounds[['trans_x', 'trans_y', 'trans_z',
                        'rot_x', 'rot_y', 'rot_z']]
    add_reg_names = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    
    
    # Create design matrix
    design_matrix = make_first_level_design_matrix(
                                        frame_times,
                                        events,
                                        drift_model="polynomial",
                                        drift_order=3,
                                        add_regs=motion,
                                        add_reg_names=add_reg_names,
                                        hrf_model='spm')
    
    dm_name = 'sub-'+subj+'_task-'+task+'_run-'+run_str+'_desc-design_matrix'
    design_matrix.to_csv(outp_dir + dm_name + '.csv')
    
    
    plot_design_matrix(design_matrix)
    plt.savefig(outp_dir + dm_name + '.png')
    """



