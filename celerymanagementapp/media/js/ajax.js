CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

CMA.Core.ajax = {
    urls: {}
};

CMA.Core.ajax.urls.loadUrls = function() {
    CMA.Core.ajax.urls.root_url = "/celerymanagementapp/";
    CMA.Core.ajax.urls.get_tasks_url = CMA.Core.ajax.urls.root_url + "task/all/list/";
    CMA.Core.ajax.urls.get_workers_url = CMA.Core.ajax.urls.root_url + "worker/all/list/";
    CMA.Core.ajax.urls.tasks_per_worker_url = CMA.Core.ajax.urls.root_url + "task/all/dispatched/byworker/count/";
    CMA.Core.ajax.urls.task_url = CMA.Core.ajax.urls.root_url + "view/dispatched_tasks/";
    CMA.Core.ajax.urls.pending_tasks_url = CMA.Core.ajax.urls.root_url + "task/all/dispatched/pending/count/";
    CMA.Core.ajax.urls.worker_processes_url = CMA.Core.ajax.urls.root_url + "worker/all/subprocess/count/";
    CMA.Core.ajax.urls.shutdown_worker_url = CMA.Core.ajax.urls.root_url + "worker/<placeHolder>/shutdown/";
    CMA.Core.ajax.urls.query_dispatched_tasks_url = CMA.Core.ajax.urls.root_url + "xy_query/dispatched_tasks/";
    CMA.Core.ajax.urls.task_url = "/celerymanagementapp/view/task/";
    CMA.Core.ajax.urls.worker_url = "/celerymanagementapp/view/task/";
    CMA.Core.ajax.urls.create_out_of_band_worker_url = CMA.Core.ajax.urls.root_url + "outofbandworker/";
    CMA.Core.ajax.urls.create_provider_url = CMA.Core.ajax.urls.root_url + "provider/";
}

CMA.Core.ajax.urls.loadTestUrls = function(){
    CMA.Core.ajax.urls.root_url = "/celerymanagementapp/site_media/test_data/";
    CMA.Core.ajax.urls.post_root_url = "/celerymanagementapp/test/post/";
    CMA.Core.ajax.urls.get_tasks_url = CMA.Core.ajax.urls.root_url + "tasks.json";
    CMA.Core.ajax.urls.get_workers_url = CMA.Core.ajax.urls.root_url + "workers.json";
    CMA.Core.ajax.urls.tasks_per_worker_url = CMA.Core.ajax.urls.root_url + "tasks_per_worker.json";
    CMA.Core.ajax.urls.pending_tasks_url = CMA.Core.ajax.urls.root_url + "tasks_pending.json";
    CMA.Core.ajax.urls.worker_processes_url = CMA.Core.ajax.urls.root_url + "worker_processes.json";
    CMA.Core.ajax.urls.shutdown_worker_url = CMA.Core.ajax.urls.post_root_url + "worker/<placeHolder>/shutdown/";
    CMA.Core.ajax.urls.query_dispatched_tasks_url = CMA.Core.ajax.urls.post_root_url + "xy_query/dispatched_tasks/";
    CMA.Core.ajax.urls.task_url = "/celerymanagementapp/test/view/task/";
    CMA.Core.ajax.urls.worker_url = "/celerymanagementapp/test/view/worker/";
    CMA.Core.ajax.urls.chart_data_url = CMA.Core.ajax.urls.root_url + "chart/enumerate-1.json";
    CMA.Core.ajax.urls.create_out_of_band_worker_url = CMA.Core.ajax.urls.post_root_url + "outofbandworker/";
    CMA.Core.ajax.urls.create_provider_url = CMA.Core.ajax.urls.post_root_url + "provider/";
}

CMA.Core.ajax.getTasks = function(callbackFunction){
    $.getJSON(CMA.Core.ajax.urls.get_tasks_url, callbackFunction);
}

CMA.Core.ajax.getWorkers = function(callbackFunction){
    $.getJSON(CMA.Core.ajax.urls.get_workers_url, callbackFunction);
}

CMA.Core.ajax.getTasksPerWorker = function(callbackFunction){
    $.getJSON(CMA.Core.ajax.urls.tasks_per_worker_url, callbackFunction);
}

CMA.Core.ajax.getPendingTasks = function(callbackFunction){
    $.getJSON(CMA.Core.ajax.urls.pending_tasks_url, callbackFunction);
}

CMA.Core.ajax.getWorkerProcesses = function(callbackFunction){
    $.getJSON(CMA.Core.ajax.urls.worker_processes_url, callbackFunction);
}

CMA.Core.ajax.postShutdownWorker = function(workerName, callbackFunction){
    $.post(CMA.Core.ajax.urls.shutdown_worker_url.replace("<placeHolder>", workerName), callbackFunction);
}

CMA.Core.ajax.getDispatchedTasksData = function(query, callbackFunction) {
    $.post(CMA.Core.ajax.urls.query_dispatched_tasks_url, query, callbackFunction);
}

CMA.Core.ajax.postCreateOutOfBandWorkerNode = function(callbackFunction){
    $.post(CMA.Core.ajax.urls.create_out_of_band_worker_url, $('#blankOutOfBandForm').serialize(), callbackFunction);
}

CMA.Core.ajax.postCreateProvider = function(callbackFunction){
    $.post(CMA.Core.ajax.urls.create_provider_url, $('#blankProviderForm').serialize(), callbackFunction);
}
