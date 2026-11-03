#!/bin/bash

# This is the bash parameters file to be used in conjunction with BidsConvert.sh
# Modify everything in quotes for each element (1-7) below for your study.

# 1) Subjects
# Define the subject IDs for the data you want to convert. These IDs should
# match the IDs of the dicom folders. You can include numerous subjects or just
# one. It is OK if the subject IDs have dashs, underscores, or special
# characters because the BidsConvert script will remove them from the name.
# export SubID=("NET_902" "JAM_021" "JAM_023" "JAM_024" "JAM_026" "JAM_027" "JAM_029")

# 2) Dicom Directory
# Define the super directory where all the dicom folders reside.
export DcmDir="/data/neuron/SCN/dicom"

# 3) BIDS Study Directory
# Define the super directory where you want your BIDS organized data to reside.
export OutDir="/data/neuron/SCN/BIDS"

# 4) Path To dcm2niix
# Define path to the dcm2niix script. If dcm2niix is added to the bash/tcsh
# path/environment, you can simply use:
# Vert="dcm2niix"
export Vert="/data/neuron/SCN/preprocessing_code/dcm2niix"

# 5) Functional Scans
# Define the names of the functional dicom folders to convert. 
export FuncDcms=("SR1" "SR2" "SR3" "SR4" "NS1" "NS2" "NS3" "HBN1" "HBN2")
# Using the same order as above, define what you want them to be named
# REMEBER: Bids format does not like dashs, underscores, or any special
# characters for the name of the functional files. I incorporated this because
# the functional dicom folder names were not very descriptive.
export FuncName=("SR_run-01" "SR_run-02" "SR_run-03" "SR_run-04" "NS_run-01" "NS_run-02" "NS_run-03" "HBN_run-01" "HBN_run-02")

# 6) Structural Scans
# Define the names of the structural dicom folders to convert.
# Right now, this set up only allows for T1/MPRAGE structurals.
export StrctDcms=("t1_mpr")

# 7) Fieldmap Scans
# Define the names of the fieldmap dicom folders to convert.
# Right now, this only allows for opposite phase encoding direction fmaps.
export FmapDcms=("AP" "PA")


