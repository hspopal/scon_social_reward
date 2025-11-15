# Social Connection Social Reward

Contributors: Haroon Popal, Elizabeth Redcay, Victoria Alleluia Shenge


# Set Up
- [`task_audit.ipynb`](https://github.com/hspopal/scon_social_reward/blob/main/code/task_audit.ipynb)
  - The social reward fMRI task had a bug which changed trials from some participants, in which their interest was shown as a disinterest or vice-versa
  - This results in a lot of participants being presented "wrong answers" and some participants getting a lot of wrong answers
  - This notebook examines each participants data, and produces:
    - A spreadsheet for the number of errors for each participant - `answer_errors_sum.csv`
    - A duplicate of the task output files, for each participant, for each run, with a column indicating whether the trial was "wrong" or not (this can be used as a regressor in the first level fMRI analysis)
- [`MRI-QC_summary.ipynb`](https://github.com/hspopal/scon_social_reward/blob/main/code/MRI-QC_summary.ipynb)
  - Combines participant metadata from various sources (e.g. MRI QC, demographics) and outputs a series of TSV or CSVs which can be used as participant lists
  - This allows you to know which participants to use in analyses, and how that list was created, in a transparent manner
  - Output:
    - `participants.tsv`
      - "Tab-seperated values" format (it's like a CSV, except it uses tabs as delimintators) list of all participants which have a completed an MRI session (even with only a portion of the session completed)
    - `participants-qc.csv`
      - A list of subject IDs and runs that are "good" based on the lab's MRI QC protocol
    - `participants-qc-min_task_errors.csv`
      - Same as above except, participants are only included if they had 5 or less task errors
    - `participants-qc-no_task_errors.csv`
      - Same as above except, participants are only included if they had no task errors


# Analyses

## General
[`setup_analyses.sh`](https://github.com/hspopal/scon_social_reward/blob/main/code/setup_analyses.sh) contains helpful code to get things generally set up in the terminal, such as a subjects list to run for loops, and code to run the individual analysis scripts.


## Univariate Analyses
- [`prep_event_files.py`](https://github.com/hspopal/scon_social_reward/blob/main/code/neuron_code/prep_event_files.py)
    - Prep event files from the psychopy task output to be in the correct format for nilearn
- [`create_gm_brain_mask.py`](https://github.com/hspopal/scon_social_reward/blob/main/code/neuron_code/create_gm_brain_mask.py)
    - Uses the fmriprep output to create a grey matter mask for each participant
- [`social_reward_1st_level-nilearn-indiv_runs.py`](https://github.com/hspopal/scon_social_reward/blob/main/code/neuron_code/social_reward_1st_level-nilearn-indiv_runs.py)
    - Run the first level analysis for each participant, for the social reward task
    - First level here refers to creating whole-brain beta maps for each participant
    - This script creates beta maps for each condition, for each run, and averaged together (each condition for each participant)


## Behavioral Analyses
- [pre_post_task.Rmd](https://hspopal.github.io/scon_social_reward/code/pre_post_task.html)
  - Analyze the pre and post social reward task survey
- [`rt_modeling.ipynb`](https://github.com/hspopal/scon_social_reward/blob/main/code/rt_modeling.ipynb)
  - Reaction time analyses for each run and between groups


## Reinforcement Learning
### Behavioral Data Modeling
- [`social_reward_modeling.ipynb`](https://github.com/hspopal/scon_social_reward/blob/main/code/social_reward_modeling.ipynb)
  - Walkthrough of the social RL models and modeling steps
  - Does not actually produce the modeling results, but shows visualizations of the model hypotheses and the modeling steps
- [`rl_modeling_results.ipynb`](https://github.com/hspopal/scon_social_reward/blob/main/code/rl_modeling_results.ipynb)
  - Combines model fit and parameter recovery results for each participant
- [`model_simulations.ipynb`](https://github.com/hspopal/scon_social_reward/blob/main/code/model_simulations.ipynb)
  - Gives descriptions of the different model hypotheses and visualizations of their hypothesized performances

