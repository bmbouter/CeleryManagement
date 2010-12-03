var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;
var CMASystem = (typeof CMASystem == "undefined" || !CMASystem) ? {} : CMASystem;

$(document).ready(function() {

    var systemRenderer = new SystemRenderer();
    systemRenderer.init();
    CMACore.getTasks(systemRenderer.createTasks);

});
