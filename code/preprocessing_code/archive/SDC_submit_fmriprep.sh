#!/bin/bash/
# if fMRIprep failed, use this script to resubmit the job
# sh submit_bswift_job.sh 101 0
idx=$1
uname=$USER
bids_neuron=../BIDS/sub-SCN${idx}
[ uname==huaxie ] && SCN_bswift='/data/bswift-1/oliver/SCN/fmriprep' # fmriprep data should go to this folder on bswift?
function neuron2bswift () {
from_path=$1
to_path=$2
server_path=${uname}@login.bswift.umd.edu
ssh ${server_path} "[ ! -d $to_path ] && mkdir $to_path && mkdir $to_path_BIDS"
scp -r "${from_path}" "${server_path}":"$to_path"/BIDS/
}
transfer=$2
[ -n "${transfer}" ] && neuron2bswift $bids_neuron $SCN_bswift # if transfer flag is not null, transfering data to bswift 
# remove existing output file rerun completely
# ssh ${uname}@login.bswift.umd.edu "rm -rf "$SCN_bswift"/out/fmriprep/sub-SCN"$idx"  "$SCN_bswift"/out/freesurfer/sub-SCN"$idx" /data/bswift-1/oliver/SCN/log/sub-SCN"$idx".log"
ssh ${uname}@login.bswift.umd.edu "sbatch --export=indir="$SCN_bswift",uname=oliver,subID="$idx" --job-name=SCN"$idx" --mail-user="${uname}"@umd.edu --output=/data/bswift-1/oliver/SCN/log/sub-SCN"$idx".log /data/bswift-1/oliver/SCN/code/fmriprep_SCN_SDC.sh"
