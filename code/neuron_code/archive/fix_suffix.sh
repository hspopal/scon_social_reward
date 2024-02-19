#!/bin/bash
# change all fmaps json intended for line 
injson=$(ls /data/neuron/SCN/BIDS/sub-SCN1*/fmap/*.json)
for json in ${injson[@]}; do
echo $json
subID=$(echo $json | grep -o -P '(?<=BIDS/).*(?=/fmap)')
echo $subID
sed -i 's/task-SCN/task-SR/g' "$json"
done
