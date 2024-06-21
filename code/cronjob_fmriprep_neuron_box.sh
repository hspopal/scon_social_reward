#!/bin/bash

# Copy over fmriprep html files
rsync -a "neuron.umd.edu:/data/neuron/SCN/fmriprep_out/fmriprep/sub-SCN*.html" ./

# For all participants with fmriprep output, copy over the figure directory
for file in *.html; do   
    dir_name="${file//.html}"
    if [ ! -e $dir_name ]; then
        mkdir "${dir_name// (hpopal@umd.edu)}"
        rsync -a "neuron.umd.edu:/data/neuron/SCN/fmriprep_out/fmriprep/${dir_name}/figures" "${dir_name}/"
    fi
done


