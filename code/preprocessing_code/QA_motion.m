% extract the mean FD and pct good data and output to QA.csv
% print out bad runs with meanFD > 0.5mm or frames with FD greater 1mm > 20%.  
clear
indir = '/data/neuron/SCN/fmriprep_out/fmriprep';
task = {'SR','NS','HBN'};
ii =  1;
for task_id = 1 : length(task)
    intsv = dir(fullfile(indir,['sub*/func/*_task-' task{task_id} '*_desc-confounds_timeseries.tsv']));
    for i = 1 : length(intsv)
        indata = intsv(i).name;
        tmp = findstr(indata,'run-');
        task_name{ii} = task{task_id};
        run_ID{ii} = indata(tmp+4);
        tmp = findstr(indata,'_task');
        subIDX{ii} = indata(1:tmp-1);
        tbl = tsvread(fullfile(intsv(i).folder,intsv(i).name));
        FD = tbl.framewise_displacement;
        mean_FD(ii) = nanmean(FD);
        censor_1 = FD < 1;
        pct_1_censor(ii) = mean(censor_1);
        ii = ii + 1;
 	display(['Extracting dataset ' num2str(i) ' of task ' task{task_id}])    
    end
end
QA = table(subIDX(:),run_ID(:),task_name(:),mean_FD(:),pct_1_censor(:),'VariableNames',{'subIDX','run_ID','task','mean_FD','pct_less_than_1mm'});
idx = find(mean_FD>0.5 | pct_1_censor<0.8);
display('----------------- Bad runs ---------------')
for i = 1 : length(idx)
    fprintf('%s, %s-run%s is bad \n', subIDX{idx(i)},task_name{idx(i)},run_ID{idx(i)})
end
writetable(QA,'../QA.csv', "WriteVariableNames",1)
% fileattrib('../QA.csv','+w','a')
