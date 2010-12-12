var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;


$(document).ready(function() {
    
    CMACore.expandedTasks = false;
    var expandedWorkers = false;

    $('#navigation').css("height", ($(window).height() - $('#header').css("height").split("px")[0] - 2) + "px");
    $('#taskNavigationMaster').click(function (){
        if( CMACore.expandedTasks ){
            $('#taskNavigationMaster').text("+ Tasks");
            $('#taskNavigation').hide();   
            CMACore.expandedTasks = false;
        } else {
            $('#taskNavigationMaster').text("- Tasks");
            $('#taskNavigation').show();
            CMACore.expandedTasks = true;
        }
    });
    $('#workerNavigationMaster').click(function (){
        if( expandedWorkers ){
            $('#workerNavigationMaster').text("+ Workers");
            $('#workerNavigation').hide();   
            expandedWorkers = false;
        } else {
            $('#workerNavigationMaster').text("- Workers");
            $('#workerNavigation').show();
            expandedWorkers = true;
        }
    });
    
    var xhr = jQuery.getJSON(CMACore.get_tasks_url);
    var obj = jQuery.parseJSON(xhr.responseText);
    CMACore.getTasks(populateTaskNavigation);
    CMACore.getWorkers(populateWorkerNavigation);
	
    if( CMACore.taskname != "undefined" ){
        $('#taskNavigationMaster').click();
    }
    if( CMACore.workername != "undefined" ){
        $('#workerNavigationMaster').click();
    }

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

function populateTaskNavigation(data){
    var color = "#7D7D7D";
    for( item in data ){
        if( data[item] == CMACore.taskname ){
            color = "red";
        } else {
            color = "#7D7D7D";
        }
        if( data[item].length > 15 ){
            var task_text = "..." + data[item].substring(data[item].length - 15, data[item].length);
            $('#taskNavigation').append("<li><a style='color: " + color  + ";' id='" + data[item] + "' href='/celerymanagementapp/test/view/task/" + data[item] + "'>" + task_text + "</a></li>");
        } else {
            $('#taskNavigation').append("<li><a style='color: " + color  + ";' id='" + data[item] + "' href='/celerymanagementapp/test/view/task/" + data[item] + "'>" + data[item] + "</a></li>");
        }
    }
}

function populateWorkerNavigation(data){
    var color = "#7D7D7D";
    for( item in data ){
        if( data[item] == CMACore.workername ){
            color = "red";
        } else {
            color = "#7D7D7D";
        }
        if( data[item].length > 15 ){
            var worker_text = "..." + data[item].substring(data[item].length - 15, data[item].length);
            $('#workerNavigation').append("<li><a  style='color: " + color  + ";' id='" + data[item] + "' href='/celerymanagementapp/test/view/worker/" + data[item] + "'>" + worker_text + "</a></li>");
        } else {
            $('#workerNavigation').append("<li><a  style='color: " + color  + ";' id='" + data[item] + "' href='/celerymanagementapp/test/view/worker/" + data[item] + "'>" + data[item] + "</a></li>");
        }
    }
}
