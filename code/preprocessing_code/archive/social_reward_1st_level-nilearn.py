# -*- coding: utf-8 -*-
"""
Spyder Editor

First and Second Level Analysis with nltools
"""

#from nltools.data import Brain_Data
import glob
import os
import sys

#from nilearn import plotting as niplt
#import matplotlib.pyplot as plt
import pandas as pd
#import seaborn as sns
import numpy as np


subj = 'sub-'+str(sys.argv[1])
task = str(sys.argv[2])

#subj = 'sub-010'
#task = 'social'


bids_dir = '/data/projects/social_doors/'
os.chdir(bids_dir)

all_runs_dir = bids_dir + 'derivatives/social_doors-nilearn/'

print('Starting 1st-level analysis for '+subj)
if not os.path.exists(all_runs_dir+subj):
    os.makedirs(all_runs_dir+subj)



func_runs = [f for f in glob.glob(bids_dir + '/derivatives/fmriprep/'+subj+'/func/'+subj+'_task-'+task+'*space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz', recursive=True)]
#func_runs = list('derivatives/fmriprep/'+subj+'/ses-001/func/'+subjs_scan_info[subjs_scan_info['subject']==subj]['run'].str[:-5]+'_space-T1w_desc-preproc_bold.nii.gz')
func_runs.sort()
#func_runs = func_runs[1:] + [func_runs[0]]



#func_run_nums =  [s.lstrip('0') for s in subjs_scan_info[subjs_scan_info['subject']==subj]['run'].str[-8:-5]]
#func_run_nums = [int(i) for i in func_run_nums]
print('Number of functional runs for '+subj+': '+str(len(func_runs)))


# Load the brain data
## Takes about 10 mins for all four datasets

# Grab subject's T1 as a mask to keep analysis in subject space
subj_t1 = bids_dir+"derivatives/fmriprep/"+subj+"/anat/"+subj+"_space-MNI152NLin2009cAsym_label-GM_probseg_bin.nii.gz"
#subj_t1 = "derivatives/reliability_analysis/relscenarios/Anatomy/"+subj+"_space-MNI152NLin2009cAsym_label-GM_probseg_bin.nii"







## Visualize data in jupyter notebook
#stats['beta'][77].iplot()




# F-test for multiple conditions
## Valence (positive/negative) x outcome (correct/incorrect)



from nilearn.glm.first_level import FirstLevelModel
fmri_glm = FirstLevelModel(mask_img=subj_t1,
                           t_r = 2.1,
                           slice_time_ref=0.5,
                           noise_model='ar1',
                           standardize=False,
                           hrf_model='spm',
                           drift_model='polynomial',
                           high_pass=0.01)


event_files = [f for f in glob.glob(bids_dir + '/Nifti/'+subj+'/func/'+subj+'_task-'+task+'*events.tsv', recursive=True)]
#func_runs = list('derivatives/fmriprep/'+subj+'/ses-001/func/'+subjs_scan_info[subjs_scan_info['subject']==subj]['run'].str[:-5]+'_space-T1w_desc-preproc_bold.nii.gz')
event_files.sort()


fmri_run_data_dir = bids_dir+"derivatives/fmriprep/"+subj+"/func/"


motion_reg_names = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z']
confounds = []
events = []

for n in range(len(func_runs)):
    motion_reg = pd.read_csv(fmri_run_data_dir+subj+"_task-"+task+"_run-"+str(n+1)+"_desc-confounds_timeseries.tsv", sep="\t")
    confounds.append(motion_reg[motion_reg_names])
                     
    temp_event_file = pd.read_csv(event_files[n], sep='\t')
    temp_event_file = temp_event_file[temp_event_file["trial_type"].str.contains("fixation") == False]
    events.append(temp_event_file)


fmri_glm = fmri_glm.fit(func_runs, events, confounds)


design_matrix = fmri_glm.design_matrices_[0]


#import matplotlib.pyplot as plt
#from nilearn.plotting import plot_design_matrix

#plot_design_matrix(design_matrix)

#plt.show()

# Save the betas maps for relevant conditions
relv_conds = ['positive','positive_win','positive_loss',
              'negative','negative_win','negative_loss']

n_conds = len(design_matrix.columns)

contrasts = {}

for cond in relv_conds:
    contrasts[cond] = np.zeros(n_conds)
    cond_idx = [design_matrix.columns.to_list().index(cond)]
    contrasts[cond][cond_idx] = 1


conditions = {}
n = 0
for cond in design_matrix.columns:
    conditions[cond] = np.zeros(n_conds)
    conditions[cond][n] = 1
    n += 1


effects_of_interest = np.vstack((conditions['positive_win'],
                                 conditions['positive_loss'],
                                 conditions['negative_win'],
                                 conditions['negative_loss']))

contrasts['valence_x_outcome'] = effects_of_interest


# Trial positive wins versus loses
c_pos_winVlos = np.zeros(n_conds)
pos_win_idx = design_matrix.columns.to_list().index('positive_win')
pos_los_idx = design_matrix.columns.to_list().index('positive_loss')
c_pos_winVlos[pos_win_idx] = 1
c_pos_winVlos[pos_los_idx] = -1

contrasts['positive_winVlos'] = c_pos_winVlos


# Trial all wins versus loses
c_all_winVlos = np.zeros(n_conds)
win_idx = [design_matrix.columns.get_loc(c) for c in design_matrix.columns if 'win' in c]
los_idx = [design_matrix.columns.get_loc(c) for c in design_matrix.columns if 'loss' in c]
c_all_winVlos[win_idx] = 1
c_all_winVlos[los_idx] = -1

contrasts['all_winVlos'] = c_all_winVlos


for n in range(len(contrasts)):
    cont_name = list(contrasts.keys())[n]
    z_map = fmri_glm.compute_contrast(contrasts[cont_name], output_type='z_score')

    z_map.to_filename(os.path.join(all_runs_dir,subj,'zmap_'+task+'_'+cont_name+'.nii.gz'))

#from nilearn import plotting

#plotting.plot_stat_map(
#    z_map, threshold=3.0,
#    title='fixed effects')

#plotting.show()








