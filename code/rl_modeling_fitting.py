#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 10:22:26 2025

@author: hpopal
"""

import pandas as pd
import numpy as np
import os
import glob
from scipy.optimize import minimize


import importlib
import rl_functions
importlib.reload(rl_functions)

import sys
import getopt


def read_inputs(argv):
    arg_input = ""
    arg_output = ""
    arg_user = ""
    arg_help = "{0} -p <participant_id> -a <alpha> -b <beta> -i <intercept>".format(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "hp:a:b:i:", ["help", "participant_id=", 
        "alpha=", "beta="])
    except:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-p", "--participant_id]"):
            subj_id = arg
        elif opt in ("-a", "--alpha"):
            alpha_guess = arg
        elif opt in ("-b", "--beta"):
            beta_guess = arg
        elif opt in ("-i", "--intercept"):
            inter_guess = arg

    return(subj_id, alpha_guess, beta_guess, inter_guess)


if __name__ == "__main__":
    subj_id, alpha_guess, beta_guess, inter_guess = read_inputs(sys.argv)


subj = 'SCN_'+subj_id
bids_id = 'sub-SCN'+subj_id

print('Calculating model fit: '+bids_id + ', alpha='+str(alpha_guess) + ', beta='+str(beta_guess) + ', intercept='+str(inter_guess))



if os.path.isdir('/Users/hpopal'):
    proj_dir = '/Users/hpopal/Google Drive/My Drive/dscn_lab/projects/scon_social_reward/'
else:
    proj_dir = '/data/software-research/hpopal/SCN/hpopal/'

data_dir = os.path.join(proj_dir, 'derivatives', 'task_socialreward', 'data')
outp_dir = os.path.join(proj_dir, 'derivatives', 'rl_modeling', 'model_fit_results', bids_id)

# Make participant-specific directory for output if it doesn't exist
if not os.path.exists(outp_dir):
    os.makedirs(outp_dir)

os.chdir(proj_dir)



# Simulate Data

def simulate_data(n_trials):
    # Define the proportion of positive and negative feedback for each peer condition
    # 96 is used as the denominator bceause that is the number of trials in the task, but
    # more trials can be simulated here
    prop_ps_pos = 24/96
    prop_ps_neg = 8/96
    prop_pd_pos = 8/96
    prop_pd_neg = 24/96
    prop_c_pos = 16/96
    prop_c_neg = 16/96

    # Define an empty dataframe
    peer_data = []
    fb_data = []

    # Add feedback data for positive and negative feedback
    peer_data = peer_data + (['SimPeer'] * int(prop_ps_pos * n_trials))
    fb_data = fb_data + ([1] * int(prop_ps_pos * n_trials))
    peer_data = peer_data + (['SimPeer'] * int(prop_ps_neg * n_trials))
    fb_data = fb_data + ([-1] * int(prop_ps_neg * n_trials))
    peer_data = peer_data + (['DisPeer'] * int(prop_pd_pos * n_trials))
    fb_data = fb_data + ([1] * int(prop_pd_pos * n_trials))
    peer_data = peer_data + (['DisPeer'] * int(prop_pd_neg * n_trials))
    fb_data = fb_data + ([-1] * int(prop_pd_neg * n_trials))
    peer_data = peer_data + (['Computer'] * int(prop_c_pos * n_trials))
    fb_data = fb_data + ([1] * int(prop_c_pos * n_trials))
    peer_data = peer_data + (['Computer'] * int(prop_c_neg * n_trials))
    fb_data = fb_data + ([-1] * int(prop_c_neg * n_trials))

    sim_data_dict = {'Peer': peer_data, 'Feedback': fb_data} 
    sim_data = pd.DataFrame(sim_data_dict)

    # Create item interest data
    n_pos_data = len(sim_data[sim_data['Feedback'] == 1])
    n_neg_data = len(sim_data[sim_data['Feedback'] == -1])

    interest_pos = [1] * int(.75 * n_pos_data) + [2] * int(.25 * n_pos_data)
    interest_neg = [-1] * int(.75 * n_neg_data) + [-2] * int(.25 * n_neg_data)

    # Randomize
    np.random.shuffle(interest_pos)
    np.random.shuffle(interest_neg)

    sim_data['Interest'] = 0
    sim_data.loc[sim_data[sim_data['Feedback'] == 1].index,'Interest'] = interest_pos
    sim_data.loc[sim_data[sim_data['Feedback'] == -1].index,'Interest'] = interest_neg

    sim_data = sim_data.sample(frac=1).reset_index(drop=True)

    sim_data['Trial'] = (range(1,n_trials+1))

    return(sim_data)


# Define number of simulations, and trials per simulation
n_sims = 1000
n_trials = 96


# Import simulated data
sim_data = pd.read_csv(outp_dir + '/../../simulated_data.csv')




# Define fit function

def fit_model(params, n_trials, model, rt_act, sim_data):
    alpha, beta, intercept = params
    # Get simulated data
    model_data, model_data_long = rl_functions.run_rl_model(model=model, alphas=[alpha], beta=beta,
                                               intercept=intercept, neg_reward=False, sim_data=sim_data)
    
    # Pull the simulated RTs
    rt_sim = model_data['RT']
    
    
    # Compute the error between actual and predicted RTs
    mse = np.mean((np.array(rt_act) - np.array(rt_sim))**2)
    
    return mse




# Define models to test
relv_titles = ['Model 1: Rescorla-Wagner + Condition Differentiation',
               'Model 2: Rescorla-Wagner + Reaction Time Value', 
               'Model 3: Rescorla-Wagner + Reaction Time Item Value',
               'Model 4: Rescorla-Wagner + Social Preference',
               'Model 5: Rescorla-Wagner + Reaction Time Surprise']
model_list = [rl_functions.rw_rtvaldiff_model, 
              rl_functions.rw_rt_model,
              rl_functions.rw_item_model,
              rl_functions.rw_rt_modreward2_model,
              rl_functions.rw_spr_model]
models_dict = dict(zip(relv_titles, model_list))





# gradient descent to minimize MSE
res_mse = np.inf # set initial MSE to be inf

model_fit_results = pd.DataFrame(columns=['model','participant_id','alpha','beta','intercept','mse'])

n_row = 0


                
init_guess = (float(alpha_guess), float(beta_guess), float(inter_guess))

# Capure participant's actual reaction times
subj_files = glob.glob(data_dir+'/'+subj+'/*-errors.csv')
subj_files.sort()
            
if len(subj_files) >= 1:
    
            
    subj_data = pd.DataFrame()

    for i_path in subj_files:
        temp_data = pd.read_csv(i_path, index_col=0)
        subj_data = pd.concat([subj_data, temp_data], ignore_index=True)

    subj_data['First_RT'] = subj_data['First_RT'].fillna(0)
    actual_rt = subj_data['First_RT']
                
    # If participant data is different than expected, cut
    if len(actual_rt) >= n_trials:
        cut_off = n_trials
    else:
        cut_off = len(actual_rt)
                
    for model_name in models_dict.keys():
            
                        
        # minimize MSE
        result = minimize(fit_model, init_guess, 
                        args=(len(actual_rt[:cut_off]), models_dict[model_name], 
                                actual_rt[:cut_off],
                                sim_data[sim_data['n_sim'] == 0].iloc[:cut_off]), 
                        bounds=((0,1),(0,1),(0,1)))
            
        # Compute BIC
        BIC = len(init_guess) * np.log(len(actual_rt)) + 2*result.fun
            
        model_fit_results.loc[n_row,'model'] = model_name
        model_fit_results.loc[n_row,'participant_id'] = 'sub-SCN'+subj_id
        model_fit_results.loc[n_row,'alpha'] = alpha_guess
        model_fit_results.loc[n_row,'beta'] = beta_guess
        model_fit_results.loc[n_row,'intercept'] = inter_guess
        model_fit_results.loc[n_row,'mse'] = result.fun
        model_fit_results.loc[n_row,'BIC'] = BIC
            
        n_row += 1
            
        # if current negLL is smaller than the last negLL,
        # then store current data
        if result.fun < res_mse:
            res_mse = result.fun
            param_fits = result.x

        model_str = model_name.split(':')[0].replace(" ", "-")
        model_fit_results.to_csv(outp_dir+'/'+'sub-SCN'+subj_id+'_a-'+str(alpha_guess)+'_b-'+str(beta_guess)+'_i-'+str(inter_guess)+'_fit_results.csv', 
                                 index=False)





