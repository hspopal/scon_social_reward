#!/bin/bash
Sub=$1
indir=$2
uname=$USER
scp -r "${indir}"/fmriprep/out/fmriprep/"${Sub}" "${indir}"/fmriprep/out/fmriprep/"${Sub}".html "${uname}"@neuron.umd.edu:/data/neuron/SCN/fmriprep_out/fmriprep
scp -r "${indir}"/fmriprep/out/freesurfer/"${Sub}" "${uname}"@neuron.umd.edu:/data/neuron/SCN/fmriprep_out/freesurfer
scp -r "${indir}"/fmriprep/log/"$Sub".log "${uname}"@neuron.umd.edu:/data/neuron/SCN/fmriprep_out/log
