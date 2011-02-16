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

CMA.Core.util = (function($){
    var expand = function(elem) {
            $(elem).animate(
                { height: "toggle" },
                500,
                function(){}
            );
        },
        showStatus = function(text){
            $('#statusText').text(text);
            $('#statusText').show();
            $('#statusText').fadeOut(6000, function() {});
        },
        formSubmit = function(element, submitFunction, form, kwargs){
            var formReturn = function(data){
                    var setText = function(){
                            var errLength = data.failure[i].error.length,
                                text = "";
                            for( j=0; j < errLength; j += 1){
                                text += data.failure[i].error[j];
                            }
                            return text;
                        };
                    
                    if( !data.hasOwnProperty("failure") ){
                        if( typeof kwargs.successCallback === "undefined" ){
                            showStatus(data);
                            expand(element);
                        } else {
                            kwargs.successCallback(data);
                            expand(element);
                        }
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
                };
            if( kwargs.urlID ){
                submitFunction(form, kwargs.urlID, formReturn);
            } else {
                submitFunction(form, formReturn);
            }
        },
        createPopup = function(text, successCallback){
            var leftPos, topPos, container,
                html = '<div id="boxes">' +
                            '<div id="popupContainer">' + 
                                '<div id="popupTextBox">' + 
                                    text +
                                '</div>' +
                                '<div id="popupButtonContainer">' + 
                                    '<button class="popupButton click left positiveButton" id="popupYesButton" >' + 'Yes' + '</button>' +
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
                $('#popupYesButton').click(function(){ 
                    successCallback();
                    $('#boxes').remove();
                });

                container.show();
        },
        checkTab = function(evt){
            var t = evt.target,
                ss = t.selectionStart,
                se = t.selectionEnd,
                tab = "    ";
         
            // Tab key - insert tab expansion
            if (evt.keyCode == 9) {
                evt.preventDefault();
                       
                // Special case of multi line selection
                if (ss != se && t.value.slice(ss,se).indexOf("\n") != -1) {
                    // In case selection was not of entire lines (e.g. selection begins in the middle of a line)
                    // we ought to tab at the beginning as well as at the start of every following line.
                    var pre = t.value.slice(0,ss);
                    var sel = t.value.slice(ss,se).replace(/\n/g,"\n"+tab);
                    var post = t.value.slice(se,t.value.length);
                    t.value = pre.concat(tab).concat(sel).concat(post);
                           
                    t.selectionStart = ss + tab.length;
                    t.selectionEnd = se + tab.length;
                }
                       
                // "Normal" case (no selection or selection on one line only)
                else {
                    t.value = t.value.slice(0,ss).concat(tab).concat(t.value.slice(ss,t.value.length));
                    if (ss == se) {
                        t.selectionStart = t.selectionEnd = ss + tab.length;
                    }
                    else {
                        t.selectionStart = ss + tab.length;
                        t.selectionEnd = se + tab.length;
                    }
                }
            }
                   
            // Backspace key - delete preceding tab expansion, if exists
           else if (evt.keyCode==8 && t.value.slice(ss - 4,ss) == tab) {
                evt.preventDefault();
                       
                t.value = t.value.slice(0,ss - 4).concat(t.value.slice(ss,t.value.length));
                t.selectionStart = t.selectionEnd = ss - tab.length;
            }
                   
            // Delete key - delete following tab expansion, if exists
            else if (evt.keyCode==46 && t.value.slice(se,se + 4) == tab) {
                evt.preventDefault();
                     
                t.value = t.value.slice(0,ss).concat(t.value.slice(ss + 4,t.value.length));
                t.selectionStart = t.selectionEnd = ss;
            }
            // Left/right arrow keys - move across the tab in one go
            else if (evt.keyCode == 37 && t.value.slice(ss - 4,ss) == tab) {
                evt.preventDefault();
                t.selectionStart = t.selectionEnd = ss - 4;
            }
            else if (evt.keyCode == 39 && t.value.slice(ss,ss + 4) == tab) {
                evt.preventDefault();
                t.selectionStart = t.selectionEnd = ss + 4;
            }
        };

    return {
        expand: expand,
        formSubmit: formSubmit,
        createPopup: createPopup,
        checkTab: checkTab,
        showStatus: showStatus
    };
}(jQuery));

CMA.Core.init = function(){
    if( typeof CMA.Core.testUrls === "undefined" ){
        CMA.Core.ajax.loadUrls();
    } else {
        CMA.Core.ajax.loadTestUrls();
    }
 
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


CMA.Core.policy = (function(){
    var ajax = CMA.Core.ajax,
        util = CMA.Core.util,
        defaultSourceText = 'policy:\n' + 
                            '    schedule:\n' +  
                            '\tcrontab(minute="*/1")\n' + 
                            '    condition:\n' + 
                            '\tTrue\n' + 
                            '    apply:\n' + 
                            '\tprint "in policy apply..."',

        submitPolicy = function(){
            var form = {},
                success = function(data){
                    util.showStatus(data.success);
                    $('#configurationManagement').append(data.html);
                    $('.policyForm').hide();

                    $('#' + data.pk + '_update').click(function(){
                        var elem = document.getElementById($(this).attr("id").split("_")[0] + "_Form");
                        util.expand(elem);
                    });
                    $('#' + data.pk + "_delete").click(function(){
                            deletePolicy($(this));
                    });
                    $('#' + data.pk + "_editButton").click(function(){
                        var id = $(this).attr("id"),
                            split = id.split("_"),
                            form = document.getElementById(split[0] + "_Form");
                        util.formSubmit($(this).parent(), ajax.postUpdatePolicy, $(form).serialize(), 
                            { "urlID": split[0] });
                    });
                    $('textarea').keydown(util.checkTab);
                };
                
            form.name = $('#id_name').val();
            form.enabled = $('#id_enabled').attr("checked");
            form.source = $('#id_source').val();
         
            util.formSubmit($(this).parent(), ajax.postCreatePolicy, form, 
                    { "successCallback": success });
        },
        deletePolicy = function(elem){
            util.createPopup("Are you sure you wish to delete policy " + $(elem).parent().children(':first').text()  + " ?",
                function(){
                    ajax.postDeletePolicy(elem.attr("id").split("_")[0], function(data){
                        if( !data.hasOwnProperty("failure") ){
                            elem.parent().remove();
                            var elemID = elem.attr("id").split("_")[0];
                            $('#' + elemID + "_Form").remove();
                            util.showStatus(data);
                        } else {
                            util.showStatus(data.failure);
                        }
                    });
                }
            );
        },
        registerEvents = function(){ 

            $('textarea').attr("rows", "10");
            $('textarea').css("resize", "none");
            $('.policyForm').hide();

            $('.editPolicy').click(function(){
                var elem = document.getElementById($(this).attr("id").split("_")[0] + "_Form");
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
                var id = $(this).attr("id"),
                    split = id.split("_"),
                    form = document.getElementById(split[0] + "_Form");
                util.formSubmit($(this).parent(), ajax.postUpdatePolicy, $(form).serialize(), 
                    { "urlID": split[0] });
            });
            $('textarea').keydown(util.checkTab);
            $('#blankPolicyForm').children().find('#id_source').val(defaultSourceText);
        };

    return {
        registerEvents: registerEvents
    };
}());

CMA.Core.configure = (function(){
    var util = CMA.Core.util,
        ajax = CMA.Core.ajax,

        registerEvents = function() {
            if( CMA.Core.USE_MODE === "static" ){
                var success = function(data){
                    $('#configurationManagement').append(unescape(data.html));
                    $('.outOfBandForm').hide();

                    $('#' + data.pk + '_update').click(function(){
                        var elem = document.getElementById($(this).attr("id").split("_")[0] + "_Form");
                        util.expand(elem);
                    });
                    $('#' + data.pk + "_delete").click(function(){
                        var id = $(this).attr("id"),
                            split = id.split("_"),
                            that = this;
                        util.createPopup("Are you sure you wish to delete worker instance " + 
                            $(that).parent().children(':first').text() + "?", 
                            function(){
                                ajax.postDeleteOutOfBandWorker(split[0], function(data){
                                    if( !data.hasOwnProperty("failure") ){
                                        $(that).parent().remove();
                                        $('#' + split[0] + "_Form").remove();
                                    } else {
                                        util.showStatus(data.failure);
                                    }
                                });        
                            });
                    });
                    $('#' + data.pk + "_editButton").click(function(){
                        var id = $(this).attr("id"),
                            split = id.split("_"),
                            form = document.getElementById(split[0] + "_Form");
                        util.formSubmit($(this).parent(), ajax.postUpdateOutOfBandWorker, $(form), 
                                { "urlID": split[0] });
                    });

                    $('textarea').keydown(util.checkTab);
                    $('textarea').attr("rows", "3");
                    $('textarea').css("resize", "none");

                    $('#blankOutOfBandForm')[0].reset();
                },
                updateSuccess = function(){
                
                };

                $('textarea').attr("rows", "3");
                $('textarea').css("resize", "none");
                $('.outOfBandForm').hide();
                $('.editWorkerNode').click(function(){
                    var id = $(this).attr("id"),
                        split = id.split("_"),
                        that = this;
                    if( split[1] === "update" ){
                        util.expand(document.getElementById(split[0] + "_Form"));
                    } else if( split[1] === "delete" ){
                        util.createPopup("Are you sure you wish to delete worker instance " + $(that).parent().children(':first').text() + "?", 
                            function(){
                                ajax.postDeleteOutOfBandWorker(split[0], function(data){
                                    if( !data.hasOwnProperty("failure") ){
                                        $(that).parent().remove();
                                        $('#' + split[0] + "_Form").remove();
                                    } else {
                                        util.showStatus(data.failure);
                                    }
                                });        
                            });
                    } else if( split[1] === "power" ) {
                        if( $(that).parent().hasClass("active") ){
                            ajax.postShutdownWorker(split[0], function(data){
                                console.log(data);
                                $(that).parent().removeClass("active");
                                $(that).parent().addClass("inactive");
                                $(that).children('span').text("Power On");
                            });
                        } else {
                            ajax.postWorkerPower(split[0], {"power_state": "on"}, function(data){
                                $(that).parent().removeClass("inactive");
                                $(that).parent().addClass("active");
                                $(that).children('span').text("Power Off");
                                $(that).children('img').attr("src", "../../../site_media/images/power-off.png");
                            });
                        }
                    }
                });
                $('.createNewOutOfBand').click(function() {
                    util.expand($('#blankOutOfBandForm'));
                });
                $('.updateOutOfBandButton').click(function(){
                    var id = $(this).attr("id"),
                        split = id.split("_"),
                        form = document.getElementById(split[0] + "_Form");
                        util.formSubmit($(this).parent(), ajax.postUpdateOutOfBandWorker, $(form), 
                            { "urlID": split[0], 
                            "successCallback": updateSuccess });
                });
                $('#submitOutOfBandButton').click(function(){
                    util.formSubmit($('#blankOutOfBandForm'), ajax.postCreateOutOfBandWorker, $('#blankOutOfBandForm'), 
                        { "successCallback": success});
                });
                $('#blankOutOfBandForm').submit(function(){ return false; });

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
                    $('textarea').attr("rows", "3");
                    $('textarea').css("resize", "none");
                    util.expand($('#providerFormWrapper'));
                });

                $('.deleteInstance').click(function() {
                    var pk = $(this).attr("id");
                        element = $(this).parent();
                    
                    ajax.postDeleteInstance(pk, function(data){
                        if( data.hasOwnProperty("failure") ){
                            util.showStatus(data.failure);
                        } else {
                            element.remove();
                            util.showStatus(data);
                        }
                    });
                });
                
                $('#blankProviderForm').submit(function(){ return false; });
                if( $('#submitProviderButton').hasClass("positiveButton") ){
                    $('#submitProviderButton').click(function(){
                        util.formSubmit($(this).parent(), ajax.postCreateProvider, $('#blankProviderForm'));
                    });
                } else if( $('#submitProviderButton').hasClass("negativeButton") ){
                    $('#submitProviderButton').click(function(){
                        util.createPopup("WARNING: Deleting a provider will delete all Worker instances.  Are you sure you wish to continue?",
                            function(){
                                ajax.postDeleteProvider($('#providerID').text(), function(data){
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
    if( CMA.Core.USE_MODE === "dynamic" ){
        core.policy.registerEvents();
    }
    core.configure.registerEvents();

    //core.ajax.getTasks(core.navigation.populateTaskNavigation);
    //core.ajax.getWorkers(core.navigation.populateWorkerNavigation);
    
});
