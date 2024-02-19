#!/bin/bash/
# a wrapper file automatically download file from MNC server
uname=$USER
SCN='/export/software/fmri/massstorage/Elizabeth\ Redcay/SCN\ Social\ Connection' # where is data located on MNC server?
outdir=../dicom/
function download_data () {
sub=$1
echo Downloading $1
scp -r ${uname}@fmri.umd.edu:"${SCN}"/${sub}/ $outdir
}
local_dicom=$(ls -d ${outdir}/SCN* | sed 's/[^0-9]*//g')
sub=$(ssh ${uname}@fmri.umd.edu ls -l $SCN) 
echo checking MNC server for new data
cnt=0;
for el in ${sub[@]}; do
	if [[ $el == "SCN_"* ]]
	then 
		idx=$(echo ${el:4})
		if [[ $local_dicom == *${idx}* ]]
		then
			echo SCN_$idx exist
		else
			echo new data found SCN_$idx
			download_data SCN_"${idx}"
			chmod 777 $outdir/SCN_"${idx}" -R
			echo SCN_${idx} download completes and start BIDS conversion
			./BidsConvert_SCN.sh BidsConvertParameters_SCN.sh SCN_"${idx}"
		fi
	else
		((++cnt))
	fi
done

