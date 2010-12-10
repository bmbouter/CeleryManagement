var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;


$(document).ready(function() {
    
    $('#navigation').css("height", ($(window).height() - $('#header').css("height").split("px")[0]) + "px");
    
    var xhr = jQuery.getJSON(CMACore.get_tasks_url);
	var obj = jQuery.parseJSON(xhr.responseText);
	
	/*int length = obj.length;*/
});

function createTable(data) {
    var table = $('.content');
    table.html(""); //Empty the content
    
    table.html("<table> </table>");
    
    data.each(function(i, e) {
        alert(i + " " + e);
    });
}

