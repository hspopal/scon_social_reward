% Haroon Popal
% 02/19/2024
% MATLAB R2023a
%% Set-up
%{
Prior to running this script, run the "SUIT cerebellum toolbox" section of 
code in the analyses.sh script in code subdirectory. This bit of code will 
create T1s and suit directories in the appropriate places for the rest of 
this script.
%}

%% Add paths
addpath('/software/neuron/SPM/spm12')

spm;

%%
bids_dir = '/data/neuron/SCN/SR/';
data_dir = strcat(bids_dir,'derivatives/SR_univariate/');
%suit_dir = strcat(bids_dir, 'derivatives/suit/');



%% Set variables

subj_list = {'sub-SCN101', 'sub-SCN102', 'sub-SCN103', 'sub-SCN104', ...
            'sub-SCN105', 'sub-SCN106', 'sub-SCN107', 'sub-SCN108', ...
            'sub-SCN109', 'sub-SCN110'  'sub-SCN112', 'sub-SCN113', ...
            'sub-SCN117', 'sub-SCN118', 'sub-SCN119', 'sub-SCN120', ...
            'sub-SCN121', 'sub-SCN122', 'sub-SCN123', 'sub-SCN124', ...
            'sub-SCN125', 'sub-SCN126', 'sub-SCN127', 'sub-SCN128', ...
            'sub-SCN129', 'sub-SCN133', 'sub-SCN134', 'sub-SCN135', ...
            'sub-SCN138', 'sub-SCN141', 'sub-SCN142', 'sub-SCN143', ...
            'sub-SCN144', 'sub-SCN145', 'sub-SCN146', 'sub-SCN147', ...
            'sub-SCN151', 'sub-SCN152', 'sub-SCN154', 'sub-SCN155', ...
            'sub-SCN157', 'sub-SCN158', 'sub-SCN159', 'sub-SCN160', ...
            'sub-SCN164', 'sub-SCN165', 'sub-SCN168', 'sub-SCN169', ...
            'sub-SCN171', 'sub-SCN172', 'sub-SCN173', 'sub-SCN177', ...
            'sub-SCN181', 'sub-SCN182', 'sub-SCN183', 'sub-SCN184', ...
            'sub-SCN185', 'sub-SCN186', 'sub-SCN187', 'sub-SCN188', ...
            'sub-SCN189', 'sub-SCN190', 'sub-SCN194', 'sub-SCN195', ...
            'sub-SCN196', 'sub-SCN198', 'sub-SCN199', 'sub-SCN200', ...
            'sub-SCN201', 'sub-SCN204', 'sub-SCN205', 'sub-SCN206', ...
            'sub-SCN207', 'sub-SCN208', 'sub-SCN209', 'sub-SCN210', ...
            'sub-SCN215', 'sub-SCN216', 'sub-SCN218', 'sub-SCN219', ...
            'sub-SCN222', 'sub-SCN223', 'sub-SCN225', 'sub-SCN227', ...
            'sub-SCN234'};
%subj_list = char(subj_list);

tasks = {'SR'};


%% For loop
for i = 1:length(subj_list)
    subj = subj_list{i};
    % Isolate cerebellum and brainstem

    % Set paths and file prefix
    suit_dir = strcat(data_dir,subj,'/suit/');
    
    cd(suit_dir);

    subj_t1_prefix = strcat(subj,'_space-MNIPediatricAsym_cohort-5_res-2');


    % Isolate cerebellum and brainstem
    if isfile(strcat(suit_dir,'c_',subj_t1_prefix,'_desc-preproc_T1w_pcereb.nii'))    
        %print(strcat(subj, ' suit_isolate_seg already done'))
    else
        suit_isolate_seg({strcat(suit_dir,subj_t1_prefix,'_desc-preproc_T1w.nii')})
    end
        
    % Normalize to template
    job.subjND.gray={strcat(suit_dir,subj_t1_prefix,'_label-GM_probseg.nii')};
    job.subjND.white={strcat(suit_dir,subj_t1_prefix,'_label-WM_probseg.nii')};
    job.subjND.isolation={strcat(suit_dir,'c_',subj_t1_prefix,'_desc-preproc_T1w_pcereb.nii')};

    if isfile(strcat('Affine_', subj, '_run-1_space-MNI152NLin2009cAsym_label-GM_probseg.mat'))    
        %print(strcat(subj, ' suit_normalize_dartel already done'))   
    else
        suit_normalize_dartel(job)
    end
    

    % Find functional maps
    fileList = dir(strcat(data_dir,subj,'/','zmap*.nii'));

    
    % Map funcitonal data to new space
    for i_task = 1:length(tasks)
        task = tasks{i_task};
        
        for i_cond = 1:length(fileList)
            
            job.subj.affineTr = {strcat('Affine_', subj, ...
                '_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg.mat')};
            job.subj.flowfield = {strcat('u_a_', subj, ...
                '_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg.nii')};
            job.subj.resample = {strcat(suit_dir,'../',fileList(i_cond).name)};
            job.subj.mask = {strcat('c_', subj, ...
                '_space-MNIPediatricAsym_cohort-5_res-2_desc-preproc_T1w_pcereb.nii')};

            suit_reslice_dartel(job)

            % Put data from SUIT space to native space
            job.Affine = {strcat('Affine_', subj, ...
                '_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg.mat')};
            job.flowfield = {strcat('u_a_', subj, ...
                '_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg.nii')};
            job.resample = {strcat(suit_dir,fileList(i_cond).name)};
            job.resample = {strcat(suit_dir,'../wd',fileList(i_cond).name)};
            job.ref = {strcat(suit_dir,'../',fileList(i_cond).name)};
            %job.ref = {strcat(suit_dir,subj_t1_prefix,'_desc-preproc_T1w.nii')};

            suit_reslice_dartel_inv(job)
        end
    end
    
end

%% Convert cerebellum mask to MNI subject space

for i = 1:length(subj_list)
    subj = subj_list{i};
    % Isolate cerebellum and brainstem

    % Set paths and file prefix
    suit_dir = strcat(data_dir,subj,'/suit/');

    cd(suit_dir);

    job.Affine = {strcat('Affine_', subj, ...
                  '_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg.mat')};
    job.flowfield = {strcat('u_a_', subj, ...
                    '_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg.nii')};
    job.resample = {strcat('c_', subj, ...
                        '_space-MNIPediatricAsym_cohort-5_res-2_desc-preproc_T1w_pcereb.nii')};

    job.ref = {strcat(suit_dir,'../',fileList(1).name)};

    suit_reslice_dartel_inv(job)
end

%% Convert atlas to MNI subject space

subj = 'sub-010';

suit_dir = strcat(bids_dir, 'derivatives/social_doors/',subj,'/suit/');

cd(suit_dir);

job.Affine = {strcat('Affine_', subj, ...
              '_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg.mat')};
job.flowfield = {strcat('u_a_', subj, ...
                '_space-MNIPediatricAsym_cohort-5_res-2_label-GM_probseg.nii')};
job.resample = {'/usr/local/spm12/toolbox/suit/atlases/King_2019/atl-MDTB10_space-SUIT_dseg.nii '};

job.ref = {strcat(suit_dir,'../tmap_',task, ...
           '_',condition,'.nii')};

suit_reslice_dartel_inv(job)



