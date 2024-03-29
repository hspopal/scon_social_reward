#!/bin/bash/
# a wrapper file automatically download file from MNC server
uname=$USER
SCN='/export/software/fmri/massstorage/Elizabeth\ Redcay/SCN\ Social\ Connection' # where is raw data located on MNC server?
outdir=../dicom/ # where dicom file goes on neuron 
# grab data from MNC
function download_data () {
sub=$1
echo Downloading $1
scp -r ${uname}@fmri.umd.edu:"${SCN}"/${sub}/ $outdir
}
# send BIDS data from neuron to bswift  
function neuron2bswift () {
from_path=$1
to_path=$2
server_path=${uname}@login.bswift.umd.edu
ssh ${server_path} "[ ! -d $to_path ] && mkdir $to_path && mkdir $to_path_BIDS"
scp -r "${from_path}" "${server_path}":"$to_path"/BIDS/
}
local_dicom=$(ls -d ${outdir}/SCN* | sed 's/[^0-9]*//g') # get subject index
sub=$(ssh ${uname}@fmri.umd.edu ls -l $SCN) 
echo checking MNC server for new data
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
			download_data SCN_"${idx}"
			echo SCN_${idx} download completes and start BIDS conversion
			./BidsConvert_SCN.sh BidsConvertParameters_SCN.sh SCN_"${idx}" # BidsConvert_SCN.sh converts raw dicom file to nii and put it into BIDS format
			bids_neuron=../BIDS/sub-SCN${idx}
			chmod 777 -R ../dicom/SCN_${idx}
			if [ uname == huaxie ] 
			then
			    SCN_bswift='/data/bswift-1/oliver/SCN/fmriprep' # fmriprep data should go to this folder on bswift
			else
			    SCN_bswift=/data/bswift-1/"${uname}"/SCN/fmriprep # needs to be tested
			fi
			neuron2bswift $bids_neuron $SCN_bswift # transfer the data to BSWIFT
			if [ uname == huaxie ] 
			# submit jobs on bswift
                        then
				ssh ${uname}@login.bswift.umd.edu "sbatch --export=indir="$SCN_bswift",uname=oliver,subID="$idx" --job-name=SCN"$idx" --mail-user=huaxie@umd.edu --output=/data/bswift-1/oliver/SCN/log/sub-SCN"$idx".log /data/bswift-1/oliver/SCN/code/fmriprep_SCN.sh"
			else
				ssh ${uname}@login.bswift.umd.edu "sbatch --export=indir="$SCN_bswift",uname="$uname",subID="$idx" --job-name=SCN"$idx" --mail-user="${uname}"@umd.edu --output=/data/bswift-1/"$uname"/SCN/log/sub-SCN"$idx".log /data/bswift-1/oliver/SCN/code/fmriprep_SCN.sh"
			fi
		fi
	else
		((++cnt))
	fi
done

