var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

CMACore.root_url = "/celerymanagementapp/get/"
CMACore.tasks_url = CMACore.root_url + "tasks/"

CMACore.getTasks = function(callbackFunction){
    $.getJSON(CMACore.tasks_url, callbackFunction);
}
