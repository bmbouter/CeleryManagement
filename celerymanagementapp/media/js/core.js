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

    $('.outOfBandForm').hide();
    $('#createNewOutOfBand').click(function() {
        $('#blankOutOfBandForm').animate({
                height: "toggle",
            },
            500,
            function(){}
        );
    });
    $('.editWorkerNode').click(function(){
        var elem = document.getElementById($(this).attr("id") + "Form");
        $(elem).animate({
            height: "toggle",
            },
            500,
            function() {}
        );
    });

    $('#content').css("width", ($(window).width() - $('#dummy').css("width").split("px")[0] - 10) + "px");
    if( $(window).height() > $('#container').css("min-height").split("px")[0] ){
        $('#navigation').css("height", ($(window).height() - $('#header').css("height").split("px")[0] - 2) + "px");
    } else {
        $('#navigation').css("height", $('#container').css("min-height"));
    }

    $(window).resize(function() {
        $('#content').css("width", ($(window).width() - $('#dummy').css("width").split("px")[0] - 10) + "px");
        if( $(window).height() > $('#container').css("min-height").split("px")[0] ){
            $('#navigation').css("height", ($(window).height() - $('#header').css("height").split("px")[0] - 2) + "px");
        } else {
            $('#navigation').css("height", $('#container').css("min-height"));
        }
    });
    
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
            $('#taskNavigation').append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMACore.task_url + data[item] + "/'>" + task_text + "</a></li>");
        } else {
            $('#taskNavigation').append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMACore.task_url + data[item] + "/'>" + data[item] + "</a></li>");
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
            $('#workerNavigation').append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMACore.worker_url + data[item] + "/'>" + worker_text + "</a></li>");
        } else {
            $('#workerNavigation').append("<li><a id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMACore.worker_url + data[item] + "/'>" + data[item] + "</a></li>");
        }
    }
}
