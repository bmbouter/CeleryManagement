var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

var systemViewer;

$(document).ready(function() {
    
    systemViewer = new SystemViewer();
    systemViewer.init();
    
    var xhr = jQuery.getJSON(CMACore.get_tasks_url);
	var obj = jQuery.parseJSON(xhr.responseText);
	
	/*int length = obj.length;
	
	for(int i = 0; i < length; i++) {
	    
	}
	
	$('.content').html();*/
	
	//createTable(obj);
});

function createTable(data) {
    var table = $('.content');
    table.html(""); //Empty the content
    
    table.html("<table> </table>");
    
    data.each(function(i, e) {
        alert(i + " " + e);
    });
}

function refresh(){
    systemViewer.refresh();
}

//setInterval(refresh, 10000);

