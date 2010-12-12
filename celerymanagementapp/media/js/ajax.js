var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

CMACore.loadUrls = function() {
    CMACore.root_url = "/celerymanagementapp/";
    CMACore.get_tasks_url = CMACore.root_url + "task/all/list/";
    CMACore.workers_url = CMACore.root_url + "worker/all/list/";
    CMACore.tasks_per_worker_url = CMACore.root_url + "task/all/dispatched/byworker/count/";
    CMACore.task_url = CMACore.root_url + "view/dispatched_tasks/";
    CMACore.pending_tasks_url = CMACore.root_url + "task/all/dispatched/pending/count/";
    CMACore.worker_processes_url = CMACore.root_url + "worker/all/subprocess/count/";
    CMACore.shutdown_worker_url = CMACore.root_url + "worker/<placeHolder>/shutdown/";
    CMACore.query_dispatched_tasks_url = CMACore.root_url + "xy_query/dispatched_tasks/";
}

CMACore.loadTestUrls = function(){
    CMACore.root_url = "/celerymanagementapp/site_media/test_data/";
    CMACore.get_root_url = "/celerymanagementapp/test/get/";
    CMACore.post_root_url = "/celerymanagementapp/test/post/";
    CMACore.get_tasks_url = CMACore.root_url + "tasks.json";
    CMACore.workers_url = CMACore.root_url + "workers.json";
    CMACore.tasks_per_worker_url = CMACore.root_url + "tasks_per_worker.json";
    CMACore.pending_tasks_url = CMACore.root_url + "tasks_pending.json";
    CMACore.worker_processes_url = CMACore.root_url + "worker_processes.json";
    CMACore.task_url = "/celerymanagementapp/test/view/task/";
    CMACore.shutdown_worker_url = CMACore.root_url + "successful_worker_shutdown.json";
    CMACore.query_dispatched_tasks_url = CMACore.post_root_url + "xy_query/dispatched_tasks/";
}

CMACore.getTasks = function(callbackFunction){
    $.getJSON(CMACore.get_tasks_url, callbackFunction);
}

CMACore.getWorkers = function(callbackFunction){
    $.getJSON(CMACore.workers_url, callbackFunction);
}

CMACore.getTasksPerWorker = function(callbackFunction){
    $.getJSON(CMACore.tasks_per_worker_url, callbackFunction);
}

CMACore.getPendingTasks = function(callbackFunction){
    $.getJSON(CMACore.pending_tasks_url, callbackFunction);
}

CMACore.getWorkerProcesses = function(callbackFunction){
    $.getJSON(CMACore.worker_processes_url, callbackFunction);
}

CMACore.postShutdownWorker = function(workerName, callbackFunction){
    $.post(CMACore.shutdown_worker_url.replace("<placeHolder>", workerName), callbackFunction);
}

CMACore.getDispatchedTasksData = function(query, callbackFunction) {
    $.post(CMACore.query_dispatched_tasks_url, query, callbackFunction);
}
