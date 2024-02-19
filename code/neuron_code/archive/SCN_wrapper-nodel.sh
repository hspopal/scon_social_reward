#!/bin/bash/
##########################################################################
#                       SCONN Preprocessing Script
#
# A wrapper file automatically download file from MNC server
# There are 2 ways of running it:
# 1. sh SCN_wrapper.sh 
# Automatically checking for new subjects on MNC and start nifti/BIDS conversion and fmriprep preprocessing.
# 2. sh SCN_wrapper.sh 101 
# Redownload a specific subject and restart nifti/BIDS conversion and fmriprep preprocessing (this is useful when there is a missing file on MNC's end, in which case you will need to email MNC to ask them to upload the file, after which you can restart downloading.
# Author: Oliver Xie 08/18/22

# Edits by Haroon Popal 09/24/23
# Each stage of this script will be broken down and checks will be made for each stage
# For example, if dicoms have been downloaded, but fmriprep output is not present,
# then just run fmriprep
#
##########################################################################

##########################################################################
# Help
Help()
{
    # Display help
    echo "SCONN Preprocessing Script"
    echo
    echo "Syntax: sh SCN_wrapper-nodel.sh [999 -a|r|h]"
    echo "options:"
    echo "-a    Rerun the entire pipeline for a particular participant, from downloading data from MNC to fmriprep"
    echo "-r    Rerun fmriprep for a particular participant"
    echo "-h    Print this help"
}
##########################################################################

# Set variables and directories
subID=$1
uname=$USER  # Record your directory ID/username
outdir=../dicom/  # Where dicom file goes on neuron
subID=$1
bids_neuron=../BIDS/sub-SCN${subID}
SCN_bswift=/data/bswift-1/"${uname}"/SCN/fmriprep  # fmriprep data should go to this folder on bswift


# Get optional inputs
rerun_fmriprep=false
rerun_all=false

while getopts "s:arh" opt; do
	case $opt in 
        s) # Provide subject ID
            subID=${OPTARG};;
        r) # Rerun just fmriprep
            rerun_fmriprep=true;;
        a) # Rerun entire pipeline, removing all data everywhere, and 
        # redownloading data from MNC
            rerun_all=true;;
        h) # Display Help
            Help
            exit;;
	esac
done



# aux functions do not edit
# Download data from fmri2 to neuron dicom folder
function download_data () 
{
sub=$1
echo Downloading $1
scp -r ${uname}@fmri2.umd.edu:"${SCN}"/${sub}/ $outdir
}

# Send BIDS data from neuron to bswift
function neuron2bswift () 
{
from_path=$1
to_path=$2
server_path=${uname}@login.bswift.umd.edu
#ssh ${server_path} "[ ! -d $to_path ] && mkdir $to_path && mkdir $to_path_BIDS"
scp -r "${from_path}" "${server_path}":"$to_path"/BIDS/
}


# If a specific subject ID is given then restart downloading raw data from MNC server
# this is useful when a subject's scan is missing or incomplete (e.g., T1 scan) on MNC server, but the scanner still has that data	
if [ ! -z "$subID" ] && [ $rerun_fmriprep == true ]
then
    echo Running fmriprep for SCN_${subID}
    echo "$SCN_bswift"
    echo "$uname"
    echo SCN"$subID"
    echo "$SCN_bswift"/log/sub-SCN"$subID".log
    echo "sbatch --export=indir="$SCN_bswift",uname="$uname",subID="$subID" --job-name=SCN"$subID" --mail-user="${uname}"@umd.edu --output="$SCN_bswift"/log/sub-SCN"$subID".log --error="$SCN_bswift"/log/sub-SCN"$subID".err /data/bswift-1/hpopal/SCN/code/fmriprep_SCN-hpopal.sh"
    ssh ${uname}@login.bswift.umd.edu "sbatch --export=indir="${SCN_bswift}"/fmriprep,uname="${uname}",subID="${subID}" --job-name=SCN"${subID}" --mail-user="${uname}"@umd.edu --output="${SCN_bswift}"/log/sub-SCN"${subID}".log --error="${SCN_bswift}"/log/sub-SCN"${subID}".err /data/bswift-1/hpopal/SCN/code/fmriprep_SCN-hpopal.sh"
else
    # Remove all of a particular subject's data and redownload along with new data
    if [ ! -z "$subID" ] && [ $rerun_all == true ]
    then
        # Remove old dicom file
        echo removing dicom files of SCN_${subID}
        rm -rf ../dicom/SCN_${subID}
        echo removing BIDS files of SCN_${subID}
        rm -rf ../BIDS/sub-SCN${subID}
        echo Removing fmriprep files of SCN_${subID} on bswift
        ssh ${uname}@login.bswift.umd.edu "rm -rf "$SCN_bswift"/out/fmriprep/sub-SCN"$subID"  "$SCN_bswift"/out/freesurfer/sub-SCN"$subID" "$SCN_bswift"/BIDS/sub-SCN"$subID" "$SCN_bswift"/log/sub-SCN"$subID".log"
    fi

    # Start comparing exisiting subjects on neuron with MNC server
    echo ------------------------
    echo checking MNC server for new data
    echo ------------------------
    # Set path for MNC servers
    SCN='/export/software/fmri/massstorage/Elizabeth\ Redcay/SCN\ Social\ Connection'  # where is raw data located on MNC server?
    
    # Set variables to capture subject data at various stages of preprocessing
    local_dicom=$(ls -d ${outdir}/SCN* | sed 's/[^0-9A-Z]*//g' | cut -c 4-)  # get subject index, sed command reduces to SCN###, cut command reduces to just ID# - MK
    local_bids=$(ls -d ../BIDS/sub-SCN* | sed 's/[^0-9A-Z]*//g' | cut -c 4-) 
    local_fmriprep=$(ls -d ../fmriprep_out/fmriprep/sub-SCN* | sed 's/[^0-9A-Z]*//g' | cut -c 4-) 

    # Get subject index from fmri2 to compare to previous line, select IDs for new download
    sub_idxs=$(ssh ${uname}@fmri2.umd.edu ls -l $SCN)
    cnt=0;
    
    for el in ${sub_idxs[@]}; do
        if [[ $el == "SCN_"* ]]
        then 
            subID=$(echo ${el:4})
            bids_neuron=../BIDS/sub-SCN${subID}
            # Check to see if dicoms exist on neuron
            if [[ ! $local_dicom == *${subID}* ]]
            then
                echo new data found SCN_$subID 
                download_data SCN_"${subID}"  # download data from fmri2 to neuron (dicom)
                chmod 777 -R ../dicom/SCN_${subID}
            fi
            
            # Check to see if BIDS converted NIFTIs exist on neuron
            if [[ ! $local_bids == *${subID}* ]]
            then
                echo SCN_${subID} starting BIDS conversion
                ./BidsConvert_SCN.sh BidsConvertParameters_SCN.sh SCN_"${subID}"  # BidsConvert_SCN.sh converts raw dicom file to nii and put it into BIDS format
            fi

            # Check to see if fmriprep data exists on neuron
            if [[ ! $local_fmriprep == *${subID}* ]]
            then
               # Copy over fmriprep data from bswift to neuron
                scp -r "${uname}@login.bswift.umd.edu":"$SCN_bswift"/out/fmriprep/sub-SCN${subID}* \
                    ../fmriprep_out/fmriprep/
                scp -r "${uname}@login.bswift.umd.edu":"$SCN_bswift"/out/freesurfer/sub-SCN${subID} \
                    ../fmriprep_out/freesurfer/

                # Check if fmriprep data still doesn't exist, then run
                if [[ ! $local_fmriprep == *${subID}* ]]
                then
                    # Transfering data to BSWIFT 
                    echo SCN_${subID} transferring data to neuron
                    neuron2bswift $bids_neuron $SCN_bswift  # transfer the data to BSWIFT
                    
                    # Submit fmriprep sbatch on bswift
                    ssh ${uname}@login.bswift.umd.edu "sbatch --export=indir="$SCN_bswift",uname="$uname",subID="$subID" --job-name=SCN"$subID" --mail-user="${uname}"@umd.edu --output="$SCN_bswift"/log/sub-SCN"$subID".log /data/bswift-1/hpopal/SCN/code/fmriprep_SCN-hpopal.sh"
                fi
            fi

        else
            ((++cnt))
        fi
    done
fi

