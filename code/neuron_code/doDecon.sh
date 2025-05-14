#!/bin/tcsh
# For the fMRIPrep tutorial, copy and paste this into the "func" directory of ${subj} in the "derivatives/fmriprep" folder
# and type: "tcsh doDecon.sh ${subj}"

#if ( $#argv > 0 ); then
#    subj = $argv[1]
#else
#    subj = s01
#fi

subj=sub-SCN101

3dDeconvolve -input sub-SCN101_task-SR_run-*_space-MNIPediatricAsym_cohort-5_res-2_desc-preproc_bold.nii.gz \
    -mask sub-SCN101_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg_bin.nii.gz \
    -polort 2 \
    -num_stimts 19 \
    -stim_times 1 stimuli/ButtonPress.1D 'BLOCK(1,1)' \
    -stim_label 1 ButtonPress \
    -stim_times 2 stimuli/HighReward_Computer-fb.1D 'BLOCK(2,1)' \
    -stim_label 2 HighReward_Computer-fb \
    -stim_times 3 stimuli/HighReward_DisPeer-fb.1D 'BLOCK(2,1)' \
    -stim_label 3 HighReward_DisPeer-fb \
    -stim_times 4 stimuli/HighReward_SimPeer-fb.1D 'BLOCK(2,1)' \
    -stim_label 4 HighReward_SimPeer-fb \
    -stim_times 5 stimuli/LowReward_Computer-fb.1D 'BLOCK(2,1)' \
    -stim_label 5 LowReward_Computer-fb \
    -stim_times 6 stimuli/LowReward_DisPeer-fb.1D 'BLOCK(2,1)' \
    -stim_label 6 LowReward_DisPeer-fb \
    -stim_times 7 stimuli/LowReward_SimPeer-fb.1D 'BLOCK(2,1)' \
    -stim_label 7 LowReward_SimPeer-fb \
    -stim_file 8 trans_x_run1.txt'[0]' -stim_base 8 -stim_label 8 trans_x_01 \
    -stim_file 9 trans_y_run1.txt'[0]' -stim_base 9 -stim_label 9 trans_y_01 \
    -stim_file 10 trans_z_run1.txt'[0]' -stim_base 10 -stim_label 10 trans_z_01 \
    -stim_file 11 rot_x_run1.txt'[0]' -stim_base 11 -stim_label 11 rot_x_01 \
    -stim_file 12 rot_y_run1.txt'[0]' -stim_base 12 -stim_label 12 rot_y_01 \
    -stim_file 13 rot_z_run1.txt'[0]' -stim_base 13 -stim_label 13 rot_z_01 \
    -stim_file 14 trans_x_run2.txt'[0]' -stim_base 14 -stim_label 14 trans_x_02 \
    -stim_file 15 trans_y_run2.txt'[0]' -stim_base 15 -stim_label 15 trans_y_02 \
    -stim_file 16 trans_z_run2.txt'[0]' -stim_base 16 -stim_label 16 trans_z_02 \
    -stim_file 17 rot_x_run2.txt'[0]' -stim_base 17 -stim_label 17 rot_x_02 \
    -stim_file 18 rot_y_run2.txt'[0]' -stim_base 18 -stim_label 18 rot_y_02 \
    -stim_file 19 rot_z_run2.txt'[0]' -stim_base 19 -stim_label 19 rot_z_02 \
    -jobs 8 \
    -fout -tout -x1D X.xmat.1D -xjpeg X.jpg \
    -x1D_uncensored X.nocensor.xmat.1D \
    -fitts fitts.${subj} \
    -errts errts.${subj} \
    -bucket stats.${subj}