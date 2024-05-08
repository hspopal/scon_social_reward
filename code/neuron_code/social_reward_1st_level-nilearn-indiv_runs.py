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
from nilearn.plotting import plot_design_matrix
from matplotlib import pyplot as plt

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

##########################################################################
# Set up
##########################################################################

# Take script inputs
subj = 'sub-SCN'+str(sys.argv[1])
task = 'SR'

# For beta testings
#subj = 'sub-SCN101'
#task = 'social'

# Define fmriprep template space
template = 'MNIPediatricAsym_cohort-5_res-2'

# Set BIDS project directory
bids_dir = '/data/neuron/SCN/SR/'
os.chdir(bids_dir)

# Set output directory
outp_dir = bids_dir + 'derivatives/SR_univariate/'+subj+'/'


##########################################################################
# Set scan specific paramters
##########################################################################

tr = 1.25  # repetition time is 1 second
n_scans = 241  # the acquisition comprises 128 scans
frame_times = np.arange(n_scans) * tr  # here are the corresponding frame times
slice_time_ref = 0.5  # Slice time correction to middle of TR

##########################################################################
# Find subject specific data
##########################################################################

print('Starting 1st-level analysis for '+subj)

# Make participant-specific directory for output if it doesn't exist
if not os.path.exists(outp_dir):
    os.makedirs(outp_dir)

# Find QC data for participant
qc_data = pd.read_csv(os.path.join(bids_dir, 'derivatives', 'participants_good.csv'))

# Filter for only participant QC data
subj_qc_data = qc_data[qc_data['participant_id'] == subj]

# Find all of the preprocessed functional runs
#func_runs = [f for f in glob.glob(bids_dir + '/derivatives/fmriprep/'+subj+'/func/'+subj+'_task-'+task+'*space-'+template+'_desc-preproc_bold.nii.gz', recursive=True)]
#func_runs.sort()
#print('Number of functional runs for '+subj+': '+str(len(func_runs)))

# Grab subject's T1 as a mask to keep analysis in subject space
subj_t1 = bids_dir+'derivatives/fmriprep/'+subj+'/anat/'+subj+'_space-'+template+'_label-GM_probseg_bin.nii.gz'

# Find the task event files that are ready to become design matrices
#event_files = [f for f in glob.glob(bids_dir + '/derivatives/task_socialreward/data/SCN_'+subj[-3:]+'/'+subj+'_task-'+task+'_run-*_desc-events'+'.csv', recursive=True)]
#event_files.sort()

# Set path to subject specific fmriprep output
fmri_run_data_dir = bids_dir+'derivatives/fmriprep/'+subj+'/func/'

# Set motion parameters to regress out
motion_reg_names = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z',
                    'trans_x_derivative1','trans_y_derivative1','trans_z_derivative1',
                    'rot_x_derivative1','rot_y_derivative1','rot_z_derivative1',
                    'white_matter','csf','scrub']

# Create empty lists to append run data
func_runs = []
events = []
confounds = []
design_matrices = []

# Set the relevant conditions (not contrasts)
relv_conds = ['HighReward_Computer','HighReward_Computer-fb',
              'HighReward_DisPeer','HighReward_DisPeer-fb',
              'HighReward_SimPeer','HighReward_SimPeer-fb',
              'LowReward_Computer','LowReward_Computer-fb',
              'LowReward_DisPeer','LowReward_DisPeer-fb',
              'LowReward_SimPeer','LowReward_SimPeer-fb']


##########################################################################
# Loop through funcitonal runs
##########################################################################

for n in range(len(subj_qc_data)):
    
    # Specify run number
    run_num = subj_qc_data['run'].iloc[n][-1]
    
    # Find preprocessed functional run
    func_run = bids_dir + '/derivatives/fmriprep/'+subj+'/func/'+subj+'_task-'+task+'_run-'+run_num+'_space-'+template+'_desc-preproc_bold.nii.gz'
    func_runs.append(func_run)
    
    # Import the event file as a dataframe
    event_path = os.path.join(bids_dir, 'derivatives', 'task_socialreward', 'data',
                              'SCN_'+subj[-3:], subj+'_task-'+task+'_run-'+run_num+'_desc-events'+'.csv')
    event_file = pd.read_csv(event_path)
    event_file = event_file[event_file['trial_type'].str.contains('fixation') == False]
    events.append(event_file)
    
    # Set motion parameters and input as a dataframe
    motion_reg = pd.read_csv(fmri_run_data_dir+subj+'_task-'+task+'_run-'+run_num+'_desc-confounds_timeseries.tsv', sep='\t')
    
    # Add a regressor to "scrub" TRs with large framewise displacement
    motion_reg['scrub'] = 0.0
    motion_reg.loc[motion_reg['framewise_displacement'] > 0.5, 'scrub'] = 1.0
    
    # Fill na values
    motion_reg = motion_reg.fillna(0)
    
    confound_file = motion_reg[motion_reg_names]
    
    # Filter for just the motion regressors specified above and add to a 
    # general confounds list
    confounds.append(confound_file)

    
    # Set the first level model parameters
    fmri_glm = FirstLevelModel(t_r=tr,
                               mask_img=subj_t1,
                               slice_time_ref=slice_time_ref,
                               noise_model='ar1',
                               standardize=False,
                               hrf_model='spm',
                               drift_model='polynomial',
                               high_pass=0.01)

    # Conduct the GLM using the functional data, event file, and the confounds
    fmri_glm = fmri_glm.fit(func_run, event_file, confound_file)

    # Specify the design matrix to pull conditions and contrasts later
    design_matrix = fmri_glm.design_matrices_[0]
    
    # Plot and save design matrix
    plot_design_matrix(design_matrix)
    plt.savefig(os.path.join(outp_dir, 
                             'task-'+task+'_run-'+run_num+'_design_matrix.png'))
    
    
    # Find the total number of conditions in the design matrix
    n_conds = len(design_matrix.columns)


    # Set contrasts for each condition, to make a beta map for each condition
    # This loop sets a column of 1s for each condition separately, so that
    # each condition can be examined separately 
    contrasts = {}
    for cond in relv_conds:
        contrasts[cond] = np.zeros(n_conds)
        cond_idx = [design_matrix.columns.to_list().index(cond)]
        contrasts[cond][cond_idx] = 1


    # Create z-scored beta maps contrasts
    for n_cont in range(len(contrasts)):
        cont_name = list(contrasts.keys())[n_cont]
        z_map = fmri_glm.compute_contrast(contrasts[cont_name], output_type='z_score')
    
        z_map.to_filename(os.path.join(outp_dir,'zmap_'+task+'_'+cont_name+'_run-'+run_num+'.nii.gz'))
    
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
    

##############################################################################
# Create specific contrasts
##############################################################################

# Create a list of conditions that will be tested against each other
# The index of each list will be the contrast (e.g. cond_a_list[0] > cond_b_list[0])
cond_a_list = ['HighReward_SimPeer-fb', 'HighReward_SimPeer-fb', 
               'HighReward_SimPeer', 'HighReward_SimPeer', 
               'LowReward_DisPeer', 'LowReward_DisPeer-fb']
cond_b_list = ['HighReward_DisPeer-fb', 'HighReward_Computer-fb', 
               'HighReward_DisPeer', 'HighReward_Computer',
               'LowReward_Computer', 'LowReward_Computer-fb']
contrasts_df = pd.DataFrame(list(zip(cond_a_list, cond_b_list)), 
                            columns=['cond_a','cond_b'])

# Create a dictionary that will store the contrast arrays
contrasts_bw_conds = {}

dm_cols = list(design_matrices[0].columns)

# Loop through and fill in 1s and 0s for contrasts
for n in range(len(contrasts_df)):
    # Find the condition names to be contrasted
    cond_a = contrasts_df.loc[n,'cond_a']
    cond_b = contrasts_df.loc[n,'cond_b']
    
    # Create an array of zeros
    contrasts_bw_conds[cond_a+'_V_'+cond_b] = np.zeros(len(dm_cols))
    
    # Find the index of each condtion as defined before
    temp_idx_a = dm_cols.index(cond_a)
    temp_idx_b = dm_cols.index(cond_b)
    
    # Fill the exact condition index in the contrast array with a 1 or -1
    contrasts_bw_conds[cond_a+'_V_'+cond_b][temp_idx_a] = 1
    contrasts_bw_conds[cond_a+'_V_'+cond_b][temp_idx_b] = -1


# Conduct positive (HighReward) vs negative (LowReward) contrast
pos_conds_idx = [dm_cols.index(x) for x in dm_cols if 'HighReward' in x]
pos_conds = [dm_cols[i] for i in pos_conds_idx]
pos_conds_idx = [dm_cols.index(x) for x in pos_conds if '-fb' in x]

neg_conds_idx = [dm_cols.index(x) for x in dm_cols if 'LowReward' in x]
neg_conds = [dm_cols[i] for i in neg_conds_idx]
neg_conds_idx = [dm_cols.index(x) for x in neg_conds if '-fb' in x]

contrasts_bw_conds['HighReward-fb_V_LowReward-fb'] = np.zeros(len(dm_cols))
contrasts_bw_conds['HighReward-fb_V_LowReward-fb'][pos_conds_idx] = 1
contrasts_bw_conds['HighReward-fb_V_LowReward-fb'][neg_conds_idx] = -1


# Create contrast maps
for n_cont in range(len(contrasts_bw_conds)):
    cont_name = list(contrasts_bw_conds.keys())[n_cont]
    z_map = fmri_glm.compute_contrast(contrasts_bw_conds[cont_name], output_type='z_score')

    z_map.to_filename(os.path.join(outp_dir,'zmap_'+task+'_'+cont_name+'_run-all.nii.gz'))





