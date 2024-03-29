# -*- coding: utf-8 -*-
"""
Create a binarized brain mask from the fmriprep output

Author: Haroon Popal
"""

import os
import sys

from nilearn.image import binarize_img

import warnings
warnings.filterwarnings("ignore")


# Take script inputs
subj = 'sub-SCN'+str(sys.argv[1])

# For beta testings
#subj = 'sub-SCN101'

# Set BIDS project directory
bids_dir = '/data/neuron/SCN/SR/'
os.chdir(bids_dir)

# Set output directory
data_dir = bids_dir + 'derivatives/fmriprep/'+subj+'/anat/'


# Define fmriprep template space
template = 'MNIPediatricAsym_cohort-5_res-2'

# Find participant gm segmentation
subj_gm = data_dir+subj+'_space-'+template+'_label-GM_probseg.nii.gz'

# Binarize image
img = binarize_img(subj_gm, threshold=0.2)


# Save grey matter mask
img.to_filename(data_dir+subj+'_space-'+template+'_label-GM_probseg_bin.nii.gz')
