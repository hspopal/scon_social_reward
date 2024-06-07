#!/bin/bash

# Run fmriprep on local Mac

bids_dir=/Users/hpopal/Desktop/dscn_lab/projects/social_reward/bids

docker run -ti --rm \
    -v ${bids_dir}:/data:ro \
    -v ${bids_dir}/derivatives:/out \
    nipreps/fmriprep:20.2.6 \
    /data /out \
    participant --participant-label sub-SCN196 \
    --skull-strip-template MNI152NLin2009cAsym \
    --output-spaces MNIPediatricAsym:cohort-5:res-2 MNI152NLin6Asym:res-2 anat \
    --use-aroma \
    --nthreads 8 --n_cpus 6 --omp-nthreads 8 --mem-mb 24000 \
    --skip_bids_validation \
    --no-submm-recon \
    --fs-license-file /data/archive/license.txt

