var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

CMACore.root_url = "/celerymanagementapp/";
CMACore.get_tasks_url = CMACore.root_url + "task/all/list/";
CMACore.workers_url = CMACore.root_url + "worker/all/list/";
CMACore.tasks_per_worker_url = CMACore.root_url + "task/all/dispatched/byworker/count/";
CMACore.task_url = CMACore.root_url + "view/dispatched_tasks/";

CMACore.getTasks = function(callbackFunction){
    $.getJSON(CMACore.get_tasks_url, callbackFunction);
}

CMACore.getWorkers = function(callbackFunction){
    $.getJSON(CMACore.workers_url, callbackFunction);
}

CMACore.getTasksPerWorker = function(callbackFunction){
    $.getJSON(CMACore.tasks_per_worker_url, callbackFunction);
}
