#!/bin/bash
##########################################################################
#                       SCONN Preprocessing Script
#
# Preprocessing script for the SCONN project which downloads dicoms from
# the MNC servers, converts them to niftis in BIDS format, and runs
# preprocessing via fmriprep on the bswift HPC.

# Each stage of this script can be run independently. See the help 
# function for details on running this script. This script should be 
# placed in the "preprocessing_code" directory on Neuron. It relies on 
# certain helper scripts developed by Oliver Xie and Junaid Merchant.
# 
# Prerequisite scripts:
# 1. BidsConvert_SCN.sh - should be in the preprocessing_code directory
# 2. BidsConvertParameters_SCN.sh - same as above
# 3. fmriprep_SCN.sh - should be in YOUR "code" directory on bswift
# (e.g. /data/bswift-1/hpopal/SCN/code/fmriprep_SCN.sh)
#
##########################################################################

##########################################################################
# Help
Help()
{
    # Display help
    echo "SCONN Preprocessing Script"
    echo
    echo "Syntax: sh SCN_preprocesssing.sh -s [999 -d|n|f|r|a|h]"
    echo "options:"
    echo "-d    Only download dicoms from MNC servers"
    echo "-n    Only convert dicoms to Niftis"
    echo "-f    Run fmriprep preprocessing"
    echo "-r    Rerun fmriprep for a particular participant"
    echo "-a    Rerun the entire pipeline for a particular participant, from downloading data from MNC to fmriprep"
    echo "-t    Transfer fmriprep, freesurfer, and log data from bswift to neuron"
    echo "-h    Print this help"
}
##########################################################################

# Get optional inputs
dicom_download=false
convert_niftis=false
run_fmriprep=false
rerun_fmriprep=false
transfer_bswift2neuron=false

while getopts "s:dnfrath" opt; do
	case $opt in 
        s) # Provide subject ID
            subID=${OPTARG};;
        d) # Download dicoms
            dicom_download=true;;
        n) # Convert dicoms to niftis
            convert_niftis=true;;
        f) # Rerun just fmriprep
            run_fmriprep=true;;
        r) # Rerun just fmriprep
            run_fmriprep=true;
            rerun_fmriprep=true;;
        a) # Rerun entire pipeline, removing all data everywhere, and 
           # redownloading data from MNC
            dicom_download=true;
            convert_niftis=true;
            rerun_fmriprep=true;;
        t) # Transfer data from bswift to neuron
            transfer_bswift2neuron=true;;
        h) # Display Help
            Help
            exit;;
	esac
done

# Set variables and directories
uname=$USER  # Record your directory ID/username
proj_dir=/data/neuron/SCN
dicom_dir="$proj_dir"/dicom/  # Where dicom file goes on neuron
nifti_dir=${proj_dir}/BIDS/sub-SCN${subID}
SCN_bswift=/data/software-research/"${uname}"/SCN/fmriprep/  # fmriprep data should go to this folder on bswift

# Navigate to the project directory
cd $proj_dir
echo $subID

##########################################################################
# Define Functions
##########################################################################
# Download data from fmri2 to neuron dicom folder
function download_data () 
{
sub=$1
echo Downloading $1

# Path for project data on MNC servers
scp -r ${uname}@fmri2.umd.edu:"${SCN}"/${sub}/ $dicom_dir
}

# Send BIDS data from neuron to bswift
function neuron2bswift () 
{
from_path=$1
to_path=$2
server_path=${uname}@bswift2-login.umd.edu
#ssh ${server_path} "[ ! -d $to_path ] && mkdir $to_path && mkdir $to_path_BIDS"
scp -r "${from_path}" "${server_path}":"$to_path"BIDS/
}



##########################################################################
# Start Pipeline
##########################################################################

# Set variables to capture subject data at various stages of preprocessing
local_dicom=$(ls -d ${dicom_dir}/SCN* | sed 's/[^0-9A-Z]*//g' | cut -c 4-)  # get subject index, sed command reduces to SCN###, cut command reduces to just ID# - MK
local_bids=$(ls -d "$proj_dir"/BIDS/sub-SCN* | sed 's/[^0-9A-Z]*//g' | cut -c 4-) 
local_fmriprep=$(ls -d "$proj_dir"/fmriprep_out/fmriprep/sub-SCN* | sed 's/[^0-9A-Z]*//g' | cut -c 4-) 



# Download dicoms

if $dicom_download
then
    echo ------------------------
    echo checking MNC server for data for ${subID}
    echo ------------------------

    # Set path for MNC servers
    SCN='/export/software/fmri/massstorage/Elizabeth\ Redcay/SCN\ Social\ Connection'  # where is raw data located on MNC server?

    # Check to see if dicoms exist on neuron
    if [[ ! $local_dicom == *${subID}* ]]
    then
        echo new data found SCN_$subID 
        download_data SCN_"${subID}"  # download data from fmri2 to neuron (dicom)
        chmod 777 -R "$proj_dir"/dicom/SCN_${subID}
    else
        echo "Dicoms already exist"
    fi
fi



# Convert dicoms to niftis

cd ${proj_dir}/preprocessing_code

if $convert_niftis
then
    echo ------------------------
    echo converting dicoms to niftis for ${subID}
    echo ------------------------

    # Check to see if BIDS converted NIFTIs exist on neuron
    if [[ ! $local_bids == *${subID}* ]]
    then
        echo SCN_${subID} starting BIDS conversion
        # Convert raw dicom file to nii and put it into BIDS format
        "$proj_dir"/preprocessing_code/BidsConvert_SCN.sh BidsConvertParameters_SCN.sh SCN_"${subID}" 
    else
        echo "Niftis already exist"
    fi
fi


# Preprocessing

cd ${proj_dir}

if $run_fmriprep
then
    # Check to see if fmriprep data exists on neuron
    if [[ ! $local_fmriprep == *${subID}* ]]
    then
        # Transfering data to BSWIFT 
        echo SCN_${subID} transferring data to neuron
        neuron2bswift $nifti_dir $SCN_bswift  # transfer the data to BSWIFT
            
        echo ------------------------
        echo running fmriprep for ${subID}
        echo ------------------------

        # Submit fmriprep sbatch on bswift
        ssh ${uname}@bswift2-login.umd.edu "sbatch --export=indir="$SCN_bswift",uname="$uname",subID="$subID" --job-name=SCN"$subID" --mail-user="${uname}"@umd.edu --output="$SCN_bswift"/log/sub-SCN"$subID".log /data/software-research/hpopal/SCN/code/fmriprep_SCN-bswift2.sh"


    elif $rerun_fmriprep
    then
        # Transfering data to BSWIFT 
        echo SCN_${subID} transferring data to neuron
        neuron2bswift $nifti_dir $SCN_bswift  # transfer the data to BSWIFT

        echo ------------------------
        echo rerunning fmriprep for ${subID}
        echo ------------------------

        # Submit fmriprep sbatch on bswift
        ssh ${uname}@bswift2-login.umd.edu "sbatch --export=indir="$SCN_bswift",uname="$uname",subID="$subID" --job-name=SCN"$subID" --mail-user="${uname}"@umd.edu --output="$SCN_bswift"/log/sub-SCN"$subID".log /data/software-research/hpopal/SCN/code/fmriprep_SCN-bswift2.sh"
    
    else
        echo ------------------------
        echo fmriprep data for ${subID} already exists. If you want to rerun, run script with "-r" flag
        echo ------------------------
    fi
fi



# Transfer data from bswift to neuron
cd ${proj_dir}

if $transfer_bswift2neuron
then
    BID_ID=sub-SCN$subID
    indir=/data/software-research/"${uname}"/SCN 

    ssh ${uname}@bswift2-login.umd.edu "sh /data/software-research/hpopal/SCN/code/data_transfer.sh "$BID_ID" "$indir"" 

    # Change permissions to fmriprep files so everyone can edit
    chgrp -R psyc-dscn-data ${proj_dir}/fmriprep_out/fmriprep/$BID_ID
    chmod -R 775 ${proj_dir}/fmriprep_out/fmriprep/$BID_ID
fi

