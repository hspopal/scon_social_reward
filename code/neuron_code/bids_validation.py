#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec  7 14:01:17 2024

@author: hpopal
"""


from os.path import join
from bids import BIDSLayout
from bids.tests import get_test_data_path
from bids import BIDSValidator
from bids.reports import BIDSReport

bids_dir = '/data/neuron/TRW/reprocessed/'


layout = BIDSLayout(bids_dir, ignore='./archive')


validator = BIDSValidator()

validator.is_bids(bids_dir)


# Initialize a report for the dataset
report = BIDSReport(layout)

# Method generate returns a Counter of unique descriptions across subjects
descriptions = report.generate()


