var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;
var CMASystem = (typeof CMASystem == "undefined" || !CMASystem) ? {} : CMASystem;

var tasksUrl = '../../get/tasks';

$(document).ready(function() {
    
    var systemRenderer = new SystemRenderer();
    systemRenderer.init();
    
    var xhr = jQuery.getJSON(tasksUrl);
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
