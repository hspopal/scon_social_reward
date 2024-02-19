#!/bin/bash
#SubList="SCN126"
#SubList="SCN108 SCN118 SCN122 SCN123 SCN126 SCN127 SCN128 SCN134 SCN119 SCN120 SCN121 SCN125 SCN105 SCN112 SCN124 SCN110 SCN129"
#currentdir=${pwd}
SubList=`cat ndar_subj.txt`
outdir=/data/neuron/SCN/SCN_anonymized
cp facemask_mni.nii.gz $outdir
cp MNI152_T1_1mm_brain.nii.gz $outdir

# strctural scans
echo ------------structural runs begin-----------------
for sub in $SubList; do
indata=/data/neuron/SCN/BIDS/sub-${sub}/anat/sub-${sub}_T1w.nii.gz
echo Anonymizing $sub T1 immage
mkdir $outdir/sub-${sub}
outdata=$outdir/sub-${sub}_T1w.nii.gz
cp $indata $outdata
NiftiAnonymizer.sh $outdata yes
mv $outdir/sub-${sub}_T1w_new_defaced.nii.gz $outdir/sub-${sub}/sub-${sub}_T1w.nii.gz
echo Finished anonymizing $sub T1 image 
done

echo ------------functional runs begin-----------------
for sub in $SubList; do
indata=$(ls /data/neuron/SCN/BIDS/sub-${sub}/func/sub-*.nii.gz)
	for in_run in ${indata[@]}; do
	tmp=$(basename "$in_run")
	run_ID=${tmp%.nii.gz}
	echo Anonymizing $run_ID BOLD image
	out_run=$outdir/$tmp
	cp $in_run $out_run
	NiftiAnonymizer.sh $out_run no
	mv $outdir/${run_ID}_new.nii.gz $outdir/sub-${sub}/$tmp
	echo Finished anonymizing $run_ID BOLD image
	done 
done


