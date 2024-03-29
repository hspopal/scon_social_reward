#!/bin/bash
uname=$USER
subID=sub-SCN$1
if [ $uname == huaxie ]
then 
    indir=/data/bswift-1/oliver/SCN
else
    indir=/data/bswift-1/"${uname}"/SCN 
fi
ssh ${uname}@login.bswift.umd.edu "sh /data/bswift-1/oliver/SCN/code/data_transfer.sh "$subID" "$indir"" 
