var System = (typeof System === "undefined" || !System) ? {} : System;
var CMA = (typeof CMA === "undefined" || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

System.Handlers = (function() {
    var Core = CMA.Core;
    
    var loadHandlers = function() {
        System.EventBus.addEventHandler('formatData', Core.DataParser.formatData);
        System.EventBus.addEventHandler('dataFormatted', Core.QuerySystem.startChart);
    };
    
    return {
        loadHandlers: loadHandlers 
    };
}());