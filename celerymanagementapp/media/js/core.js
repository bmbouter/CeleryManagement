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

CMA.Core.util = (function(){

    var expand = function(elem) {
            $(elem).animate(
                { height: "toggle" },
                500,
                function(){}
            );
        },
        formReturn = function(data){
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
                    length = data.failure.length,
                    id = data.id;
                
                for( i=0; i < length; i += 1){
                    if( id !== null && id !== undefined ){
                        elem = document.getElementById(id + "_" + data.failure[i].field + "_error");
                    } else {
                        elem = document.getElementById(data.failure[i].field + "_error");
                    }
                    $(elem).text(setText);
                    if( $(elem).text() !== ""){                
                        $(elem).show();
                    } else {
                        $(elem).hide();
                    }
                }
            }
        },
        createPopup = function(text, buttonText){
            var leftPos, topPos, container,
                html = '<div id="boxes">' +
                            '<div id="popupContainer">' + 
                                '<div id="popupTextBox">' + 
                                    text +
                                '</div>' +
                                '<div id="popupButtonContainer">' + 
                                    '<button class="popupButton click left positiveButton" id="" >' + 'Yes' + '</button>' +
                                    '<button class="popupButton click left negativeButton" id="popupCancelButton" >' + 'Cancel' + '</button>' +
                                '</div>' +
                            '</div>' +
                            '<div id="mask"></div>' +
                        '</div>',
                windowHeight = $(window).height(),
                windowWidth = $(window).width();

                $("body").append(html);
                container = $('#popupContainer');
                leftPos = (windowWidth / 2) - (container.width() / 2);
                topPos = (windowHeight / 2) - (container.height() / 2);
                container.css({ "left": leftPos, "top": topPos });

                $('#mask').css({ "width": windowWidth + "px", "height": windowHeight + "px" });
                $('#mask').click(function(){
                    $('#boxes').remove();
                });

                $('#popupCancelButton').click(function(){
                    $('#boxes').remove();
                });

                container.show();
        };

    return {
        expand: expand,
        formReturn: formReturn,
        createPopup: createPopup
    };
}());


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
    
    $('#content').css("width", ($(window).width() - $('#dummy').css("width").split("px")[0] - 30) + "px");
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

CMA.Core.navigation = (function() {
    
    var ajax = CMA.Core.ajax,
        addNavigationElements = function(names, list, linkUrl, activeItem){
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
            addNavigationElements(data, $('#taskNavigation'), ajax.getUrls().task_url, CMA.Core.taskname);
        },
        populateWorkerNavigation = function(data){
            addNavigationElements(data, $('#workerNavigation'), ajax.getUrls().worker_url, CMA.Core.workername);
        };

    return {
        populateTaskNavigation: populateTaskNavigation,
        populateWorkerNavigation: populateWorkerNavigation
    };
}());


CMA.Core.policy = function(){
    var ajax = CMA.Core.ajax,
        util = CMA.Core.util,

        submitPolicy = function(){
            var form = {},
                
                formReturn = function(data){
                    var setText = function(){
                        var errLength = data.failure[i].error.length,
                            text = "";
                        for( j=0; j < errLength; j += 1){
                            text += data.failure[i].error[j];
                        }
                        return text;
                    };
                    console.log(data);
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
            
            form.name = $('#id_name').val();
            form.enabled = $('#id_enabled').attr("checked");
            form.source = $('#id_source').val();
         
            ajax.postCreatePolicy(form, formReturn);
        },
        deletePolicy = function(elem){
            var deleteReturn = function(data){
                    console.log(data);
                    if( !data.hasOwnProperty("failure") ){
                        elem.parent().remove();
                    }
                };
            ajax.postDeletePolicy(elem.attr("id"), deleteReturn);
        },
        editPolicy = function(id){
            var editReturn = function(data){
                console.log(data);
            };
            ajax.postEditPolicy(id, editReturn);
        };

    $('.policyForm').hide();

    $('.editPolicy').click(function(){
        var elem = document.getElementById($(this).attr("id") + "_policyForm");
        util.expand(elem);
    });
    $('.createPolicy').click(function() {
        util.expand($('#blankPolicyForm'));
    });
    $('#submitPolicyButton').click(submitPolicy);
    $('.deletePolicy').click(function(){
            deletePolicy($(this));
    });
    $('.submitPolicyEdit').click(function(){
            editPolicy($(this).attr("id"));
    });
};

CMA.Core.configure = (function(){
    var util = CMA.Core.util,
        ajax = CMA.Core.ajax,

        registerEvents = function() {
            if( CMA.Core.USE_MODE === "static" ){
                $('.outOfBandForm').hide();
                $('.editWorkerNode').click(function(){
                    var id = $(this).attr("id"),
                        split = id.split("_"),
                        that = this;
                    if( split[1] === "update" ){
                        util.expand(document.getElementById(split[0] + "_Form"));
                    } else if( split[1] === "delete" ){
                        util.createPopup("test", "Yes");
                        ajax.postDeleteOutOfBandWorker(split[0], function(data){
                            if( !data.hasOwnProperty("failure") ){
                                $(that).parent().remove();
                            }
                        });        
                    }
                });
                $('.createNewOutOfBand').click(function() {
                    util.expand($('#blankOutOfBandForm'));
                });
                $('.updateOutOfBandButton').click(function(){
                    var id = $(this).attr("id"),
                        split = id.split("_"),
                        form = document.getElementById(split[0] + "_Form");
                        ajax.postUpdateOutOfBandWorker($(form), split[0], util.formReturn);
                });
                ajax.postCreateOutOfBandWorker($('#blankOutOfBandForm'), util.formReturn);

            } else if( CMA.Core.USE_MODE === "dynamic" ){
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
                    ajax.postGetImages(handleImages);
                });
                
                $('#viewProvider').click(function(){
                    //$('#submitProviderButton').text("Close");
                    util.expand($('#providerFormWrapper'));
                });

                $('.deleteInstance').click(function() {
                    var pk = $(this).attr("id");
                        element = $(this).parent();
                    
                    ajax.postDeleteInstance(pk, function(data){
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
                
                $('#blankProviderForm').submit(function(){ return false; });
                if( $('#submitProviderButton').hasClass("positiveButton") ){
                    $('#submitProviderButton').click(function(){
                        ajax.postCreateProvider($('#blankProviderForm'), util.formReturn);
                    });
                } else if( $('#submitProviderButton').hasClass("negativeButton") ){
                    $('#submitProviderButton').click(function(){
                        //util.createPopup();
                        ajax.postDeleteProvider($('#providerID').text(),function(data){
                            if( !data.hasOwnProperty("failure") ){
                                $('#configurationManagement').children().remove();
                                var elem = $(data);
                                $('#configurationManagement').append(elem);
                                CMA.Core.configure.registerEvents();
                                $('textarea').attr("rows", "3");
                                $('textarea').css("resize", "none");
                            }
                        });
                    });
                }
            }
        };
    
    return {
        registerEvents: registerEvents
    };
}());

$(document).ready(function() {

    var core = CMA.Core;
    core.init();
    core.setupEvents();
    core.policy();
    core.configure.registerEvents();

    //core.ajax.getTasks(core.navigation.populateTaskNavigation);
    //core.ajax.getWorkers(core.navigation.populateWorkerNavigation);
    
});
