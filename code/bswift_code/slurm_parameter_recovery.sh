#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --nodes=1                    ### Number of Nodes
#SBATCH --ntasks=1                   ### Number of Tasks
#SBATCH --cpus-per-task=1            ### Number of Tasks per CPU
#SBATCH --mem=1000
#SBATCH --mail-type=ALL
#SBATCH --array=0-441%80            ### Only run 80 processes at a time
#
#module ()
#{
#    eval `/usr/local/Modules/3.2.10/bin/modulecmd bash $*`
#}
Sub=sub-SCN${subID}

# Create virtual environment for python
python3 -m venv venv
source venv/bin/activate
pip3 install --upgrade pip
pip3 install numpy pandas scipy

source venv/bin/activate
echo "------------------------------------------------------------------"
echo "Starting model fitting for "
echo ${Sub}
date
echo "------------------------------------------------------------------"


j=${SLURM_ARRAY_TASK_ID}
(( alpha=j/21 % 21))
(( beta=j % 21 ))
intercept=${i}


python code/rl_parameter_recovery.py -p $subID -a $(bc <<< 'scale=2; '$alpha'/20') -b $(bc <<< 'scale=2; '$beta'/20') -i $(bc <<< 'scale=2; '$intercept'/20')

