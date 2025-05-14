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
import seaborn as sns
import matplotlib.pyplot as plt


# Take script inputs
subj_id = str(sys.argv[1])
subj = 'SCN_'+subj_id


if os.path.isdir('/Users/hpopal'):
    proj_dir = '/Users/hpopal/Google Drive/My Drive/dscn_lab/projects/scon_social_reward/'
else:
    proj_dir = '/data/neuron/SCN/SR/'

data_dir = os.path.join(proj_dir, 'derivatives', 'task_socialreward', 'data')
outp_dir = os.path.join(proj_dir, 'derivatives', 'rl_modeling')

os.chdir(proj_dir)


# Import participant id data
subj_df = pd.read_csv(proj_dir+'participants.tsv', sep='\t')

# Fix participant IDs to match the directories in the data folder (e.g. sub-SCN101 -> SCN_101)
subj_df['participant_id'] = [x[4:7]+'_'+x[7:] for x in subj_df['participant_id']]

# Create subject list
subj_list = subj_df['participant_id'].unique()





# Define models

def rw_model(trial_list, alpha, beta, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))

    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    
    for t in range(len(trial_list)):
        # Capture trial info
        cond_t = trial_list.loc[t, 'Peer']
        value_t = V.loc[t, cond_t]
        feedback_t = trial_list.loc[t, 'Feedback']
        
        # If received no feedback on the trial, RPE = 0
        if np.isnan(feedback_t):
            RPE[t] = 0
        elif feedback_t < 0 and not neg_reward:  # If feedback is negative, make it 0
            RPE[t] = 0 - value_t
        else:
            RPE[t] = feedback_t - value_t

        # Update value of current condition
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * RPE[t]
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['RPE'] = RPE
    RL_output['RT'] = np.nan
    
    return RL_output


## Model 2

def rw_randrt_model(trial_list, alpha, beta, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))

    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5    
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))
    intercept = np.random.rand()

    # Define minimum and maxium reaction time for random sampling
    min_rt = 0.25
    max_rt = 2.0
    
    
    for t in range(len(trial_list)):
        # Capture trial info
        cond_t = trial_list.loc[t, 'Peer']

        # Create a random RT
        RT[t] = beta * np.random.uniform(min_rt,max_rt) + intercept

        # Calculate the current value
        #value_t = V.loc[t, cond_t] + np.log(RT[t])
        value_t = V.loc[t, cond_t]

        # Calculate RPE
        feedback_t = trial_list.loc[t, 'Feedback']
        
        # If received no feedback on the trial, RPE = 0
        if np.isnan(feedback_t):
            RPE[t] = 0
        elif feedback_t < 0 and not neg_reward:  # If feedback is negative, make it 0
            RPE[t] = 0 - value_t
        else:
            RPE[t] = feedback_t - value_t
        
        # Update value of current condition
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * RPE[t]
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['Feedback'] = trial_list['Feedback']
    RL_output['RPE'] = RPE
    RL_output['RT'] = RT
    
    return RL_output


## Model 3

def rw_rtvaldiff_model(trial_list, alpha, beta, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))

    # Set model parameters
    mu = 0
    
    for t in range(len(trial_list)):
        # Capture the trial info
        cond_t = trial_list.loc[t, 'Peer']

        # Create a RT based on the value of each condition
        cond_diff = np.abs(V.loc[t, 'SimPeer'] - V.loc[t, 'DisPeer'] - V.loc[t, 'Computer'])
        sigma = np.std(V['SimPeer'] - V['DisPeer'] - V['Computer'])
        RT[t] = beta * np.abs(np.abs(cond_diff) + np.random.normal(mu, 0.05))

        # Calculate the current value
        value_t = V.loc[t, cond_t]

        # Calculate RPE
        feedback_t = trial_list.loc[t, 'Feedback']
        
        # If received no feedback on the trial, RPE = 0
        if np.isnan(feedback_t):
            RPE[t] = 0
        elif feedback_t < 0 and not neg_reward:  # If feedback is negative, make it 0
            RPE[t] = 0 - value_t
        else:
            RPE[t] = feedback_t - value_t

        # Update value of current condition
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * RPE[t]
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['RPE'] = RPE
    RL_output['RT'] = RT
    
    return RL_output


## Model 4

def rw_rt_model(trial_list, alpha, beta, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))

    # Set model parameters
    intercept = np.random.rand()
    
    for t in range(len(trial_list)):
        # Capture the trial info
        cond_t = trial_list.loc[t, 'Peer']
        value_t = V.loc[t, cond_t]

        # Create a RT based on the value of each condition
        RT[t] = beta * -1 * value_t + intercept

        # Calculate RPE
        feedback_t = trial_list.loc[t, 'Feedback']
        
        # If received no feedback on the trial, RPE = 0
        if np.isnan(feedback_t):
            RPE[t] = 0
        elif feedback_t < 0 and not neg_reward:  # If feedback is negative, make it 0
            RPE[t] = 0 - value_t
        else:
            RPE[t] = feedback_t - value_t

        # Update value of current condition
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * RPE[t]
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['RPE'] = RPE
    RL_output['RT'] = RT
    
    return RL_output


## Model 5

def rw_rtsocial_model(trial_list, alpha, beta, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))

    # Set model parameters
    intercept = np.random.rand()
    
    for t in range(len(trial_list)):
        # Capture the trial info
        cond_t = trial_list.loc[t, 'Peer']
        value_t = V.loc[t, cond_t]
        
        if cond_t == 'DisPeer':
            beta_t = beta * -1
        elif cond_t == 'Computer':
            beta_t = 0
        else:
            beta_t = beta
        
        # Create a RT based on the value of each condition
        RT[t] = beta_t * -1 * value_t + intercept

        # Calculate RPE
        feedback_t = trial_list.loc[t, 'Feedback']
        
        # If received no feedback on the trial, RPE = 0
        if np.isnan(feedback_t):
            RPE[t] = 0
        elif feedback_t < 0 and not neg_reward:  # If feedback is negative, make it 0
            RPE[t] = 0 - value_t
        else:
            RPE[t] = feedback_t - value_t

        # Update value of current condition
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * RPE[t]
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['RPE'] = RPE
    RL_output['RT'] = RT
    
    return RL_output


## Model 6

def rw_item_model(trial_list, alpha, beta, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))

    # Set model parameters
    intercept = np.random.rand()
    
    for t in range(len(trial_list)):
        # Capture the trial info
        cond_t = trial_list.loc[t, 'Peer']
        value_t = V.loc[t, cond_t]
        item_val_t = trial_list.loc[t, 'Interest']

        # Create a RT based on the value of each condition
        RT[t] = beta * -1 * value_t * item_val_t + intercept

        # Calculate RPE
        feedback_t = trial_list.loc[t, 'Feedback']
        
        # If received no feedback on the trial, RPE = 0
        if np.isnan(feedback_t):
            RPE[t] = 0
        elif feedback_t < 0 and not neg_reward:  # If feedback is negative, make it 0
            RPE[t] = 0 - value_t
        else:
            RPE[t] = feedback_t - value_t

        # Update value of current condition
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * RPE[t]
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['RPE'] = RPE
    RL_output['RT'] = RT
    
    return RL_output


## Model 7

def rw_rt_modreward_model(trial_list, alpha, beta, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))

    # Set model parameters
    intercept = np.random.rand()
    
    for t in range(len(trial_list)):
        # Capture the trial info
        cond_t = trial_list.loc[t, 'Peer']
        value_t = V.loc[t, cond_t]

        # Create a RT based on the value of each condition
        RT[t] = beta * -1 * value_t + intercept

        # Calculate RPE
        feedback_t = trial_list.loc[t, 'Feedback']
        
        # If received no feedback on the trial, RPE = 0
        if np.isnan(feedback_t):
            RPE[t] = 0
        #elif feedback_t < 0 and not neg_reward:  # If feedback is negative, make it 0
        #    RPE[t] = 0 - value_t
        elif feedback_t < 0:
            feedback_t = 0.5
            RPE[t] = feedback_t - value_t
        else:
            RPE[t] = feedback_t - value_t

        # Update value of current condition
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * RPE[t]
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['RPE'] = RPE
    RL_output['RT'] = RT
    
    return RL_output


## Model 8

def rw_rt_modreward2_model(trial_list, alpha, beta, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))

    # Set model parameters
    intercept = np.random.rand()
    
    for t in range(len(trial_list)):
        # Capture the trial info
        cond_t = trial_list.loc[t, 'Peer']
        value_t = V.loc[t, cond_t]

        # Create a RT based on the value of each condition
        RT[t] = beta * -1 * value_t + intercept

        # Calculate RPE
        feedback_t = trial_list.loc[t, 'Feedback']
        
        # If received no feedback on the trial, RPE = 0
        if np.isnan(feedback_t):
            feedback_t = value_t
        #elif feedback_t < 0 and not neg_reward:  # If feedback is negative, make it 0
        #    RPE[t] = 0 - value_t
        if cond_t == 'Computer':
            if feedback_t < 0:
                feedback_t = 0
            else:
                feedback_t = 0.5
        else:
            if feedback_t < 0:
                feedback_t = 0.5
            else:
                feedback_t = 1

        RPE[t] = feedback_t - value_t

        # Update value of current condition
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * RPE[t]
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['RPE'] = RPE
    RL_output['RT'] = RT
    
    return RL_output




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
n_sims = 1000
n_trials = 96


# Check if simulated data already exists
if os.path.isfile(outp_dir + '/simulated_data.csv'):
    sim_data = pd.read_csv(outp_dir + '/simulated_data.csv')

else:
    # Create a dataframe to store all the simulation data
    sim_data = pd.DataFrame()

    # Produce simulation data
    for n_sim in range(n_sims):
        # Run simulation function
        temp_sim_data = simulate_data(n_trials)
        temp_sim_data['n_sim'] = n_sim

        # Comebine with the rest of the data
        sim_data = pd.concat([sim_data, temp_sim_data])

    # Export data
    sim_data.to_csv(outp_dir + '/simulated_data.csv', index=False)



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
relv_titles = ['Model 8: Reward Condition Dependent']
model_list = [rw_rt_modreward2_model]
models_dict = dict(zip(relv_titles, model_list))





# gradient descent to minimize MSE
res_mse = np.inf # set initial MSE to be inf

model_fit_results = pd.DataFrame(columns=['model','participant_id','alpha','beta','mse'])

n_row = 0

# guess several different starting points for alpha
for alpha_guess in np.arange(0,1.05,.05):
    for beta_guess in np.arange(0,1.05,.1):
        
        print('Fitting alpha='+str(alpha_guess)+' beta='+str(beta_guess)+' for '+subj)
        
        # guesses for alpha, theta will change on each loop
        init_guess = (alpha_guess, beta_guess)
        
        
        # Capure participant's actual reaction times
        subj_files = glob.glob(data_dir+'/'+subj+'/*-errors.csv')
        subj_files.sort()
        
        if len(subj_files) < 1:
            continue
        
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
                              bounds=((0,1),(0,1)))
    
            # Compute BIC
            BIC = len(init_guess) * np.log(len(actual_rt)) + 2*result.fun
    
            model_fit_results.loc[n_row,'model'] = model_name
            model_fit_results.loc[n_row,'participant_id'] = 'sub-SCN'+subj_id
            model_fit_results.loc[n_row,'alpha'] = alpha_guess
            model_fit_results.loc[n_row,'beta'] = beta_guess
            model_fit_results.loc[n_row,'mse'] = result.fun
            model_fit_results.loc[n_row,'mse'] = BIC
    
            n_row += 1
    
            # if current negLL is smaller than the last negLL,
            # then store current data
            if result.fun < res_mse:
                res_mse = result.fun
                param_fits = result.x

        model_str = model_name.split(':')[0].replace(" ", "-")
        model_fit_results.to_csv(outp_dir+'/model_fit_results/'+'sub-SCN'+subj_id+'_'+model_str+'_fit_results.csv', index=False)





