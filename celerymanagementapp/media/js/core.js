var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

var systemViewer;

$(document).ready(function() {
    
    systemViewer = new SystemViewer();
    systemViewer.init();
    
    var xhr = jQuery.getJSON(CMACore.get_tasks_url);
	var obj = jQuery.parseJSON(xhr.responseText);
	
	/*int length = obj.length;*/
});


//setInterval(refresh, 10000);