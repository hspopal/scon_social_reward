#!/bin/bash
#SBATCH --time=24:00:00
#SBATCH --nodes=1                    ### Number of Nodes
#SBATCH --ntasks=1                   ### Number of Tasks
#SBATCH --cpus-per-task=1            ### Number of Tasks per CPU
#SBATCH --mem=100000
#SBATCH --mail-type=ALL
#
#module ()
#{
#    eval `/usr/local/Modules/3.2.10/bin/modulecmd bash $*`
#}
Sub=sub-SCN${subID}
#
#module load python/3.8.10
#

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


j=0
(( z=j % 400 )) 
(( y=j % 20 ))
(( x=j/20 ))

(( alpha=x/20 ))
(( beta=y/20 ))
(( intercept=z/20 ))


python3 code/rl_modeling_fitting.py -p $subID -a $alpha -b $beta -i $intercept

