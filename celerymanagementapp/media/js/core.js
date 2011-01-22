var CMA = (typeof CMA === "undefined" || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;
CMA.Core.ajax = (typeof CMA.Core.ajax === "undefined" || !CMA.Core.ajax) ? {} : CMA.Core.ajax;


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
};

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
};

CMA.Core.setupFormEvents = function(){
    var formReturn = function(data){
        console.log(data);
        var setText = function(){
                var errLength = data.failure[i].error.length,
                    text = "";
                for( j=0; j < errLength; j += 1){
                    text += data.failure[i].error[j];
                }
                return text;
            };

        if( !data.hasOwnProperty("failure") ){
            console.log("success");
        } else {
            var i = 0,
                elem,
                length = data.failure.length;
            
            for( i=0; i < length; i += 1){
                elem = document.getElementById(data.failure[i].field + "_error");
                $(elem).text(setText);
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
        url: CMA.Core.ajax.getUrls().create_out_of_band_worker_url,
        success: formReturn
    });
    
    $('#blankProviderForm').ajaxForm({
        dataType: 'json',
        url: CMA.Core.ajax.getUrls().create_provider_url,
        success: formReturn
    });

    $('.createNewOutOfBand').click(function() {
        var formHeight = $('#blankOutOfBandForm').height();
        $('#blankOutOfBandForm').animate({
                height: "toggle"
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
                height: "toggle"
            },
            500,
            function(){
                $(elem).css("height", formHeight + "px");
            }
        );
    });
    
};


CMA.Core.navigation = (function() {
    
    var addNavigationElements = function(names, list, linkUrl, activeItem){
            var color = "#7D7D7D",
                clone = list.clone(),
                length = names.length,
                name, i, displayText,
                
                createTaskElement = function(name, displayName, color){
                    clone.append("<li><a  id='navigation_" + name  + 
                                "' style='color: " + color  + 
                                ";' id='" + name + 
                                "' href='" + linkUrl + name + "/'>" + 
                                displayName + "</a></li>");
                };
            
            for(i = 0; i < length; i += 1){
                name = names[i];
                color = (name === activeItem) ? "red" : "#7D7D7D";
                displayText = (name.length > 15) ? "..." + name.substring(name.length - 15, name.length) : name;
                createTaskElement(name, displayText, color);
            }
            list.replaceWith(clone);
        },
        populateTaskNavigation = function(data){
            addNavigationElements(data, $('#taskNavigation'), CMA.Core.ajax.getUrls().task_url, CMA.Core.taskname);
        },
        populateWorkerNavigation = function(data){
            addNavigationElements(data, $('#workerNavigation'), CMA.Core.ajax.getUrls().worker_url, CMA.Core.workername);
        };

    return {
        populateTaskNavigation: populateTaskNavigation,
        populateWorkerNavigation: populateWorkerNavigation
    };
}());

CMA.Core.providerCreation = function() {
    var handleImages = function(data) {
            var providerStep2 = $('#providerStep2'),
                div, length, i, element;

            if( !data.hasOwnProperty("failure") ){
                div = '<div class="fieldWrapper">';
                length = data.length;
                
                for(i=0; i < length; i += 1){
                    div += '<input class="imageID" type="radio" name="image_id" value="' + data[i].id + '">' + data[i].name + '<br/>';
                }
                div += '</div>';
                
                providerStep2.text("Step 2: Please choose the image ID to be used.");
                element = $(div);
                providerStep2.append(element);
                $('#providerStep3').show();
                $('#submitProviderButton').show();
                $('.fieldWrapper').show();
            } else {
                providerStep2.text(originalText);
            }
        };
    
    $('#getImagesButton').click(function() {
        var providerStep2 = $('#providerStep2');
        
        $(this).hide();
        providerStep2.text("Please wait while we determine the availible images...");
        providerStep2.show();
        CMA.Core.ajax.postGetImages(handleImages);
    });
    
    $('#viewProvider').click(function(){
        //$('#submitProviderButton').text("Close");
        $('#providerFormWrapper').animate({
                height: "toggle"
            },
            500,
            function(){}
        );
    });

    $('.deleteInstance').click(function() {
        var pk = $(this).attr("id");
            element = $(this).parent();
        CMA.Core.ajax.postDeleteInstance(pk, function(data){
            if( data.hasOwnProperty("failure") ){
                $('#statusText').show();
                $('#statusText').text(data.failure);
            } else {
                element.remove();
                $('#statusText').show();
                $('#statusText').text("Instance successfully deleted.");
                $('#statusText').fadeOut(3000, function() {});
            }
        });
    });

};

CMA.Core.policy = function(){
    var expandPolicy = function(){
            console.log("expanding");
            var elem = document.getElementById($(this).attr("id") + "_policyForm"),
                formHeight = $(elem).height();
            
            $(elem).animate({
                    height: "toggle"
                },
                500,
                function(){
                    $(elem).css("height", formHeight + "px");
                }
            );
        };

    $('.editPolicy').click(expandPolicy);
};

$(document).ready(function() {

    var core = CMA.Core;
    core.init();
    core.setupEvents();
    core.setupFormEvents();
    core.providerCreation();
    core.policy();

    core.ajax.getTasks(core.navigation.populateTaskNavigation);
    core.ajax.getWorkers(core.navigation.populateWorkerNavigation);
    
});
