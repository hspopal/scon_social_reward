#!/bin/bash
module load matlab
cd /data/neuron/SCN/preprocessing_code
matlab -nodisplay -nosplash -nodesktop -r "run('QA_motion.m');exit;" | tail -n +11
