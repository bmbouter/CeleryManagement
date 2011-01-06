var CMA = (typeof CMA === "undefined" || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

$(document).ready(function() {

    CMA.Core.init();
    CMA.Core.setupEvents();
    CMA.Core.setupFormEvents();

    CMA.Core.getTasks(CMA.Core.populateTaskNavigation);
    CMA.Core.getWorkers(CMA.Core.populateWorkerNavigation);
    
    var xhr = jQuery.getJSON(CMA.Core.get_tasks_url);
    var obj = jQuery.parseJSON(xhr.responseText);
	
});

function createTable(data) {
    var table = $('.content');
    table.html(""); //Empty the content
    
    table.html("<table> </table>");
    
    data.each(function(i, e) {
        alert(i + " " + e);
    });
}

CMA.Core.init = function(){
    if( typeof CMA.Core.testUrls === "undefined" ){
        CMA.Core.ajax.urls.loadUrls();
    } else {
        CMA.Core.ajax.urls.loadTestUrls();
    }
    
    $('textarea').attr("rows", "3");
    $('textarea').css("resize", "none");

    CMA.Core.expandedTasks = false;
    CMA.Core.expandedWorkers = false;
    
    $('#content').css("width", ($(window).width() - $('#dummy').css("width").split("px")[0] - 10) + "px");
    if( $(window).height() > $('#container').css("min-height").split("px")[0] ){
        $('#navigation').css("height", ($(window).height() - $('#header').css("height").split("px")[0] - 2) + "px");
    } else {
        $('#navigation').css("height", $('#container').css("min-height"));
    }
}

CMA.Core.setupEvents = function(){
    
    $('#taskNavigationMaster').click(function (){
        if( CMA.Core.expandedTasks ){
            $('#taskNavigationMaster').text("+ Tasks");
            $('#taskNavigation').hide();   
            CMA.Core.expandedTasks = false;
        } else {
            $('#taskNavigationMaster').text("- Tasks");
            $('#taskNavigation').show();
            CMA.Core.expandedTasks = true;
        }
    });
    $('#workerNavigationMaster').click(function (){
        if( CMA.Core.expandedWorkers ){
            $('#workerNavigationMaster').text("+ Workers");
            $('#workerNavigation').hide();   
            CMA.Core.expandedWorkers = false;
        } else {
            $('#workerNavigationMaster').text("- Workers");
            $('#workerNavigation').show();
            CMA.Core.expandedWorkers = true;
        }
    });
    
    if( CMA.Core.taskname !== "undefined" ){
        $('#taskNavigationMaster').click();
    }
    if( CMA.Core.workername !== "undefined" ){
        $('#workerNavigationMaster').click();
    }

    $('.menuItem').hover(
        function() {
            var elem = $(this);
            var img = document.getElementById(elem.attr("id") + "Img");
            $(elem).toggleClass("menuItemHover rightRounded");
            $(img).toggleClass("menuItemHover leftRounded");
        },
        function() {
            var elem = $(this);
            var img = document.getElementById(elem.attr("id") + "Img");
            $(elem).toggleClass("menuItemHover rightRounded");
            $(img).toggleClass("menuItemHover leftRounded");
        }
    );

    $('.menuImg').hover(
        function() {
            var elem = $(this);
            var img = document.getElementById(elem.attr("id").split("Img")[0]);
            $(elem).toggleClass("menuItemHover leftRounded");
            $(img).toggleClass("menuItemHover rightRounded");
        },
        function() {
            var elem = $(this);
            var img = document.getElementById(elem.attr("id").split("Img")[0]);
            $(elem).toggleClass("menuItemHover leftRounded");
            $(img).toggleClass("menuItemHover rigtRounded");
        }
    );

    $(window).resize(function() {
        if( $(window).width() > $('#container').css("min-width").split("px")[0] ){
            $('#content').css("width", ($(window).width() - $('#dummy').css("width").split("px")[0] - 20) + "px");
        } 
        if( $(window).height() > $('#container').css("min-height").split("px")[0] ){
            $('#navigation').css("height", ($(window).height() - $('#header').css("height").split("px")[0] - 2) + "px");
        } else {
            $('#navigation').css("height", $('#container').css("min-height"));
        }
    });
}

CMA.Core.setupFormEvents = function(){
    var formReturn = function(data){
        if( !data.hasOwnProperty("failure") ){
            console.log("success");
        } else {
            var i = 0,
                elem,
                length = data.failure.length;
            
            for( i=0; i < length; i += 1){
                elem = document.getElementById(data.failure[i].field + "_error");
                $(elem).text(function(){
                    var errLength = data.failure[i].error.length,
                        text = "";
                    for( j=0; j < errLength; j += 1){
                        text += data.failure[i].error[j];
                    }
                    return text;
                });
                if( $(elem).text() !== ""){                
                    $(elem).show();
                } else {
                    $(elem).hide();
                }
            }
        }
    };

    $('.outOfBandForm').hide();

    $('#blankOutOfBandForm').ajaxForm({
        dataType: 'json',
        url: CMA.Core.create_out_of_band_worker_url,
        success: formReturn
    });

    $('.createNewOutOfBand').click(function() {
        var formHeight = $('#blankOutOfBandForm').height();
        $('#blankOutOfBandForm').animate({
                height: "toggle",
            },
            500,
            function(){
                $('#blankOutOfBandForm').css("height", formHeight + "px");
            }
        );
    });

    $('.editWorkerNode').click(function(){
        var elem = document.getElementById($(this).attr("id") + "Form");
        var formHeight = $(elem).height();
        $(elem).animate({
            height: "toggle",
            },
            500,
            function(){
                $(elem).css("height", formHeight + "px");
            }
        );
    });
    
    $('#blankProviderForm').ajaxForm({
        dataType: 'json',
        url: CMA.Core.create_provider_url,
        success: formReturn
    });
    
    /*$('.createNewProvider').click(function() {
        var formHeight = $('#providerForm').height();
        $('#blankProviderForm').animate({
                height: "toggle",
            },
            500,
            function(){
                $('#providerForm').css("height", formHeight + "px");
            }
        );
    });
    
    $('.editProvider').click(function(){
        var elem = document.getElementById($(this).attr("id") + "Form");
        var formHeight = $(elem).height();
        $(elem).animate({
            height: "toggle",
            },
            500,
            function(){
                $(elem).css("height", formHeight + "px");
            }
        );
    });*/
}

CMA.Core.populateTaskNavigation = function(data){
    var color = "#7D7D7D";
    for( item in data ){
        if( data[item] === CMA.Core.taskname ){
            color = "red";
        } else {
            color = "#7D7D7D";
        }
        if( data[item].length > 15 ){
            var task_text = "..." + data[item].substring(data[item].length - 15, data[item].length);
            $('#taskNavigation').append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMA.Core.task_url + data[item] + "/'>" + task_text + "</a></li>");
        } else {
            $('#taskNavigation').append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMA.Core.task_url + data[item] + "/'>" + data[item] + "</a></li>");
        }
    }
}

CMA.Core.populateWorkerNavigation = function(data){
    var color = "#7D7D7D";
    for( item in data ){
        if( data[item] === CMA.Core.workername ){
            color = "red";
        } else {
            color = "#7D7D7D";
        }
        if( data[item].length > 15 ){
            var worker_text = "..." + data[item].substring(data[item].length - 15, data[item].length);
            $('#workerNavigation').append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMA.Core.worker_url + data[item] + "/'>" + worker_text + "</a></li>");
        } else {
            $('#workerNavigation').append("<li><a id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMA.Core.worker_url + data[item] + "/'>" + data[item] + "</a></li>");
        }
    }
}

