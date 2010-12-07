var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

CMACore.loadUrls = function() {
    CMACore.root_url = "/celerymanagementapp/";
    CMACore.get_tasks_url = CMACore.root_url + "task/all/list/";
    CMACore.workers_url = CMACore.root_url + "worker/all/list/";
    CMACore.tasks_per_worker_url = CMACore.root_url + "task/all/dispatched/byworker/count/";
    CMACore.task_url = CMACore.root_url + "view/dispatched_tasks/";
    CMACore.pending_tasks_url = CMACore.root_url + "task/all/dispatched/pending/count/";
    CMACore.worker_processes_url = CMACore.root_url + "worker/all/subprocess/count/";
}

CMACore.loadTestUrls = function(){
    CMACore.root_url = "/celerymanagementapp/site_media/test_data/";
    CMACore.get_tasks_url = CMACore.root_url + "tasks.json";
    CMACore.workers_url = CMACore.root_url + "workers.json";
    CMACore.tasks_per_worker_url = CMACore.root_url + "tasks_per_worker.json";
    CMACore.pending_tasks_url = CMACore.root_url + "tasks_pending.json";
    CMACore.worker_processes_url = CMACore.root_url + "worker_processes.json";
    CMACore.task_url = CMACore.root_url + "/celerymanagementapp/view/dispatched_tasks/";
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
