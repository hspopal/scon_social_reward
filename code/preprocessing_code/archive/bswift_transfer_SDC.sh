#!/bin/bash
uname=$USER
subID=sub-SCN$1
[ $uname == huaxie ] && indir='/data/bswift-1/oliver/SCN'
ssh ${uname}@login.bswift.umd.edu "sh /data/bswift-1/oliver/SCN/code/data_transfer_SDC.sh "$subID" "$indir"" 
