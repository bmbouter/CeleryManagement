var CMA = (typeof CMA === "undefined" || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

$(document).ready(function() {

    CMA.Core.init();
    CMA.Core.setupEvents();
    CMA.Core.setupFormEvents();
    CMA.Core.providerCreation();

    CMA.Core.ajax.getTasks(CMA.Core.populateTaskNavigation);
    CMA.Core.ajax.getWorkers(CMA.Core.populateWorkerNavigation);
    
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
        CMA.Core.ajax.loadUrls();
    } else {
        CMA.Core.ajax.loadTestUrls();
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

    var resizer = (function() {
            var wind = $(window),
                container = $('#container'),
                navigation = $('#navigation'),
    
                resize = function() {
                    if( wind.width() > container.css("min-width").split("px")[0] ){
                        $('#content').css("width", (wind.width() - $('#dummy').css("width").split("px")[0] - 20) + "px");
                    } 
                    if( wind.height() > container.css("min-height").split("px")[0] ){
                        navigation.css("height", (wind.height() - $('#header').css("height").split("px")[0] - 2) + "px");
                    } else {
                        navigation.css("height", container.css("min-height"));
                    }
                };

            return resize;
    }());

    $(window).resize(resizer);
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
    $('.policyForm').hide();

    $('#blankOutOfBandForm').ajaxForm({
        dataType: 'json',
        url: CMA.Core.ajax.urls.create_out_of_band_worker_url,
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
        url: CMA.Core.ajax.urls.create_provider_url,
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
    var color = "#7D7D7D",
        task_text = "",
        taskList = $('#taskNavigation'),
        clone = taskList.clone();

    for( item in data ){
        if( data[item] === CMA.Core.taskname ){
            color = "red";
        } else {
            color = "#7D7D7D";
        }
        if( data[item].length > 15 ){
            task_text = "..." + data[item].substring(data[item].length - 15, data[item].length);
            clone.append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMA.Core.ajax.urls.task_url + data[item] + "/'>" + task_text + "</a></li>");
        } else {
            clone.append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMA.Core.ajax.urls.task_url + data[item] + "/'>" + data[item] + "</a></li>");
        }
    }

    taskList.replaceWith(clone);
}

CMA.Core.populateWorkerNavigation = function(data){
    var color = "#7D7D7D",
        worker_text = "",
        workerList = $('#workerNavigation'),
        clone = workerList.clone();

    for( item in data ){
        if( data[item] === CMA.Core.workername ){
            color = "red";
        } else {
            color = "#7D7D7D";
        }

        if( data[item].length > 15 ){
            worker_text = "..." + data[item].substring(data[item].length - 15, data[item].length);
            clone.append("<li><a  id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMA.Core.ajax.urls.worker_url + data[item] + "/'>" + worker_text + "</a></li>");
        } else {
            clone.append("<li><a id='navigation_" + data[item]  + "' style='color: " + color  + ";' id='" + data[item] + "' href='" + CMA.Core.ajax.urls.worker_url + data[item] + "/'>" + data[item] + "</a></li>");
        }
    }
 
    workerList.replaceWith(clone);   
}

CMA.Core.providerCreation = function() {
    
    $('#getImagesButton').click(function() {
        var providerStep2 = $('#providerStep2');
            originalText = providerStep2.text();
        $(this).hide();
        providerStep2.show();
        providerStep2.text("Please wait while we determine the availible images...");
        CMA.Core.ajax.postGetImages(function(data) {
            window.setTimeout(function(){            console.log(data);
            providerStep2.text(originalText);
            }, 
            3000);
        });           
    });


};
