CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

CMA.Core.ajax = {
    urls: {}
};

CMA.Core.ajax.urls.loadUrls = function() {
    CMA.Core.root_url = "/celerymanagementapp/";
    CMA.Core.get_tasks_url = CMA.Core.root_url + "task/all/list/";
    CMA.Core.get_workers_url = CMA.Core.root_url + "worker/all/list/";
    CMA.Core.tasks_per_worker_url = CMA.Core.root_url + "task/all/dispatched/byworker/count/";
    CMA.Core.task_url = CMA.Core.root_url + "view/dispatched_tasks/";
    CMA.Core.pending_tasks_url = CMA.Core.root_url + "task/all/dispatched/pending/count/";
    CMA.Core.worker_processes_url = CMA.Core.root_url + "worker/all/subprocess/count/";
    CMA.Core.shutdown_worker_url = CMA.Core.root_url + "worker/<placeHolder>/shutdown/";
    CMA.Core.query_dispatched_tasks_url = CMA.Core.root_url + "xy_query/dispatched_tasks/";
    CMA.Core.task_url = "/celerymanagementapp/view/task/";
    CMA.Core.worker_url = "/celerymanagementapp/view/task/";
    CMA.Core.create_out_of_band_worker_url = CMA.Core.root_url + "outofbandworker/";
    CMA.Core.create_provider_url = CMA.Core.root_url + "provider/";
}

CMA.Core.ajax.urls.loadTestUrls = function(){
    CMA.Core.root_url = "/celerymanagementapp/site_media/test_data/";
    CMA.Core.post_root_url = "/celerymanagementapp/test/post/";
    CMA.Core.get_tasks_url = CMA.Core.root_url + "tasks.json";
    CMA.Core.get_workers_url = CMA.Core.root_url + "workers.json";
    CMA.Core.tasks_per_worker_url = CMA.Core.root_url + "tasks_per_worker.json";
    CMA.Core.pending_tasks_url = CMA.Core.root_url + "tasks_pending.json";
    CMA.Core.worker_processes_url = CMA.Core.root_url + "worker_processes.json";
    CMA.Core.shutdown_worker_url = CMA.Core.post_root_url + "worker/<placeHolder>/shutdown/";
    CMA.Core.query_dispatched_tasks_url = CMA.Core.post_root_url + "xy_query/dispatched_tasks/";
    CMA.Core.task_url = "/celerymanagementapp/test/view/task/";
    CMA.Core.worker_url = "/celerymanagementapp/test/view/worker/";
    CMA.Core.chart_data_url = CMA.Core.root_url + "chart/enumerate-1.json";
    CMA.Core.create_out_of_band_worker_url = CMA.Core.post_root_url + "outofbandworker/";
    CMA.Core.create_provider_url = CMA.Core.post_root_url + "provider/";
}

CMA.Core.getTasks = function(callbackFunction){
    $.getJSON(CMA.Core.get_tasks_url, callbackFunction);
}

CMA.Core.getWorkers = function(callbackFunction){
    $.getJSON(CMA.Core.get_workers_url, callbackFunction);
}

CMA.Core.getTasksPerWorker = function(callbackFunction){
    $.getJSON(CMA.Core.tasks_per_worker_url, callbackFunction);
}

CMA.Core.getPendingTasks = function(callbackFunction){
    $.getJSON(CMA.Core.pending_tasks_url, callbackFunction);
}

CMA.Core.getWorkerProcesses = function(callbackFunction){
    $.getJSON(CMA.Core.worker_processes_url, callbackFunction);
}

CMA.Core.postShutdownWorker = function(workerName, callbackFunction){
    $.post(CMA.Core.shutdown_worker_url.replace("<placeHolder>", workerName), callbackFunction);
}

CMA.Core.getDispatchedTasksData = function(query, callbackFunction) {
    $.post(CMA.Core.query_dispatched_tasks_url, query, callbackFunction);
}

CMA.Core.postCreateOutOfBandWorkerNode = function(callbackFunction){
    $.post(CMA.Core.create_out_of_band_worker_url, $('#blankOutOfBandForm').serialize(), callbackFunction);
}

CMA.Core.postCreateProvider = function(callbackFunction){
    $.post(CMA.Core.create_provider_url, $('#blankProviderForm').serialize(), callbackFunction);
}
