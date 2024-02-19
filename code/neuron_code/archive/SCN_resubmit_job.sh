#!/bin/bash/
# if fMRIprep failed, use this script to resubmit the job
# Ex1: if you wnat to completely reun subject SCN-101 
# sh SCN_resubmit_job.sh 101 1
# this will remove all the exisiting fmriprep files on bswift 
# Ex2: if you want to pick up from where fmriprep left off and reuse intermediate results (e.g., your fmriprep failed due to memory or timing limit) 
# sh SCN_resubmit_job.sh 101 
idx=$1
uname=$USER
bids_neuron=../BIDS/sub-SCN${idx}
if [ $uname == huaxie ] 
then
    SCN_bswift=/data/bswift-1/oliver/SCN/fmriprep # where fmriprep data is stored on bswift, I need to do this because my directory ID is not my home directory name on bswift  
else
    SCN_bswift=/data/bswift-1/${uname}/SCN/fmriprep 
fi
rerun=$2
if [ ! -z "$rerun" ]
then 
# Optional: remove existing output file rerun completely
ssh ${uname}@login.bswift.umd.edu "rm -rf "$SCN_bswift"/out/fmriprep/sub-SCN"$idx"  "$SCN_bswift"/out/freesurfer/sub-SCN"$idx" "$SCN_bswift"/log/sub-SCN"$idx".log"
fi
# submit fmriprep sbatch on bswift
ssh ${uname}@login.bswift.umd.edu "sbatch --export=indir="$SCN_bswift",uname="$uname",subID="$idx" --job-name=SCN"$idx" --mail-user="${uname}"@umd.edu --output="$SCN_bswift"/log/sub-SCN"$idx".log /data/bswift-1/"${uname}"/SCN/code/fmriprep_SCN.sh"
