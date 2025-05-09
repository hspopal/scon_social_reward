#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 16 10:22:26 2025

@author: hpopal
"""

import sys
import pandas as pd
import numpy as np
import os
import glob

from scipy import stats
from scipy.optimize import minimize


import importlib
import rl_functions
importlib.reload(rl_functions)

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

print('Calculating parameter recovery: '+bids_id + ', alpha='+str(alpha_guess) + ', beta='+str(beta_guess) + ', intercept='+str(inter_guess))



if os.path.isdir('/Users/hpopal'):
    proj_dir = '/Users/hpopal/Google Drive/My Drive/dscn_lab/projects/scon_social_reward/'
else:
    proj_dir = '/data/neuron/SCN/SR/'

data_dir = os.path.join(proj_dir, 'derivatives', 'task_socialreward', 'data')
outp_dir = os.path.join(proj_dir, 'derivatives', 'rl_modeling', 'parameter_recovery', bids_id)

# Make participant-specific directory for output if it doesn't exist
if not os.path.exists(outp_dir):
    os.makedirs(outp_dir)

os.chdir(proj_dir)


# Import participant id data
subj_df = pd.read_csv(proj_dir+'participants.tsv', sep='\t')

# Fix participant IDs to match the directories in the data folder (e.g. sub-SCN101 -> SCN_101)
subj_df['participant_id'] = [x[4:7]+'_'+x[7:] for x in subj_df['participant_id']]

# Create subject list
subj_list = subj_df['participant_id'].unique()


# Model simulation function

def run_rl_model(model, alphas, beta, neg_reward, sim_data):
    # Create empty dataframe to store data
    model_data = pd.DataFrame()

    n_sims = sim_data['n_sim'].max() + 1

    for n_sim in range(n_sims):
        for alpha in alphas:
            # Filter for one simulation's data
            #sim_data = simulate_data(n_trials)
            sim_data_temp = sim_data[sim_data['n_sim'] == n_sim].copy()
            sim_data_temp = sim_data_temp.reset_index(drop=True)
            
            # Run models
            model_data_temp = model(sim_data_temp, alpha, beta, neg_reward=neg_reward)
        
            model_data_temp['n_sim'] = n_sim
            model_data_temp['alpha'] = alpha
        
            model_data = pd.concat([model_data, model_data_temp])

    # Turn index into time point
    model_data['trial'] = model_data.index
    model_data_long = pd.melt(model_data, id_vars=['n_sim','Peer','RPE','RT','alpha','trial','Interest'], 
                              var_name='Condition',
                              value_vars=['SimPeer','DisPeer','Computer'], value_name='Value')

    return(model_data, model_data_long)


# Define number of simulations, and trials per simulation
n_trials = 96


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



# Define fit function

def fit_model(params, n_trials, model, rt_act, sim_data):
    alpha, beta = params
    # Get simulated data
    model_data, model_data_long = run_rl_model(model=model, alphas=[alpha], beta=beta,
                                               neg_reward=False, sim_data=sim_data)
    
    # Pull the simulated RTs
    rt_sim = model_data['RT']
    
    
    # Compute the error between actual and predicted RTs
    mse = np.mean((np.array(rt_act) - np.array(rt_sim))**2)
    
    return mse


from scipy.optimize import minimize


# Define models to test
relv_titles = ['Model 1: Rescorla-Wagner + Condition Differentiation',
               'Model 2: Rescorla-Wagner + Reaction Time Value', 
               'Model 3: Rescorla-Wagner + Social Preference']
model_list = [rl_functions.rw_rtvaldiff_model, 
              rl_functions.rw_rt_model,
              rl_functions.rw_rt_modreward2_model]
models_dict = dict(zip(relv_titles, model_list))


# simulate subjects' alpha and theta params

# initialize lists to store params and data
mse_sim = []
Q_fit = []
alpha_fit = []
beta_fit = []
n_row = 0


# Import model fit results
model_fit_files = glob.glob(outp_dir + '/../../model_fit_results/'+bids_id+'*_fit_results.csv')
model_fit_files.sort()

model_fit_results = pd.DataFrame()

for temp_file in model_fit_files:
    temp_data = pd.read_csv(temp_file)

    model_fit_results = pd.concat([model_fit_results, temp_data])



model_rec_results = pd.DataFrame(columns=['participant_id','model','alpha_fit','beta_fit','mse'])

np.random.seed(int(subj_id))
    
# simulate subject data (for trial orders, not RT
simdata_rc = simulate_data(n_trials=n_trials)
simdata_rc['n_sim'] = 0
    
    
for model_name in models_dict.keys():
    temp_model_data = model_fit_results[model_fit_results['model'] == model_name]
    print(temp_model_data.head())
    alpha = temp_model_data['alpha'].iloc[0]
    beta = temp_model_data['beta'].iloc[0]
        
    model_data, model_data_long = run_rl_model(model=models_dict[model_name], alphas=[alpha], beta=beta, neg_reward=False,
                                    sim_data=simdata_rc)
        
    # gradient descent to minimize MSE
    res_mse = np.inf
        
    # guess several different starting points for alpha
    #for alpha_guess in np.arange(0,1.05,.05):
    
    #    for beta_guess in np.arange(0,1.05,.05):
            
    # guesses for alpha will change
    init_guess = (alpha_guess, beta_guess)
                
                
    # minimize MSE
    result = minimize(fit_model, init_guess, 
                      args=(len(simdata_rc), models_dict[model_name], model_data['RT'], simdata_rc), 
                      bounds=((0,1),(0,1)))
                
    # if current negLL is smaller than the last negLL,
    # then store current data
    if result.fun < res_mse:
        res_mse = result.fun
        param_fits = result.x
        #Q_vals = Q_sim
        
    # append model fits to lists
    #mse_sim.append(res_mse)
    #Q_fit.append(Q_vals)
    #alpha_fit.append(param_fits[0])
    #beta_fit.append(param_fits[1])
    
    model_rec_results.loc[n_row,'model'] = model_name
    model_rec_results.loc[n_row,'participant_id_sim'] = bids_id
    model_rec_results.loc[n_row,'alpha_sim'] = alpha_guess
    model_rec_results.loc[n_row,'beta_sim'] = beta_guess
    model_rec_results.loc[n_row,'alpha_fit'] = param_fits[0]
    model_rec_results.loc[n_row,'beta_fit'] = param_fits[1]
    model_rec_results.loc[n_row,'mse'] = res_mse

    n_row += 1

    model_rec_results.to_csv(outp_dir+'/'+bids_id+'_alpha-'+str(alpha_guess)+'_beta-'+str(beta_guess)+'.csv', index=False)



