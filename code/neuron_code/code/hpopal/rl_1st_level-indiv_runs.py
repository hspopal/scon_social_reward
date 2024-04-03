# -*- coding: utf-8 -*-
"""
Spyder Editor

First and Second Level Analysis with nilearn
"""

import glob
import os
import sys

import pandas as pd
import numpy as np

from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.first_level import compute_regressor
from nilearn.glm.first_level import make_first_level_design_matrix

##########################################################################
# Set up
##########################################################################

# Take script inputs
subj = 'sub-SCN'+str(sys.argv[1])
task = 'SR'

# For beta testings
#subj = 'sub-SCN215'
#task = 'social'

# Define fmriprep template space
template = 'MNIPediatricAsym_cohort-5_res-2'

# Set BIDS project directory
bids_dir = '/data/neuron/SCN/SR/'
os.chdir(bids_dir)

# Set output directory
outp_dir = bids_dir + 'derivatives/rl_modeling/'+subj+'/'


##########################################################################
# Set scan specific paramters
##########################################################################

tr = 1.25  # repetition time is 1 second
n_scans = 241  # the acquisition comprises 128 scans
#frame_times = np.arange(n_scans) * tr  # here are the corresponding frame times
slice_time_ref = 0.5

##########################################################################
# Find subject specific data
##########################################################################

print('Starting 1st-level analysis for '+subj)

# Make participant-specific directory for output if it doesn't exist
if not os.path.exists(outp_dir):
    os.makedirs(outp_dir)

# Find all of the preprocessed functional runs
func_runs = [f for f in glob.glob(bids_dir + '/derivatives/fmriprep/'+subj+'/func/'+subj+'_task-'+task+'*space-'+template+'_desc-preproc_bold.nii.gz', recursive=True)]
func_runs.sort()
print('Number of functional runs for '+subj+': '+str(len(func_runs)))

# Grab subject's T1 as a mask to keep analysis in subject space
subj_t1 = bids_dir+'derivatives/fmriprep/'+subj+'/anat/'+subj+'_space-'+template+'_label-GM_probseg_bin.nii.gz'

# Find the task event files that are ready to become design matrices
event_files = [f for f in glob.glob(bids_dir + '/derivatives/rl_modeling/SCN_'+subj[-3:]+'/'+subj+'_task-'+task+'_run-*_desc-events'+'.csv', recursive=True)]
event_files.sort()

# Set path to subject specific fmriprep output
fmri_run_data_dir = bids_dir+'derivatives/fmriprep/'+subj+'/func/'

# Set motion parameters to regress out
motion_reg_names = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z',
                    'trans_x_derivative1','trans_y_derivative1','trans_z_derivative1',
                    'rot_x_derivative1','rot_y_derivative1','rot_z_derivative1',
                    'white_matter','csf','scrub']
confounds = []
events = []

# Set the relevant conditions (not contrasts)
relv_conds = ['RPE', 'RPE_abs', 'ButtonPress']


##########################################################################
# Loop through funcitonal runs
##########################################################################
design_matrices = []
for n in range(len(func_runs)):
    # Set motion parameters and input as a dataframe
    motion_reg = pd.read_csv(fmri_run_data_dir+subj+'_task-'+task+'_run-'+str(n+1)+'_desc-confounds_timeseries.tsv', sep='\t')
    
    # Add a regressor to "scrub" TRs with large framewise displacement
    motion_reg['scrub'] = 0.0
    motion_reg.loc[motion_reg['framewise_displacement'] > 0.5, 'scrub'] = 1.0
    
    # Fill na values
    motion_reg = motion_reg.fillna(0)
    
    # Filter for just the motion regressors specified above and add to a 
    # general confounds list
    confounds.append(motion_reg[motion_reg_names])

    # Import the event file as a dataframe                 
    temp_event_file = pd.read_csv(event_files[n])
    temp_event_file = temp_event_file[temp_event_file['trial_type'].str.contains('fixation') == False]
    events.append(temp_event_file[['trial_type','onset','duration']])
    
    
    # Calcualte RPE regressor
    #frame_times = np.linspace(0.625,tr*n_scans, n_scans)
    start_time = slice_time_ref * tr
    end_time = (n_scans - 1 + slice_time_ref) * tr
    frame_times = np.linspace(start_time, end_time, n_scans)
    rpe_events = temp_event_file[temp_event_file['trial_type'].str.contains('fb')]
    rpe_events.loc[:,'RPE_abs'] = list(rpe_events['RPE'].abs())
    rpe_condition = rpe_events[['onset','duration','RPE']].to_numpy()
    signal_rpe, _labels = compute_regressor(rpe_condition.T, 'spm', frame_times, con_id='RPE')
    rpe_abs_condition = rpe_events[['onset','duration','RPE_abs']].to_numpy()
    signal_rpe_abs, _labels = compute_regressor(rpe_abs_condition.T, 'spm', frame_times, con_id='RPE_abs')
    #test['RPE'] = signal
    
    # Make design matrix
    design_matrix = make_first_level_design_matrix(frame_times, 
                                                        events[n], 
                                                        hrf_model='spm',
                                                        drift_model='polynomial',
                                                        high_pass=0.01,
                                                        add_regs=confounds[n].values,
                                                        add_reg_names=confounds[n].columns.tolist())
    
    # Add RPE regressor
    design_matrix.loc[:,'RPE'] = signal_rpe
    design_matrix.loc[:,'RPE_abs'] = signal_rpe_abs
    
    # If the "error" regressor does not exist, add a column of 0s 
    if 'error' not in design_matrix.columns:
        design_matrix['error'] = 0
        
    
    # Remove fb regressors
    design_matrix = design_matrix.loc[:,~design_matrix.columns.str.contains('-fb')]
    
    # Set the first level model parameters
    fmri_glm = FirstLevelModel(t_r=tr,
                               mask_img=subj_t1,
                               slice_time_ref=0.5,
                               noise_model='ar1',
                               standardize=False,
                               hrf_model='spm',
                               drift_model='polynomial',
                               high_pass=0.01)

    # Conduct the GLM using the functional data, event file, and the confounds
    fmri_glm = fmri_glm.fit(func_runs[n], design_matrices=design_matrix)

    # Specify the design matrix to pull conditions and contrasts later
    design_matrix = fmri_glm.design_matrices_[0]
    
    # Find the total number of conditions in the design matrix
    n_conds = len(design_matrix.columns)


    # Set contrasts for each condition, to make a beta map for each condition
    # This loop sets a column of 1s for each condition separately, so that
    # each condition can be examined separately 
    contrasts = {}
    for cond in ['RPE', 'RPE_abs', 'ButtonPress']:
        contrasts[cond] = np.zeros(n_conds)
        cond_idx = [design_matrix.columns.to_list().index(cond)]
        contrasts[cond][cond_idx] = 1

    

    # Create z-scored beta maps contrasts
    for n_cont in range(len(contrasts)):
        cont_name = list(contrasts.keys())[n_cont]
        z_map = fmri_glm.compute_contrast(contrasts[cont_name], output_type='z_score')
    
        z_map.to_filename(os.path.join(outp_dir,'zmap_'+task+'_'+cont_name+'_run-'+str(n+1)+'.nii.gz'))
    
    # Export design matrix image
    
    
    # Save design matrix for between run analysis
    design_matrices.append(design_matrix)

# Compute contrasts across all runs
fmri_glm = FirstLevelModel(t_r=tr,
                           mask_img=subj_t1,
                           slice_time_ref=0.5,
                           noise_model='ar1',
                           standardize=False,
                           hrf_model='spm',
                           drift_model='polynomial',
                           high_pass=0.01)

fmri_glm = fmri_glm.fit(func_runs, design_matrices=design_matrices)

for n_cont in range(len(contrasts)):
    cont_name = list(contrasts.keys())[n_cont]
    z_map = fmri_glm.compute_contrast(contrasts[cont_name], output_type='z_score')

    z_map.to_filename(os.path.join(outp_dir,'zmap_'+task+'_'+cont_name+'_run-all.nii.gz'))
    







