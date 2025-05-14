#!/bin/bash

# This script sets up some general things like files and directories, and
# includes code to run various analyses


export BIDS_DIR="/data/neuron/SCN/SR"
cd ${BIDS_DIR}

subj_list=(  101 102 103 104 105 106 107 108 109 110 
             112 117 118 119 120 121 122 123 124 125 
             126 127 128 129 133 134 135 141 142 143 
             144 145 147 149 151 152 154 155 157 158 
             159 160 164 165 168 169 171 172 173 177 
             181 182 183 184 185 186 187 189 190 195 
             196 197 198 199 200 201 204 207 208 210 
             214 215 216 217 220 221 222 223 224 225 
             226 227 228 231 232 233 234 235 236 237 
             238 239 241 242 244 246 249 250 251 252 
             253 256 261 263 264 267 268 272 275 277 
             278 283 287)

subj_list = ( 101 102 103 104 105 106 107 108 110 112 
              117 118 119 120 121 122 123 124 125 126 
              127 128 129 133 134 135 141 142 143 144 
              145 147 151 152 154 155 157 158 159 160 
              164 165 168 169 171 172 173 177 181 182 
              183 184 185 186 187 189 190 195 196 197 
              198 199 200 204 207 208 210 214 215 216 
              217 220 221 222 223 224 225 226 227 228 
              231 232 233 234 235 236 238 239 241 242 
              244 246 249 250 251 252 253 256 261 263 
              264 266 267 268 271 272 275 277 278 283 
              287 285 289 286 265 295 300 301 307 309 
              315 306 305 310 323 316 109 149 201 237 )

#subj_list=$(tail -n +2 participants.tsv | awk '{print $1}')




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



##########################################################################
# Reinforcement Learning
##########################################################################

# Model fitting
subj_list=( 101 102 103 104 105 106 107 108 109 110 )
subj_list=( 112 117 118 119 120 121 122 123 124 125 )
subj_list=( 126 127 128 129 133 134 135 141 142 143 )
subj_list=( 144 145 147 149 151 152 154 155 157 158 )
subj_list=( 159 160 164 165 168 169 171 172 173 177 )
subj_list=( 181 182 183 184 185 186 187 189 190 195 )
subj_list=( 196 197 198 199 200 201 204 207 208 210 )
subj_list=( 214 215 216 217 220 221 222 223 224 225 )
subj_list=( 226 227 228 231 232 233 234 235 236 237 ) 
subj_list=( 238 239 241 242 244 246 249 250 251 252 )
subj_list=( 253 256 261 263 264 267 268 272 275 277 278 283 287)

for subj in "${subj_list[@]}"; do 
    python code/hpopal/rl_modeling_fitting.py $subj
done

for inter in $(seq 0 20); do
    sbatch --export=subID=101,i=${inter} \
           --job-name=fit-"$subID" \
           --output=derivatives/logs/model_fit_sub-SCN"$subID".log \
           code/slurm_model_fit.sh 
done

JOBID=""
for inter in $(seq 0 20); do
    subID=102
    if [ -z "$JOBID" ]; then
        JOBID=$(sbatch --export=subID="$subID",i=${inter} \
           --job-name=fit-"$subID" \
           --output=derivatives/logs/model_fit_sub-SCN"$subID"_inter-"$inter".log \
           code/slurm_model_fit.sh | awk '{print $4}')
           sleep 10s
    else
        JOBID=$(sbatch --dependency=afterok:$JOBID \
           --export=subID="$subID",i=${inter} \
           --job-name=fit-"$subID" \
           --output=derivatives/logs/model_fit_sub-SCN"$subID"_inter-"$inter".log \
           code/slurm_model_fit.sh | awk '{print $4}')
    fi
    echo "Submitted "$subID" with intercept $inter as job $JOBID"
done

sbatch --export=subID=102,i=0 \
           --job-name=rcv-101 \
           --output=derivatives/logs/parameter_recovery_sub-SCN101.log \
           code/slurm_model_fit.sh 


JOBID=""
for inter in $(seq 0 20); do
    subID=101
    if [ -z "$JOBID" ]; then
        JOBID=$(sbatch --export=subID="$subID",i=${inter} \
           --job-name=fit-"$subID"-"$inter" \
           --output=derivatives/logs/model_fit_sub-SCN"$subID"_inter-"$inter".log \
           code/slurm_model_fit.sh | awk '{print $4}')
    else
        JOBID=$(sbatch --dependency=afterok:$JOBID \
           --export=subID="$subID",i=${inter} \
           --job-name=rcv-"$subID"-"$inter" \
           --output=derivatives/logs/parameter_recovery_sub-SCN"$subID"_inter-"$inter".log \
           code/slurm_parameter_recovery.sh | awk '{print $4}')
    fi
    echo "Submitted "$subID" with intercept $inter as job $JOBID"
done

sbatch --export=subID=102,i=0 \
           --job-name=rcv-101 \
           --output=derivatives/logs/parameter_recovery_sub-SCN101.log \
           code/slurm_parameter_recovery.sh 




for subj in "${subj_list[@]}"; do 
    sbatch --export=subID=101,i=1 \
    --output=derivatives/logs/model_fit_sub-SCN"$subID".log \
    code/slurm_model_fit.sh 
done

for subj in "${subj_list[@]}"; do 
    #mkdir derivatives/fmriprep/sub-SCN${subj}
    mkdir derivatives/fmriprep/sub-SCN${subj}
done



