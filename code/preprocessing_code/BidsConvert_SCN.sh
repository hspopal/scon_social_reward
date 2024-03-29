#!/bin/bash
#SBATCH --time=144:00:00
#SBATCH --cores=4
#SBATCH --mem=24000

############################################################################
# Convert functional MRI data to BIDS folder
# Takes as input: SubjectID, name of functional file, output/BIDS folder path,
# & Dicom/Input directory.
# -junaid.salim.merchant 2018.07.30
# update: change the behavior when having multiple dicom files with the same task name, now choosing the one that is most recently modified. Oliver Xie 06/08/22 
############################################################################
#
############################################
# Qsub options.  Change only the -o option #
############################################
# Use current working directory
#$ -cwd
# Combine job and error logs
#$ -j y
# Name of job/error log
#$ -N BidsConvertFunc
# Directory where job/error logs are written. !CHANGE THIS!
#$ -o ~/Desktop
# Use bash
#$ -S /bin/bash
#$ -V
#
if [ $# -ne 2 ]; then
	echo "This is script is to convert functional, structural, & fieldmap MRI data into
 BIDS format."
	echo ""
	echo "Takes parameters file as input, which defines the subject IDs, paths, and fil
es to covert."
	echo ""
	echo "USAGE: ./BidsConvert.sh BidsConvertParameters_SCN.sh <SubID>"
	exit;
fi
#
#
source $1
#
SubID=$2
#
if [ ! -d BIDS_log ]; then
   mkdir BIDS_log
fi
# Loop through all the subjects and convert
for s in ${SubID[@]}; do
	#
	echo "Working on $s:"
	# Take in the subject ID from first input, but remove any dashes or special characters
	subid=${s//[-._]/}
	#
	# Assign output subject directory, and make dir if there isn't one.
	outdir=${OutDir}/sub-${subid}
	if [ ! -d $outdir ]; then
		mkdir $outdir
	fi
	#
	#
	#### START WORKING ON FUNCTIONALS ############################################
	# Assign output func directory, and make dir if there isn't one.
	if [ ! -d $outdir/func ]; then
		mkdir $outdir/func
	fi
	#
	# First, get a count for all the functional folders that need Converting
	Count=$(seq 0 $((${#FuncDcms[@]}-1)))
	#
	# Then use this count to loop through the functional files
	for c in ${Count[@]}; do
		funcD=${FuncDcms[$c]}
		funcN=${FuncName[$c]}
		echo "-- $funcN"
		#
		# Get input directory by searching the subject dicom folder for the
		# current functional.
		# CHANGED THIS PART FOR CAT 
		indir=$(find $DcmDir/$s -type d -name *$funcD)
		#
		# Check to see if there was only one directory of that name. If there
		# are multiple folders, select the last one and send message.
		# Note that if a functional is suppposed to have more than one run, make
		# sure to indicate that in the parameters file.
		if [ $(find $DcmDir/$s -type d -name *$funcD | wc -l) -gt 1 ]; then
			echo "Attention: there is more than one directory for $funcD , please check!"
			echo "Using the last file based on modification tome for now..."
			indir=$(ls -dt $DcmDir/$s/*/*$funcD | tail -1)
		fi
		#
		# Now you can convert that functional, and label it with the appropriate
		# label in the FuncName list:
		$Vert -o $outdir/func/ -f sub-${subid}_task-${FuncName[$c]}_bold -b y -ba y -z y $indir >> ./BIDS_log/log_${s}.txt
		#
		# End functional loop.
	done
	#
	#### START WORKING ON STRUCTURALS ############################################
	# Assign output anat directory, and make dir if there isn't one.
  echo "-- anat/T1w"
  if [ ! -d $outdir/anat ]; then
		mkdir $outdir/anat
	fi
	#
	# Get input directory by searching the subject dicom folder for the
	# structural. It's currently set up only for one structural.
	indir=$(find $DcmDir/$s -type d -name *$StrctDcms*)
	#
	# Check to see if there was only one directory of that name. If there
	# are multiple folders, select the last one and send message.
	if [ $(find $DcmDir/$s -type d -name *$StrctDcms* | wc -l) -gt 1 ]; then
		echo "Attention: there is more than one directory for $StrctDcms , please check!"
		echo "Using the last file based on modification tome for now..."
		indir=$(ls -dt $DcmDir/$s/*/*$StrctDcms* | tail -1)
	fi
	#
	# Convert MPRAGE and label with '_T1w' as per BIDS specification.
	$Vert -o $outdir/anat/ -f sub-${subid}_T1w -b y -ba y -z y $indir >> ./BIDS_log/log_${s}.txt
	#
	#
	#### START WORKING ON FIELD MAPS #############################################
	# Assign output anat directory, and make dir if there isn't one.
	if [ ! -d $outdir/fmap ]; then
		mkdir $outdir/fmap
	fi
	#
	for f in ${FmapDcms[@]}; do
		# Lower case the AP/PA for labeling the output as per the BIDS specification.
		Cur=$(echo $f | tr '[:upper:]' '[:lower:]')
    	echo "-- fmap/${Cur}"
		#
		# Get input directory by searching the subject dicom folder for fmap.
		indir=$(find ${DcmDir}/${s} -type d -name *_${f}_*)
		echo $indir
		#
		# Check to see if there was only one directory. If there are multiple
		# folders, select the last one and send message.
		if [ $(find ${DcmDir}/${s} -type d -name *_${f}_* | wc -l) -gt 1 ]; then
			echo "Attention: there is more than one directory for $f , please check!"
			echo "Using the last directory for now..."
			indir=$(find $DcmDir/$s -type d -name '*$f*' | xargs ls | tail -1)
		fi
		#
		# Convert MPRAGE and label with '_T1w' as per BIDS specification.
		$Vert -o $outdir/fmap/ -f sub-${subid}_dir-${Cur}_epi -b y -ba y -z y $indir >> ./BIDS_log/log_${s}.txt
    	#### ADDED IN FROM SHAWN TO INCORPORATE FMAPS #######
    	#sed -e '/"InstitutionalDepartmentName": "Department",/a\	"IntendedFor": ["func/sub-'${subid}'_task-SR_run-01_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-02_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-03_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-04_bold.nii.gz", "func/sub-'${subid}'_task-NS_run-01_bold.nii.gz", "func/sub-'${subid}'_task-NS_run-02_bold.nii.gz","func/sub-'${subid}'_task-NS_run-03_bold.nii.gz","func/sub-'${subid}'_task-HBN_run-01_bold.nii.gz","func/sub-'${subid}'_task-HBN_run-02_bold.nii.gz"],' ${outdir}/fmap/sub-${subid}_dir-${Cur}_epi.json > ${outdir}/fmap/sub-${subid}_dir-${Cur}_epi.json.tmp  
    	sed -e '/"ConversionSoftware": "dcm2niix",/a\	"IntendedFor": ["func/sub-'${subid}'_task-SR_run-01_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-02_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-03_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-04_bold.nii.gz", "func/sub-'${subid}'_task-NS_run-01_bold.nii.gz", "func/sub-'${subid}'_task-NS_run-02_bold.nii.gz","func/sub-'${subid}'_task-NS_run-03_bold.nii.gz","func/sub-'${subid}'_task-HBN_run-01_bold.nii.gz","func/sub-'${subid}'_task-HBN_run-02_bold.nii.gz"],' ${outdir}/fmap/sub-${subid}_dir-${Cur}_epi.json > ${outdir}/fmap/sub-${subid}_dir-${Cur}_epi.json.tmp  
    	#textin='"IntendedFor": ["func/sub-'${subid}'_task-SR_run-01_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-02_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-03_bold.nii.gz", "func/sub-'${subid}'_task-SR_run-04_bold.nii.gz", "func/sub-'${subid}'_task-NS_run-01_bold.nii.gz", "func/sub-'${subid}'_task-NS_run-02_bold.nii.gz","func/sub-'${subid}'_task-NS_run-03_bold.nii.gz","func/sub-'${subid}'_task-HBN_run-01_bold.nii.gz","func/sub-'${subid}'_task-HBN_run-02_bold.nii.gz"],'
	#json=${outdir}/fmap/sub-${subid}_dir-${Cur}_epi.json.tmp
	#lineout=$(cat $json | wc -l)
	#sed -i "${lineout}i $textin " $json
	rm -f ${outdir}/fmap/sub-${subid}_dir-${Cur}_epi.json 
    	cp ${outdir}/fmap/sub-${subid}_dir-${Cur}_epi.json.tmp ${outdir}/fmap/sub-${subid}_dir-${Cur}_epi.json
		#
		rm -f ${outdir}/fmap/*tmp
		#
	done
	#
	#
	# end subject loop
done

chmod -R 777 ${outdir}
