var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

CMACore.root_url = "/celerymanagementapp/"
CMACore.tasks_url = CMACore.root_url + "get/tasks/"
CMACore.workers_url = CMACore.root_url + "get/workers/"
CMACore.tasks_per_worker_url = CMACore.root_url + "tasks_per_worker/"

CMACore.getTasks = function(callbackFunction){
    $.getJSON(CMACore.tasks_url, callbackFunction);
}

CMACore.getWorkers = function(callbackFunction){
    $.getJSON(CMACore.workers_url, callbackFunction);
}

CMACore.getTasksPerWorker = function(callbackFunction){
    $.getJSON(CMACore.tasks_per_worker_url, callbackFunction);
}
