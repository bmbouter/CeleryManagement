var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

$(document).ready(function() {
    var systemRenderer = new SystemRenderer();
    systemRenderer.init();
});
