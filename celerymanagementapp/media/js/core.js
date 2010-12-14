var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;


$(document).ready(function() {

    if( typeof CMACore.testUrls == "undefined" ){
        CMACore.loadUrls();
    } else {
        CMACore.loadTestUrls();
    }
    
    CMACore.expandedTasks = false;
    var expandedWorkers = false;
    $('textarea').attr("rows", "3");
    $('textarea').css("resize", "none");


    $('#navigation').css("height", ($(window).height() - $('#header').css("height").split("px")[0] - 2) + "px");
    $('#content').css("width", ($(window).width() - $('#dummy').css("width").split("px")[0] - 10) + "px");

    $(window).resize(function() {
        $('#content').css("width", ($(window).width() - $('#dummy').css("width").split("px")[0] - 10) + "px");
        $('#navigation').css("height", ($(window).height() - $('#header').css("height").split("px")[0] - 2) + "px");
    });
    
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
            $('#taskNavigation').append("<li><a style='color: " + color  + ";' id='" + data[item] + "' href='" + CMACore.task_url + data[item] + "/'>" + task_text + "</a></li>");
        } else {
            $('#taskNavigation').append("<li><a style='color: " + color  + ";' id='" + data[item] + "' href='" + CMACore.task_url + data[item] + "/'>" + data[item] + "</a></li>");
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
            $('#workerNavigation').append("<li><a  style='color: " + color  + ";' id='" + data[item] + "' href='" + CMACore.worker_url + data[item] + "/'>" + worker_text + "</a></li>");
        } else {
            $('#workerNavigation').append("<li><a  style='color: " + color  + ";' id='" + data[item] + "' href='" + CMACore.worker_url + data[item] + "/'>" + data[item] + "</a></li>");
        }
    }
}
