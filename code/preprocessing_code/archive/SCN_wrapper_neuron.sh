#!/bin/bash/
# A wrapper file automatically download file from MNC server
# There are 2 ways of running it:
# 1. sh SCN_wrapper.sh 
# Automatically checking for new subjects on MNC and start nifti/BIDS conversion and fmriprep preprocessing.
# 2. sh SCN_wrapper.sh 101 
# Redownload a specific subject and restart nifti/BIDS conversion and fmriprep preprocessing (this is useful when there is a missing file on MNC's end, in which case you will need to email MNC to ask them to upload the file, after which you can restart downloading.
# Author: Oliver Xie 08/18/22

# Edited by Haroon Popal 09/21/23
# This wrapper runs fmriprep locally on neuron

subID=$1
uname=$USER #record your directory ID/username
outdir=../dicom/ # where dicom file goes on neuron 
# aux functions do not edit
#download data from fmri2 to neuron dicom folder
function download_data () {
sub=$1
echo Downloading $1
scp -r ${uname}@fmri2.umd.edu:"${SCN}"/${sub}/ $outdir
}

# aux ends
SCN_bswift=/data/neuron/SCN/fmriprep_out 

if [ ! -z "$subID" ]
then
   # if a specific subject ID is given then restart downloading raw data from MNC server
   # this is useful when a subject's scan is missing or incomplete (e.g., T1 scan) on MNC server, but the scanner still has that data
	idx=$subID
	# remove old dicom file
	echo removing dicom files of SCN_${idx}
	rm -rf ../dicom/SCN_${idx}
	echo removing BIDS files of SCN_${idx}
	rm -rf ../BIDS/sub-SCN${idx}

fi
	# if no sub ID is provided then start comparing exisiting subjects on neuron with MNC server
	echo ------------------------
	echo checking MNC server for new data
	echo ------------------------
	SCN='/export/software/fmri/massstorage/Elizabeth\ Redcay/SCN\ Social\ Connection' # where is raw data located on MNC server?
	local_dicom=$(ls -d ${outdir}/SCN* | sed 's/[^0-9A-Z]*//g' | cut -c 4-) # get subject index, sed command reduces to SCN###, cut command reduces to just ID# - MK
	sub=$(ssh ${uname}@fmri2.umd.edu ls -l $SCN) #get subject index from fmri2 to compare to previous line, select IDs for new download
	cnt=0;
	for el in ${sub[@]}; do
		if [[ $el == "SCN_"* ]]
		then 
			idx=$(echo ${el:4})
			if [[ $local_dicom == *${idx}* ]]
			then
				echo SCN_$idx exist # skip downloading if the file has already been downloaded
			else
				echo new data found SCN_$idx 
				download_data SCN_"${idx}" #download data from fmri2 to neuron (dicom)
				chmod 777 -R ../dicom/SCN_${idx}
				echo SCN_${idx} download completes and start BIDS conversion
				./BidsConvert_SCN.sh BidsConvertParameters_SCN.sh SCN_"${idx}" # BidsConvert_SCN.sh converts raw dicom file to nii and put it into BIDS format
				bids_neuron=../BIDS/sub-SCN${idx}
				# Begin preprocessing on neuron
				ssh ${uname}@login.bswift.umd.edu "sbatch --export=indir="$SCN_bswift"/fmriprep,uname="$uname",subID="$idx" --job-name=SCN"$idx" --mail-user="${uname}"@umd.edu --output="$SCN_bswift"/log/sub-SCN"$idx".log /data/bswift-1/mkiely/SCN/code/fmriprep_SCN.sh"
			    
                /usr/local/miniconda/bin/fmriprep \
                /home/vallelui/SCN/fmriprep/BIDS \
                /home/vallelui/SCN/fmriprep/out \
                participant --participant-label sub-SCN209 \
                -w /home/vallelui/SCN/fmriprep/working \
                --skull-strip-template MNI152NLin2009cAsym \
                --output-spaces MNIPediatricAsym:cohort-5:res-2 MNI152NLin6Asym:res-2 anat \
                --use-aroma \
                --nthreads 8 --n_cpus 6 --omp-nthreads 6 --mem-mb 24000 \
                --skip_bids_validation \
                --no-submm-recon \
                --fs-license-file /home/vallelui/license.txt
            
            fi
		else
			((++cnt))
		fi
	done
