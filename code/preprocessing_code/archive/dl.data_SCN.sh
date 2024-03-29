#!/bin/bash/
# download folder from MNC 
# usage: sh dl.data_SCN.sh "SCN_998"
uname=$USER
MNC='/export/software/fmri/massstorage/Elizabeth\ Redcay/SCN\ Social\ Connection'
outdir=../dicom
function download_data () {
sub=$1
echo Start downloading $1, script running in background
scp -r ${uname}@fmri2.umd.edu:"${MNC}"/${sub}/ $outdir &
}
download_data $1
