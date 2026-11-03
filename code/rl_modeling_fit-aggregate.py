#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 10:22:26 2026

@author: hpopal
"""



import pandas as pd
import numpy as np
import os
import glob



proj_dir = '/data/software-research/hpopal/SCN/hpopal/'

data_dir = os.path.join(proj_dir, 'derivatives', 'task_socialreward', 'data')
outp_dir = os.path.join(proj_dir, 'derivatives', 'rl_modeling')

os.chdir(proj_dir)



# Import participant id data
subj_df = pd.read_csv(proj_dir+'participants.tsv', sep='\t')

# Fix participant IDs to match the directories in the data folder (e.g. sub-SCN101 -> SCN_101)
subj_df['participant_id'] = [x[4:7]+'_'+x[7:] for x in subj_df['participant_id']]

# Create subject list
subj_list = subj_df['participant_id'].unique()

subj_df['participant_id'] = 'sub-'+subj_df['participant_id'].str.replace('_','')



print('Found '+str(len(subj_list))+' participants')



model_fit_files = glob.glob(outp_dir + '/model_fit_results/sub-*/*_fit_results.csv')
model_fit_files.sort()

print(len(model_fit_files))

model_fit_results = pd.DataFrame()

for temp_file in model_fit_files:
    temp_data = pd.read_csv(temp_file)

    model_fit_results = pd.concat([model_fit_results, temp_data])



# Find the best parameters for each participant
subj_fit_params = pd.DataFrame(columns=['participant_id', 'model', 'alpha', 'beta', 'intercept',
                                        'mse','BIC'])
i_row = 0

for subj in model_fit_results['participant_id'].unique():
    temp_subj_data = model_fit_results[model_fit_results['participant_id'] == subj]

    for temp_model in temp_subj_data['model'].unique():
        temp_model_data = temp_subj_data[temp_subj_data['model'] == temp_model]
        temp_params = temp_model_data[temp_model_data['mse'] == temp_model_data['mse'].min()]

        subj_fit_params.loc[i_row, 'participant_id'] = subj
        subj_fit_params.loc[i_row, 'model'] = temp_model
        subj_fit_params.loc[i_row, 'alpha'] = temp_params.iloc[0]['alpha']
        subj_fit_params.loc[i_row, 'beta'] = temp_params.iloc[0]['beta']
        subj_fit_params.loc[i_row, 'intercept'] = temp_params.iloc[0]['intercept']
        subj_fit_params.loc[i_row, 'mse'] = temp_params.iloc[0]['mse']
        subj_fit_params.loc[i_row, 'BIC'] = temp_params.iloc[0]['BIC']
        i_row += 1

subj_fit_params = subj_fit_params.merge(subj_df, on='participant_id')
subj_fit_params[['alpha','beta','intercept']] = subj_fit_params[['alpha','beta','intercept']].apply(pd.to_numeric)

subj_fit_params.to_csv(outp_dir+'/model_fit_results/subject_best_fits.csv', index=False)

