#!/bin/bash

# This script sets up some general things like files and directories, and
# includes code to run various analyses


export BIDS_DIR="/data/neuron/SCN/SR"
cd ${BIDS_DIR}

subj_list=( 101 102 103 104 105 106 107 108 109 110 
            112 117 118 119 120 121 123 124 125 128 
            129 133 134 135 141 143 145 147 149 158 
            165 169 172 177 185 186 187 196 197 201 
            208 216 217 220 221 223 224 225 226 227 
            228 231 232 233 234 236 237 238 239 241 
            242 244 246 249 250 253 )





# Create event files for first level design matrices
for subj in "${subj_list[@]}"; do 
    python code/hpopal/prep_event_files.py $subj
done

for subj in "${subj_list[@]}"; do 
    python code/hpopal/prep_event_files-rl.py $subj
done

# Create grey matter masks for each subject
for subj in "${subj_list[@]}"; do 
    python code/hpopal/create_gm_brain_mask.py $subj
done


# Run first level analysis
for subj in "${subj_list[@]}"; do 
    python code/hpopal/social_reward_1st_level-nilearn-indiv_runs.py $subj
done

for subj in "${subj_list[@]}"; do 
    python code/hpopal/rl_1st_level-indiv_runs.py $subj
done


##########################################################################
# SUIT cerebellum toolbox
##########################################################################

## Create suit directory in subj folders and copy relevant files
for subj in "${subj_list[@]}"; do 
    mkdir derivatives/SR_first_level/sub-SCN${subj}/suit
    cp derivatives/fmriprep/sub-SCN${subj}/anat/sub-SCN${subj}*preproc_T1w.nii.gz derivatives/SR_first_level/sub-SCN${subj}/suit/
    cp derivatives/fmriprep/sub-SCN${subj}/anat/sub-SCN${subj}*GM_probseg.nii.gz derivatives/SR_first_level/sub-SCN${subj}/suit/
    cp derivatives/fmriprep/sub-SCN${subj}/anat/sub-SCN${subj}*WM_probseg.nii.gz derivatives/SR_first_level/sub-SCN${subj}/suit/
    gzip -df derivatives/SR_first_level/sub-SCN${subj}/suit/*.nii.gz
    gzip -df derivatives/SR_first_level/sub-SCN${subj}/zmap_*.nii.gz
done

# Move files around for better organization
for subj in "${subj_list[@]}"; do 
    mv derivatives/SR_first_level/sub-SCN${subj}/wdzmap_* derivatives/SR_first_level/sub-SCN${subj}/suit/
done

# Copy over some files for the individual run data
for subj in "${subj_list[@]}"; do 
    gzip -d derivatives/SR_first_level-indiv_runs/sub-SCN${subj}/zmap_*.nii.gz
    cp -r derivatives/SR_first_level/sub-SCN${subj}/suit derivatives/SR_first_level-indiv_runs/sub-SCN${subj}/
    rm derivatives/SR_first_level-indiv_runs/sub-SCN${subj}/suit/wdzmap_*
done

# Recombine new cerebellum SUIT data with original first level maps
# Dont actually run

# Resample to original functional space
flirt -in derivatives/social_doors/sub-SCN010/suit/c_sub-SCN010_run-1_space-MNI152NLin2009cAsym_desc-preproc_T1w_pcereb.nii \
      -ref derivatives/social_doors/sub-SCN010/tmap_social_facesVoutcm.nii \
      -out derivatives/social_doors/sub-SCN010/suit/c_sub-SCN010_run-1_space-MNI152NLin2009cAsym_desc-preproc_T1w_pcereb_2mm.nii -applyxfm

flirt -in derivatives/social_doors/sub-SCN010/suit/iw_wdtmap_social_facesVoutcm_u_a_sub-SCN010_run-1_space-MNI152NLin2009cAsym_label-GM_probseg.nii \
      -ref derivatives/social_doors/sub-SCN010/tmap_social_facesVoutcm.nii \
      -out derivatives/social_doors/sub-SCN010/suit/iw_wdtmap_social_facesVoutcm_u_a_sub-SCN010_run-1_space-MNI152NLin2009cAsym.nii -applyxfm

fslmaths derivatives/social_doors/sub-SCN010/suit/iw_wdtmap_social_facesVoutcm_u_a_sub-SCN010_run-1_space-MNI152NLin2009cAsym.nii -bin derivatives/social_doors/sub-SCN010/suit/iw_wdtmap_social_facesVoutcm_u_a_sub-SCN010_run-1_space-MNI152NLin2009cAsym.nii

# Subtract old data
fslmaths derivatives/social_doors/sub-SCN010/tmap_social_facesVoutcm.nii \
         -sub derivatives/social_doors/sub-SCN010/suit/c_sub-SCN010_run-1_space-MNI152NLin2009cAsym_desc-preproc_T1w_pcereb_2mm.nii \
         derivatives/social_doors/sub-SCN010/suit/tmap_social_facesVoutcm_suit.nii.gz

# Add cerebellum SUIT data to original functional data
fslmaths derivatives/social_doors/sub-SCN010/suit/tmap_social_facesVoutcm_suit.nii.gz \
         -add derivatives/social_doors/sub-SCN010/suit/iw_wdtmap_social_facesVoutcm_u_a_sub-SCN010_run-1_space-MNI152NLin2009cAsym.nii \
         derivatives/social_doors/sub-SCN010/suit/tmap_social_facesVoutcm_suit.nii.gz






