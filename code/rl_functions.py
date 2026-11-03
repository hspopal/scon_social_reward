try:
    import os
    import pandas as pd
    import numpy as np

except ImportError:
    pass




# Define model run function
def run_rl_model(model, alphas, beta, intercept, neg_reward, sim_data, sim=True):
    # Create empty dataframe to store data
    model_data = pd.DataFrame()

    if 'Run' in sim_data.columns:
        n_sims = sim_data['Run'].max()
        iter_colname = 'Run'
        iter_names = sim_data['Run'].unique()

        for alpha in alphas:
            # Filter for one simulation's data
            #sim_data = simulate_data(n_trials)
            #sim_data_temp = sim_data[sim_data[iter_colname] == i_iter].copy()
            #sim_data_temp = sim_data_temp.reset_index(drop=True)
            
            # Run models
            model_data_temp = model(sim_data, alpha, beta, intercept, neg_reward=neg_reward)
            model_data_temp[iter_colname] = sim_data['Run'].copy()
            model_data_temp['RT_actual'] = sim_data['First_RT'].copy()
            model_data_temp['alpha'] = alpha
            model_data_temp['beta'] = beta
            model_data_temp['intercept'] = intercept
        
            model_data = pd.concat([model_data, model_data_temp])
        
    else:
        n_sims = sim_data['n_sim'].max() + 1
        iter_colname = 'n_sim'
        iter_names = sim_data['n_sim'].unique()

        for i_iter in iter_names:
            for alpha in alphas:
                # Filter for one simulation's data
                #sim_data = simulate_data(n_trials)
                sim_data_temp = sim_data[sim_data[iter_colname] == i_iter].copy()
                sim_data_temp = sim_data_temp.reset_index(drop=True)
                
                # Run models
                model_data_temp = model(sim_data_temp, alpha, beta, intercept, neg_reward=neg_reward)
                model_data_temp[iter_colname] = i_iter
                model_data_temp['alpha'] = alpha
                model_data_temp['beta'] = beta
                model_data_temp['intercept'] = intercept
            
                model_data = pd.concat([model_data, model_data_temp])

    # Turn index into time point
    model_data['trial'] = model_data.index
    model_data_long = pd.melt(model_data, id_vars=[iter_colname,'Peer','RPE','RT','alpha','trial','Interest'], 
                              var_name='Condition',
                              value_vars=['SimPeer','DisPeer','Computer'], value_name='Value')

    return(model_data, model_data_long)





# Define models

## Basic generative model
def rw_model(trial_list, alpha, beta, intercept, neg_reward=False):
    
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


## Modeling with reaction time being random

def rw_randrt_model(trial_list, alpha, beta, intercept, neg_reward=False):
    
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


## RT is dependent on the difference between condition values

def rw_rtvaldiff_model(trial_list, alpha, beta, intercept, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))
    
    for t in range(len(trial_list)):
        # Capture the trial info
        cond_t = trial_list.loc[t, 'Peer']

        # Create a RT based on the value of each condition
        cond_diff = np.abs(V.loc[t, 'SimPeer'] - V.loc[t, 'DisPeer'] - V.loc[t, 'Computer'])
        sigma = np.std(V['SimPeer'] - V['DisPeer'] - V['Computer'])
        RT[t] = beta * np.abs(np.abs(cond_diff) + intercept)

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


## RT is calculated by value

def rw_rt_model(trial_list, alpha, beta, intercept, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))
    
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


## RT is biased for peer conditions

def rw_rtsocial_model(trial_list, alpha, beta, intercept, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))
    
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


## RT is dependent on condition value and the item value

def rw_item_model(trial_list, alpha, beta, intercept, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))
    
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


## Computer feedback is limited, and peer feedback is increased or negative reward

def rw_rt_modreward_model(trial_list, alpha, beta, intercept, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))

    
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


## Computer feedback is limited, and peer feedback is increased or negative reward

def rw_rt_modreward2_model(trial_list, alpha, beta, intercept, neg_reward=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))

    
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

## Surprise model: Surprise modulates RT
def rw_spr_model(trial_list, alpha, beta, intercept, neg_reward=False, sim=False):
    
    # Define an empty dataframe for the value of each condition at each trial 
    V = pd.DataFrame(columns=['SimPeer', 'DisPeer', 'Computer'], 
                     index=range(len(trial_list)))
    
    # Create initial variables
    # Define intitional condition values for similar, dissimilar, and computer
    V.loc[0, ['SimPeer', 'DisPeer', 'Computer']] = 0.5
    RPE = np.empty(len(trial_list))
    RT = np.empty(len(trial_list))
    
    for t in range(len(trial_list)):
        # Capture the trial info
        cond_t = trial_list.loc[t, 'Peer']
        value_t = V.loc[t, cond_t]

        # Create a RT based on the value of each condition
        RT[t] = beta * value_t + intercept

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
        V.loc[t+1, cond_t] = V.loc[t, cond_t] + alpha * np.abs(RPE[t])
        
        # Copy over value of all other conditions
        V.loc[t+1, V.columns != cond_t] = V.loc[t, V.columns != cond_t]
    
    RL_output = V.iloc[:-1].copy()
    RL_output['Peer'] = trial_list['Peer']
    RL_output['Interest'] = trial_list['Interest']
    RL_output['RPE'] = RPE
    RL_output['RT'] = RT
    
    return RL_output







