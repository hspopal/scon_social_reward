#!/bin/bash
#SBATCH --time=72:00:00
#SBATCH --nodes=1                    ### Number of Nodes
#SBATCH --ntasks=1                   ### Number of Tasks
#SBATCH --cpus-per-task=1            ### Number of Tasks per CPU
#SBATCH --mem=16000
#SBATCH --mail-type=ALL
#
#module ()
#{
#    eval `/usr/local/Modules/3.2.10/bin/modulecmd bash $*`
#}
Sub=sub-SCN${subID}

module use /data/software-research/software/modulefiles/linux-rhel8-x86_64/Core

# Create virtual environment for python
#python3.11 -m venv venv
#source venv/bin/activate
#pip3 install --upgrade pip
#pip3 install numpy pandas scipy

source venv/bin/activate
echo "------------------------------------------------------------------"
echo "Starting model fit result aggregation... "
echo ${Sub}
date
echo "------------------------------------------------------------------"


python code/rl_modeling_fit-aggregate.py 
