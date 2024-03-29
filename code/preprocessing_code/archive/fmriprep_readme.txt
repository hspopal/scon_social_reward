There are 3 main scripts for the automatic fmriprep preprocessing pipeline (version: fmriprep-20.2.5). Here is how you run them. 
1. cd /data/neuron/SCN/preprocessing_code
This is where all scripts are stored, and the scripts you will be using are SCN_wrapper.sh, SCN_bsw2neu_data.sh, and SCN_resubmit_job.sh.

2. sh SCN_wrapper.sh (for automatic preprocessing)
It will check the existing files on neuron with those on MNC server and start downloading the new ones. If neuron is up to date, you will see a list of "SCN_xxx exist". 
If there is a new subject, the script will start downloading them and convert them into BIDS format before sending them to bswift. The whole process will take a few minutes before you see the final slurm message of "Submitted batch job xxxxxx."
Note, the raw dicom file can be found at /data/neuron/SCN/dicom
The nifti files organized in BIDS format can be found at /data/neuron/SCN/BIDS.

Alternatively, sh SCN_wrapper.sh 101 will restart the whole preprocesing process from the beginning. It happened a few times that MNC did not upload all files from the scanner to the server (mostly structural scans were missing, like only 20 slices out of 192 were uploaded to the server). If it happens, you will need to email wzhan@umd.edu and let him know and he will manually upload the file. The raw file on MNC server (fmri.umd.edu) can be found at 
/export/software/fmri/massstorage/Elizabeth Redcay/SCN Social Connection

3. If everything goes smoothly, after a day or two, you should get an email from slurm with the title 
SLURM Job_id=484960 Name=SCN143 Ended, Run time 1-04:24:56, COMPLETED, ExitCode 0
This means fmriprep is successfully completed and now you can transfer them back to neuron, for which you need to go back to
data/neuron/SCN/preprocessing_code folder and run
sh SCN_bsw2neu_data.sh 101
This will transfer the preprocessed data and corresponding log file back to neuron folder /data/neuron/SCN/fmriprep_out.

4. If anything unexpected happens, you can resubmit the fmriprep job on bswift using 
sh SCN_resubmit_job.sh 101 1: this removes all existing preprocessed files on bswift and restarts. Or, running 
sh submit_rebswift_job.sh 101: this will allow fmriprep to pick up from where it left off and reuse intermediate results (e.g., fmriprep fails due to memory or timing limit)
If fmriprep fails, your best chance to find out why would be checking the last few lines of the fmriprep log file of that subject located on bswift by 
cd /data/bswift-1/$USER/SCN/fmriprep/log
tail sub-SCN101.log -n 20
Note, the error message "slurmstepd: error: Exceeded step memory limit at some point." is normal. 

5. After everything is done, check off the Scan Tracker sheet of SCN fMRI Master Log to let Riley and whoever is responsible for QA know that the fmriprep preprocessing is completed for that subject. 
https://docs.google.com/spreadsheets/d/1-MOW372sO0g1y9cKl1_GkhMunp0lgdst11etN7qmZvU/edit#gid=843672936

For a new user who wants to run the wrapper scripts for the first time, make sure to set up the folder structure following /data/bswift-1/mkiely/SCN and they have freesurfer license on the root folder (/data/bswift-1/$USER/license.txt). 
