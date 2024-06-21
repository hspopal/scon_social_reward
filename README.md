# Social Connection - Social Reward
Contributors: Haroon Popal, Elizabeth Redcay, Victoria Alleluia Shenge


# Set Up
- `task_audit.ipynb`
  - The social reward fMRI task had a bug which changed trials from some participants, in which their interest was shown as a disinterest or vice-versa
  - This results in a lot of participants being presented "wrong answers" and some participants getting a lot of wrong answers
  - This notebook examines each participants data, and produces:
    - A spreadsheet for the number of errors for each participant
    - A duplicate of the task output files, for each participant, for each run, with a column indicating whether the trial was "wrong" or not (this can be used as a regressor in the first level fMRI analysis)
- `prep_participants_lists.ipynb`
  - For each subject, list the runs that have passed experimentor quality control
  - Output:
    - `participants_good.csv`
      - A list of subject IDs and runs that are "good" based on fMRI QC
    - `participants_good-min_task_errors.csv`
      - Same as above except, participants are only included if they had 5 or less task errors
    - `participants_good-no_task_errors.csv`
      - Same as above except, participants are only included if they had no task errors


# Analyses

## Reinforcement Learning
### Behavioral Data Modeling
Run `social_reward_modeling.ipynb`

### Neuroimaging

1. Run `prep_event_files-rl.py` for each subject
    - Creates a design matrix with a reward prediction error regressor
2. Run `rl_1st_level-indiv_runs.py` for each subject
    - Runs the first level analysis, creating beta maps for reward prediction errors

