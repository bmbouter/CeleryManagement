var CMA = ( CMA === undefined || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

CMA.SystemDisplay = {};


CMA.SystemDisplay.refresh = function(){
    CMA.SystemDisplay.fire("Refresh");
    $('#statusText').text("Refreshing view...");
    $('#statusText').fadeOut("slow", function() {});
    $('#statusText').show();
    $('#statusText').fadeIn("slow", function() {});
    $('#statusText').fadeOut("slow", function() {});
    $('#statusText').fadeIn("slow", function() {});
    $('#statusText').fadeOut("slow", function() {});
    $('#statusText').fadeIn("slow", function() {});
    $('#statusText').fadeOut(2000, function() {});
    console.log("refreshed");
};


CMA.SystemDisplay.Controller = function(){
    var canvasElement = $('#systemCanvas'),
        canvas = $('#systemCanvas')[0],
        ajax = CMA.Core.ajax;
        canvas.width = $(window).width() - $('#dummy').css("width").split("px")[0];

    var modelFactory = CMA.SystemDisplay.ModelFactory(canvas);

    ajax.getTasks(modelFactory.createTasks);
    ajax.getWorkers(modelFactory.createWorkers);
   
    var viewer = CMA.SystemDisplay.Viewer(modelFactory, canvas, canvasElement),
        systemEventHandler = CMA.SystemDisplay.EventHandler(canvasElement, viewer, modelFactory);
};

CMA.SystemDisplay.ModelFactory = function(canvas){
    var tasks = {},
        workers = {},
        connectors = [],
        workersSet = false,
        tasksSet = false,
        canvasHeight = 0,
        connectorWeight = 0,
        ajax = CMA.Core.ajax,
            
        createWorkers = function(data){
            var y = 40,
                i = 0,
                length = data.length;

            workers = {};
            
            for (i=0; i < length; i += 1){
                workers[data[i]] = CMA.SystemDisplay.Worker(y, canvas.width, data[i], data[i], true);
                y += 60;
            }

            if( y > canvasHeight ){
                canvasHeight = y;
            }

            ajax.getWorkerProcesses(setWorkerProcesses);
            workersSet = true;
            if( tasksSet ){
                ajax.getTasksPerWorker(createConnectors);
            }
        },

        createTasks = function(data){
            var y = 40,
                i = 0,
                length = data.length;
            
            tasks = {};

            for(i=0; i < length; i += 1){
                tasks[data[i]] = CMA.SystemDisplay.Task(y, data[i]);
                y += 60;
            }

            if( y > canvasHeight ){
                canvasHeight = y;
            }

            ajax.getPendingTasks(setPendingTasks);
            tasksSet = true;
            if( workersSet ){
                ajax.getTasksPerWorker(createConnectors);
            }
        },

        createConnectors = function(data){
            var num, task, worker;
            
            console.log(data);

            connectors = [];
            connectorWeight = 0;

            for( task in tasks ){
                if( tasks.hasOwnProperty(task) ){
                    for( worker in workers ){
                        if( workers.hasOwnProperty(worker) ){
                            num = data[task][worker];
                            if( num ){
                                connectors.push(CMA.SystemDisplay.Connector(tasks[task], workers[worker], num));
                                connectorWeight += num;
                            }
                        }
                    }
                }
            }
            console.log("test");
            CMA.SystemDisplay.fire("Redraw");
        },

        setPendingTasks = function(data){
            var item;
            for( item in data ){
                if( data.hasOwnProperty(item) ){
                    tasks[item].pending = data[item];
                }
            }
            CMA.SystemDisplay.fire("Redraw");
        },

        setWorkerProcesses = function(data){
            var item;
            for( item in data ){
                if( data.hasOwnProperty(item) ){
                    workers[item].processes = data[item];
                }
            }
            CMA.SystemDisplay.fire("Redraw");
        },

        getWorkers = function(){
            return workers;
        },

        getTasks = function(){
            return tasks;
        },

        getConnectors = function(){
            return connectors;
        },
        
        getCanvasHeight = function(){
            return canvasHeight;
        },
        
        getConnectorsWeight = function(){
            return connectorWeight;
        },
        
        setConnectorsWeight = function(weight){
            connectorWeight = weight;
        };

    return {
        getTasks: getTasks,
        getWorkers: getWorkers,
        getConnectors: getConnectors,
        getCanvasHeight: getCanvasHeight,
        getConnectorsWeight: getConnectorsWeight,
        setConnectorsWeight: setConnectorsWeight,
        createTasks: createTasks,
        createWorkers: createWorkers
    };
};

CMA.SystemDisplay.Viewer = function(modelFactory, canvas, canvasElement){
    
    var expandedTask = false,
        expandedWorker = false,
        canvasHeight = 0,
        systemRenderer = CMA.SystemDisplay.Renderer(canvas, modelFactory),
        dummyWidth = $('#dummy').css("width").split("px")[0],
        ajax = CMA.Core.ajax,

        connectorWeightingFunction = function(size){
            return (size / modelFactory.getConnectorsWeight() + 0.35) * 4;
        },

        redraw = function(){
            var workers, worker, item, connectors, connector;
            canvas.width = $(window).width() - dummyWidth - 20;
            
            if( $(window).width() > $('#container').css("min-width").split("px")[0] ){
                workers = modelFactory.getWorkers();
                connectors = modelFactory.getConnectors();
                for( item in workers ){
                    if( workers.hasOwnProperty(item) ){
                        worker = workers[item];
                        worker.x = canvas.width - worker.width - 100;
                        worker.xCenter = (worker.width / 2) + worker.x;
                    }
                }
                //CMA.Core.ajax.getTasksPerWorker(createConnectors);
            }
            draw();
        },

        draw = function(){
            var connectors = modelFactory.getConnectors(),
                tasks = modelFactory.getTasks(),
                workers = modelFactory.getWorkers(),
                task, worker, connector;
            
            systemRenderer = CMA.SystemDisplay.Renderer(canvas, modelFactory);
            canvas.width = $(window).width() - $('#dummy').css("width").split("px")[0];
            
            for( connector in connectors ){
                if( connectors.hasOwnProperty(connector) ){
                    systemRenderer.drawConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
                }
            }
            for( task in tasks ){
                if( tasks.hasOwnProperty(task) ){
                    systemRenderer.drawTask(tasks[task]);
                }
            }
            for( worker in workers ){
                if( workers.hasOwnProperty(worker) ){
                    systemRenderer.drawWorker(workers[worker]);
                }
            }
        },
    
        showTaskConnectors = function(task){
            var connectors = modelFactory.getConnectors(),
                connector;
            for( connector in connectors ){
                if( connectors.hasOwnProperty(connector) ){
                    if( connectors[connector].task.fullName === task.fullName ){
                        systemRenderer.highlightConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
                    }
                }
            }
        },

        showWorkerConnectors = function(worker){
            var connectors = modelFactory.getConnectors(),
                connector;
            for( connector in connectors ){
                if( connectors.hasOwnProperty(connector) ){
                    if( connectors[connector].worker.fullName === worker.fullName ){
                        systemRenderer.highlightConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
                    }
                }
            }
        },
        
        expandTask = function(task, expand){
            var newTask;
            if( expand ){
                if( task.fullName !== task.displayName ){
                    newTask = CMA.SystemDisplay.Task(task.y, task.fullName);
                    newTask.width = task.fullName.length * 6.8;
                    newTask.x = task.x - ((newTask.width - task.width) / 2);
                    newTask.displayName = task.fullName;
                    newTask.pending = task.pending;
                    systemRenderer.drawTask(newTask);
                    expandedTask = newTask;
                } else {
                    expandedTask = task;
                }
            } else {
                newTask = CMA.SystemDisplay.Task(task.y, task.displayName);
                systemRenderer.clearCanvas();
                draw();
                expandedTask = false;
            }
        },

        expandWorker = function(worker, expand){
            var newWorker;
            if( expand ){
                if( worker.fullName !== worker.displayName ){
                    newWorker = CMA.SystemDisplay.Worker(worker.y, canvas.width, worker.id, worker.fullName, worker.active);
                    newWorker.width = worker.fullName.length * 7;
                    newWorker.x = worker.x - ((newWorker.width - worker.width) / 2);
                    newWorker.displayName = worker.fullName;
                    newWorker.processes = worker.processes;
                    systemRenderer.drawWorker(newWorker);
                    expandedWorker = newWorker;
                } else {
                    expandedWorker = worker;
                }
            } else {
                newWorker = CMA.SystemDisplay.Worker(worker.y, canvas.width, worker.id, worker.displayName, worker.active);
                systemRenderer.clearCanvas();
                draw();
                expandedWorker = false;
            }
        },

        refresh = function(){
            ajax.getTasks(modelFactory.createTasks);
            ajax.getWorkers(modelFactory.createWorkers);
        },
        powerOnWorker = function(data){
            var connectors = modelFactory.getConnectors(),
                weight = modelFactory.getConnectorsWeight(),
                connector, workers;
                
                workers = modelFactory.getWorkers();
                workers[data.name].active = true;

            if( data !== "failed" || data !== undefined ){
                for( connector in connectors ){
                    if( connectors.hasOwnProperty(connector) ){
                        if( connectors[connector].worker.fullName === data.name ){
                            weight += connectors[connector].numTasks;
                            modelFactory.setConnectorsWeight(weight);
                            connectors[connector].active = true;
                        }
                    }
                }
                draw();
            }
        };

    CMA.SystemDisplay.on("Redraw", redraw);
    CMA.SystemDisplay.on("Refresh", refresh);

    return {
        shutdownWorker: function(data){
            var connectors = modelFactory.getConnectors(),
                weight = modelFactory.getConnectorsWeight(),
                connector, workers;

            if( data !== "failed" || data !== undefined ){
                for( connector in connectors ){
                    if( connectors.hasOwnProperty(connector) ){
                        if( connectors[connector].worker.fullName === data.name ){
                            weight -= connectors[connector].numTasks;
                            modelFactory.setConnectorsWeight(weight);
                            connectors[connector].active = false;
                        }
                    }
                }
                workers = modelFactory.getWorkers();
                workers[data.name].active = false;
                draw();
            }
        },
        powerOnWorker: powerOnWorker,
        redraw: redraw,
        draw: draw,
        handleTaskHover: function(task){
            if( !expandedTask ){
                showTaskConnectors(task);
                expandTask(task, true);
            }
        },
        handleWorkerHover: function(worker){
            if( !expandedWorker ){
                showWorkerConnectors(worker);
                expandWorker(worker, true);
            }
        },
        unexpandEntity: function(){
            if( expandedTask ){
                expandTask(expandedTask, false);   
                canvasElement.css("cursor", "auto");
            } else if( expandedWorker ){
                expandWorker(expandedWorker, false);   
                canvasElement.css("cursor", "auto");
            }
        }
    };
};

CMA.SystemDisplay.EventHandler = function(canvasElement, viewer, modelFactory){
    var events = {},
        handlers = {},
        clickedEntity = null,
        yOffset = $('#header').css("height").split("px")[0],
        xOffset = $('#dummy').css("width").split("px")[0],
        ajax = CMA.Core.ajax,
        powerImg = new Image();

    var getEntity = function(xPos, yPos){
        var xMousePos = xPos - xOffset,
            yMousePos = yPos - yOffset,
            tasks = modelFactory.getTasks(),
            workers = modelFactory.getWorkers(),
            item, task, worker;

        for( item in tasks ){
            if( tasks.hasOwnProperty(item) ){
                task = tasks[item];
                if( xMousePos < (task.x + task.width) && xMousePos > task.x ){
                    if( yMousePos < (task.y + task.height) && yMousePos > task.y ){
                        return task;
                    }
                }
            }
        }
        for( item in workers ){
            if( workers.hasOwnProperty(item) ){
                worker = workers[item];
                if( xMousePos < (worker.x + worker.width) && xMousePos > worker.x ){
                    if( yMousePos < (worker.y + worker.height) && yMousePos > worker.y ){
                        return worker;
                    }
                }
            }
        }
    };

    handlers.handleClick = function(e){
        var entity = getEntity(e.pageX, e.pageY);
        if( entity !== undefined && entity.objectType === "Task" ){
            window.location = ajax.getUrls().task_url + entity.fullName + "/";
        }     
    };
 
    handlers.handleHover = function(e){
        var entity = getEntity(e.pageX, e.pageY);
        if( entity !== undefined && entity.objectType === "Task" ){
            viewer.handleTaskHover(entity);
        } else if( entity !== undefined && entity.objectType === "Worker" ){
            viewer.handleWorkerHover(entity);
        } else {
            viewer.unexpandEntity();
        }
    };
    
    var menuSetup = function(){
        if( CMA.Core.USE_MODE === "static" ){
            
            canvasElement.bind("contextmenu", function(e){
                var entity = getEntity(e.pageX, e.pageY);
                clickedEntity = entity;

                if( entity !== undefined  && entity.objectType === "Worker" ){
                    $('#taskMenu').hide();
                    $('#powerWorker').text(entity.active ? "Power Off" : "Power On");
                    $('#workerMenu').css({
                        top: (e.pageY - yOffset) + 'px',
                        left: (e.pageX - xOffset - $('#workerMenu').width()) + 'px'
                    }).show();
                }
                return false;
            });

            $('#powerWorker').click(function (){
                if(  clickedEntity !== undefined  && clickedEntity.objectType === "Worker" ){
                    if( $(this).text() === "Power Off" ){
                        ajax.postWorkerPower(clickedEntity.id, {"power_state": "off"}, viewer.shutdownWorker);
                        $('#powerWorkerImg').children('img').attr("src", ajax.getUrls().media_url + 'images/power-on.png');
                    } else {
                        ajax.postWorkerPower(clickedEntity.id, {"power_state": "on"}, viewer.powerOnWorker);
                        $('#powerWorkerImg').children('img').attr("src", ajax.getUrls().media_url + 'images/power-off.png');
                    }
                    clickedEntity = false;
                }
            });
        } else {
            canvasElement.bind("contextmenu", function(e){
                return false;
            });
        }
        
        if( CMA.Core.USE_MODE === "static" ){
            
            canvasElement.bind("contextmenu", function(e){
                var entity = getEntity(e.pageX, e.pageY);
                clickedEntity = entity;
                
                if( entity !== undefined  && entity.objectType === "Task" ){
                    $('#workerMenu').hide();
                    $('#taskMenu').css({
                        top: (e.pageY - yOffset) + 'px',
                        left: (e.pageX - xOffset) + 'px'
                    }).show();
                }
                return false;
            });

            $('#dispatchTask').click(function (){
                if(  clickedEntity !== undefined  && clickedEntity.objectType === "Task" ){
                    //CMA.Core.postShutdownWorker(clickedEntity.fullName, viewer.shutdownWorker);
                    console.log("task dispatch");
                    clickedEntity = false;
                }
            });
        } else {
            canvasElement.bind("contextmenu", function(e){
                return false;
            });
        }
        
        $(document).ready(function() {
            $('#workerMenu').click(function() {
                $('#workerMenu').hide();
            });
            $('#taskMenu').click(function() {
                $('#taskMenu').hide();
            });
            $(document).click(function() {
                $('#workerMenu').hide();
                $('#taskMenu').hide();
            });
        });
    };

    handlers.resizer = (function() {
        var canvasElement = $('#systemCanvas')[0],
            wind = $(window),
            dummyWidth = $('#dummy').css("width").split("px")[0];

            resize = function() {
                canvasElement.width = wind.width() - dummyWidth;
                CMA.SystemDisplay.fire("Redraw");
            };

        return resize;
    }());

    //canvasElement.click(handlers.handleClick);
    canvasElement.mousemove(handlers.handleHover);
    $(window).resize(handlers.resizer);

};

CMA.SystemDisplay.Renderer = function(canvas, modelFactory){
    var context = canvas.getContext("2d"),
        height = modelFactory.getCanvasHeight() + 60,
        drawShapes = CMA.SystemDisplay.DrawShapes(context);

    context.lineJoin = "bevel";
    canvas.height = height;
   
    return {
        drawTask: function(task){
            drawShapes.roundedRect(task.x, task.y, task.width, task.height, task.getFill());
            context.textBaseline = "middle";
            context.textAlign = "start";
            context.font = "12px sans-serif";
            context.fillStyle = "black";
            context.fillText(task.displayName, task.x + 5, task.y + 12);
            context.font = "11px sans-serif";
            context.fillStyle = "black";
            context.fillText("Pending: " + task.pending, task.x + 5, task.y + 12 + 15);
        },
        drawWorker: function(worker){
            var fill = worker.active ? '#FFC028' : '#CCC';
            drawShapes.roundedRect(worker.x, worker.y, worker.width, worker.height, fill);
            context.textBaseline = "middle";
            context.textAlign = "start";
            context.font = "12px sans-serif";
            context.fillStyle = "black";
            context.fillText(worker.displayName, worker.x + 5, worker.y + 12);
            context.font = "11px sans-serif";
            context.fillStyle = "black";
            context.fillText("Worker Processes: " + worker.processes, worker.x + 5, worker.y + 12 + 15);
        },
        drawConnector: function(connector, weight){
            if( connector.active ){
                connector.x2 = connector.worker.xCenter - (connector.worker.width / 2);
                context.lineWidth = weight;
                context.beginPath();
                context.moveTo(connector.x1, connector.y1);
                context.lineTo(connector.x2, connector.y2);
                context.closePath();
                context.strokeStyle = connector.getFill();
                context.stroke();
            }
        },
        highlightConnector: function(connector, weight){
            if( connector.active ){
                context.lineCap = "butt";
                context.lineWidth = weight;
                context.beginPath();
                context.moveTo(connector.x1, connector.y1);
                context.lineTo(connector.x2, connector.y2);
                context.closePath();
                context.strokeStyle = "red";
                context.stroke();
                context.textBaseline = "middle";
                context.textAlign = "left";
                context.font = "15px sans-serif";
                context.fillStyle = "black";
                context.fillText(connector.numTasks, connector.getXCenter()+10, connector.getYCenter()+5);
            }
        },
        dimConnector: function(connector){
            context.lineCap = "butt";
            context.lineWidth = 3;
            context.beginPath();
            context.moveTo(connector.x1, connector.y1);
            context.lineTo(connector.x2, connector.y2);
            context.closePath();
            context.strokeStyle = '#FFF';
            context.stroke();
            context.fillStyle = '#FFF';
            context.fill();
            context.lineCap = "butt";
            context.lineWidth = 1;
            context.beginPath();
            context.moveTo(connector.x1, connector.y1);
            context.lineTo(connector.x2, connector.y2);
            context.closePath();
            context.strokeStyle = '#CCC';
            context.stroke();
        },
        clearCanvas: function(){
            canvas.width = $(window).width() - $('#dummy').css("width").split("px")[0];
            canvas.height = height;
            context.clearRect(0, 0, canvas.width, canvas.height);
        }
    };
};

CMA.SystemDisplay.DrawShapes = function(context){
    
    var roundedRect = function(x, y, width, height, fill, radius, stroke) {
        stroke = (stroke === undefined ) ? true : stroke;
        radius = radius || 5;
        
        context.beginPath();
        context.moveTo(x + radius, y);
        context.lineTo(x + width - radius, y);
        context.quadraticCurveTo(x + width, y, x + width, y + radius);
        context.lineTo(x + width, y + height - radius);
        context.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
        context.lineTo(x + radius, y + height);
        context.quadraticCurveTo(x, y + height, x, y + height - radius);
        context.lineTo(x, y + radius);
        context.quadraticCurveTo(x, y, x + radius, y);
        context.closePath();
        if( stroke ){
            context.lineWidth = 3;
            context.strokeStyle = '#A6790D';
            context.stroke();
        }
        if( fill ){
            context.fillStyle = fill;
            context.fill();
        }
    };

    return {
        roundedRect: roundedRect
    };
};

CMA.SystemDisplay.Task = function(y, name){

    var x = 100,
        width = 200,
        height = 40,
        xCenter = (width / 2) + x,
        yCenter = (height / 2) + y,
        fill = '#FFC028',
        displayName = (name.length > 30) ? ("..." + name.substring(name.length-29, name.length)) : name,

        getFill = function(){
            return fill;
        };

    return {
        x: x,
        y: y,
        width: width,
        height: height,
        fullName: name,
        displayName: displayName,
        xCenter: xCenter,
        yCenter: yCenter,
        pending: 0,
        getFill: getFill,
        objectType: "Task"
    };
};

CMA.SystemDisplay.Worker = function(y, canvasWidth, id, name, active){

    var width = 200,
        height = 40,
        x = canvasWidth - width - 100,
        activeFill = '#FFC028',
        inactiveFill = '#CCC',
        fullName = name,
        xCenter = (width / 2) + x,
        yCenter = (height / 2) + y,
        processes = 0,
        displayName = (name.length > 30) ? ("..." + name.substring(name.length-29, name.length)) : name,

        getFill = function(){
            return active ? activeFill : inactiveFill;
        };
    
    return {
        id: id,
        x: x,
        y: y,
        width: width,
        height: height,
        fullName: name,
        displayName: displayName,
        xCenter: xCenter,
        yCenter: yCenter,
        active: active,
        processes: processes,
        getFill: getFill,
        objectType: "Worker"
    };
    
};

CMA.SystemDisplay.Connector = function(task, worker, numTasks){
    var x1 = task.xCenter + (task.width / 2),
        y1 = task.yCenter,
        x2 = worker.xCenter - (worker.width / 2),
        y2 = worker.yCenter,
        active = true,

        getXCenter = function(){ 
            return ((worker.xCenter - (worker.width / 2)) - ((((worker.xCenter - (worker.width / 2)) - (task.xCenter + (task.width / 2))) / 2)));
        },
        getYCenter = function(){
            return (worker.yCenter - ((worker.yCenter - task.yCenter) / 2));
        },
        
        getFill = function(){
            return '#CCC';
        };
    
    return{
        task: task,
        worker: worker,
        x1: x1,
        y1: y1,
        x2: x2,
        y2: y2,
        active: active,
        numTasks: numTasks,
        getXCenter: getXCenter,
        getYCenter: getYCenter,
        getFill: getFill
    };
};

var eventuality = function(that){
    var registry = {};

    that.fire = function(event){
        var array,
            func,
            handler,
            i,
            type = typeof event === 'string' ? event : event.type;

        if(registry.hasOwnProperty(type)){
            array = registry[type];
            for(i=0; i < array.length; i += 1){
                handler = array[i];
                func = handler.method;
                if( typeof func === 'string' ){
                    func = this[func];
                }

                func.apply(this, handler.parameters || [event]);
            }
        }
        return this;
    };

    that.on = function(type, method, parameters){
        
        var handler = {
            method: method,
            parameters: parameters
        };
        if(registry.hasOwnProperty(type)){
            registry[type].push(handler);
        } else {
            registry[type] = [handler];
        }
        return this;
    };
    return that;
};

$(document).ready(function() {
    
    eventuality(CMA.SystemDisplay);
    systemDisplay = CMA.SystemDisplay.Controller();
     
});
