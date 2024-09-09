#!/bin/bash
#SBATCH --time=168:00:00
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --mem=24000
#SBATCH --mail-type=ALL
#
#module ()
#{
#    eval `/usr/local/Modules/3.2.10/bin/modulecmd bash $*`
#}
Sub=sub-SCN${subID}
#
module load freesurfer
#
echo "------------------------------------------------------------------"
echo "started freesurfer"
echo ${Sub}
date
echo "------------------------------------------------------------------"

#
indir=/data/software-research/${uname}/SCN/fmriprep
[ ! -d $indir ] && mkdir $indir
[ ! -d $indir/out ] && mkdir $indir/out
[ ! -d $indir/out/freesurfer ] && mkdir $indir/out/freesurfer
#[ ! $indir/BIDS/dataset_description.json ] && cp /data/bswift-1/oliver/SCN/fmriprep/BIDS/dataset_description.json $indir/BIDS/dataset_description.json
recon-all -i $indir/BIDS/${Sub}/anat/${Sub}_T1w.nii.gz -openmp 8 -s ${Sub} -sd $indir/out/freesurfer -all -parallel
#
#
echo "------------------------------------------------------------------"
echo "Ended freesurfer"
echo ${Sub}
date
echo "------------------------------------------------------------------"
#
#
#
# You can change the 4 lines below, I just like having it time stamp it
echo "------------------------------------------------------------------"
echo "Starting fMRIprep at:"
echo working on ${Sub}
date
echo "------------------------------------------------------------------"
#
# 
#
#export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow
#
/data/software-research/software/apptainer/bin/singularity run --cleanenv \
    -B /data/software-research/${uname}/SCN/fmriprep:/data \
    /data/software-research/hpopal/fmriprep-20.2.6.simg \
    /data/BIDS /data/out participant \
    --participant-label ${Sub} \
    -w /tmp/work_${uname}_${Sub}_1 \
    --skull-strip-template MNI152NLin2009cAsym \
    --output-spaces MNIPediatricAsym:cohort-5:res-2 MNI152NLin6Asym:res-2 anat \
    --use-aroma \
    --nthreads 8 --n_cpus 6 --omp-nthreads 6 \
    --mem-mb 24000 \
    --skip_bids_validation \
    --no-submm-recon \
    --fs-license-file /data/license.txt

rm -rf /tmp/work_${uname}_${Sub}_1


#
echo "------------------------------------------------------------------"
echo "Ended fMRIprep"
echo ${Sub}
date
echo "------------------------------------------------------------------"

# echo start transfering ${Sub} preprocessed data and log file to neuron
# sh /data/bswift-1/oliver/SCN/code/data_transfer.sh $Sub $indir
scp -r "${indir}"/out/fmriprep/"${Sub}" "${indir}"/out/fmriprep/"${Sub}".html "${uname}"@neuron.umd.edu:/data/neuron/SCN/fmriprep_out/fmriprep/
scp -r "${indir}"/out/freesurfer/"${Sub}" "${uname}"@neuron.umd.edu:/data/neuron/SCN/fmriprep_out/freesurfer/
scp -r "${indir}"/log/sub-SCN"$idx".log "${uname}"@neuron.umd.edu:/data/neuron/SCN/fmriprep_out/log/
