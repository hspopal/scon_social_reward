# Social Connection - Social Reward
Contributors: Haroon Popal, Elizabeth Redcay, Victoria Alleluia Shenge


# Analyses

## Reinforcement Learning
### Behavioral Data Modeling
Run social_reward_modeling.ipynb

### Neuroimaging

1. Run prep_event_files-rl.py for each subject
    - Creates a design matrix with a reward prediction error regressor
2. Run rl_1st_level-indiv_runs.py for each subject
    - Runs the first level analysis, creating beta maps for reward prediction errors

