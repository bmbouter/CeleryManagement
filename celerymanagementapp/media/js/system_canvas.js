var CMA = ( CMA === undefined || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

CMA.SystemDisplay = {};

$(document).ready(function() {
    
    eventuality(CMA.SystemDisplay);
    systemDisplay = CMA.SystemDisplay.Controller();
     
    $(window).resize(function(e) {
        $('#systemCanvas')[0].width = $(window).width() - $('#dummy').css("width").split("px")[0];
        CMA.SystemDisplay.fire("Redraw");
    });
    
});

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
        canvas = $('#systemCanvas')[0];
        canvas.width = $(window).width() - $('#dummy').css("width").split("px")[0];

    var modelFactory = CMA.SystemDisplay.ModelFactory(canvas),
        viewer = CMA.SystemDisplay.Viewer(modelFactory, canvas, canvasElement),
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
            
        createWorkers = function(data){
            var y = 40,
                i = 0,
                length = data.length;

            workers = {};
            
            for (i=0; i < length; i += 1){
                workers[data[i]] = CMA.SystemDisplay.Worker(y, canvas.width, data[i], true);
                y += 60;
            }

            if( y > canvasHeight ){
                canvasHeight = y;
            }

            workersSet = true;
            if( tasksSet ){
                CMA.Core.getTasksPerWorker(createConnectors);
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

            tasksSet = true;
            if( workersSet ){
                CMA.Core.getTasksPerWorker(createConnectors);
            }
        },

        createConnectors = function(data){
            var num;

            connectors = [];
            connectorWeight = 0;

            for( task in tasks ){
                for( worker in workers ){
                    if( workers.hasOwnProperty(worker) && tasks.hasOwnProperty(task) ){
                        num = data[task][worker];
                        if( num ){
                            connectors.push(CMA.SystemDisplay.Connector(tasks[task], workers[worker], num));
                            connectorWeight += num;
                        }
                    }
                }
            }

            CMA.Core.getPendingTasks(setPendingTasks);
            CMA.Core.getWorkerProcesses(setWorkerProcesses);
        },

        setPendingTasks = function(data){
            for( item in data ){
                if( data.hasOwnProperty(item) ){
                    tasks[item].pending = data[item];
                }
            }
            CMA.SystemDisplay.fire("Redraw");
        },

        setWorkerProcesses = function(data){
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
    CMA.Core.getTasks(modelFactory.createTasks);
    CMA.Core.getWorkers(modelFactory.createWorkers);
    
    var expandedTask = false,
        expandedWorker = false,
        canvasHeight = 0,

        connectorWeightingFunction = function(size){
            return (size / modelFactory.getConnectorsWeight() + 0.35) * 4;
        },

        redraw = function(){
            canvas.width = $(window).width() - $('#dummy').css("width").split("px")[0];
            var workers;
            if( $(window).width() > $('#container').css("min-width").split("px")[0] ){
                workers = modelFactory.getWorkers();
                for( wrkr in workers ){
                    worker = workers[wrkr];
                    worker.x = canvas.width - worker.width - 100;
                    worker.xCenter = (worker.width / 2) + worker.x;
                }
            }
            draw();
        },

        draw = function(){
            systemRenderer = CMA.SystemDisplay.Renderer(canvas, modelFactory.getCanvasHeight() + 60);
            canvas.width = $(window).width() - $('#dummy').css("width").split("px")[0];
            var connectors = modelFactory.getConnectors();
            var tasks = modelFactory.getTasks();
            var workers = modelFactory.getWorkers();
            for( connector in connectors ){
                systemRenderer.drawConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
            }
            for( task in tasks ){
                systemRenderer.drawTask(tasks[task]);
            }
            for( worker in workers ){
                systemRenderer.drawWorker(workers[worker]);
            }
        },
    
        showTaskConnectors = function(task){
            var connectors = modelFactory.getConnectors();
            for( connector in connectors ){
                if( connectors[connector].task.fullName === task.fullName ){
                    systemRenderer.highlightConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
                }
            }
        },

        showWorkerConnectors = function(worker){
            var connectors = modelFactory.getConnectors();
            for( connector in connectors ){
                if( connectors[connector].worker.fullName === worker.fullName ){
                    systemRenderer.highlightConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
                }
            }
        },
        
        expandTask = function(task, expand){
            if( expand ){
                if( task.fullName !== task.displayName ){
                    var newTask = CMA.SystemDisplay.Task(task.y, task.fullName);
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
                var newTask = CMA.SystemDisplay.Task(task.y, task.displayName);
                systemRenderer.clearCanvas();
                draw();
                expandedTask = false;
            }
        },

        expandWorker = function(worker, expand){
            if( expand ){
                if( worker.fullName !== worker.displayName ){
                    var newWorker = CMA.SystemDisplay.Worker(worker.y, canvas.width, worker.fullName, worker.active);
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
                var newWorker = CMA.SystemDisplay.Worker(worker.y, canvas.width, worker.displayName, worker.active);
                systemRenderer.clearCanvas();
                draw();
                expandedWorker = false;
            }
        },

        refresh = function(){
            CMA.Core.getTasks(modelFactory.createTasks);
            CMA.Core.getWorkers(modelFactory.createWorkers);
        };

    CMA.SystemDisplay.on("Redraw", redraw);
    CMA.SystemDisplay.on("Refresh", refresh);

    return {
        shutdownWorker: function(data){
            if( data !== "failed" || data !== undefined ){
                var connectors = modelFactory.getConnectors();
                for( connector in connectors ){
                    if( connectors[connector].worker.fullName === data ){
                        var weight = modelFactory.getConnectorsWeight();
                        weight -= connectors[connector].numTasks;
                        modelFactory.setConnectorsWeight(weight);
                        delete connectors[connector];
                    }
                }
                var workers = modelFactory.getWorkers();
                delete workers[data];
                draw();
            }
        },
        redraw: redraw,
        draw: draw,
        handleTaskHover: function(task){
            if( !expandedTask ){
                showTaskConnectors(task);
                expandTask(task, true);
                canvasElement.css("cursor", "pointer");
                canvasElement.css("cursor", "hand");
            }
        },
        handleWorkerHover: function(worker){
            if( !expandedWorker ){
                showWorkerConnectors(worker);
                expandWorker(worker, true);
                canvasElement.css("cursor", "pointer");
                canvasElement.css("cursor", "hand");
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
    var clickedEntity = null,
        yOffset = $('#header').css("height").split("px")[0],
        xOffset = $('#dummy').css("width").split("px")[0];

    $(document).ready(function() {
        $('#workerMenu').click(function() {
            $('#workerMenu').hide();
        });
        $(document).click(function() {
            $('#workerMenu').hide();
        });
    });

    var getEntity = function(xPos, yPos){
        var xMousePos = xPos - xOffset,
            yMousePos = yPos - yOffset,
            tasks = modelFactory.getTasks(),
            workers = modelFactory.getWorkers();

        for( item in tasks ){
            var task = tasks[item];
            if( xMousePos < (task.x + task.width) && xMousePos > task.x ){
                if( yMousePos < (task.y + task.height) && yMousePos > task.y ){
                    return task;
                }
            }
        }
        for( item in workers ){
            var worker = workers[item];
            if( xMousePos < (worker.x + worker.width) && xMousePos > worker.x ){
                if( yMousePos < (worker.y + worker.height) && yMousePos > worker.y ){
                    return worker;
                }
            }
        }
    }

    function handleClick(e){
        var entity = getEntity(e.pageX, e.pageY);
        if( entity !== undefined && entity.objectType === "Task" ){
            window.location = CMA.Core.task_url + entity.fullName + "/";
        } else if( entity !== undefined && entity.objectType === "Worker" ){
            window.location = CMA.Core.worker_url + entity.fullName + "/";
        }
    }
 
    function handleHover(e){
        var entity = getEntity(e.pageX, e.pageY);
        if( entity !== undefined && entity.objectType === "Task" ){
            viewer.handleTaskHover(entity);
        } else if( entity !== undefined && entity.objectType === "Worker" ){
            viewer.handleWorkerHover(entity);
        } else {
            viewer.unexpandEntity();
        }
    }
    
    if( CMA.Core.USE_MODE === "static" ){
        
        canvasElement.bind("contextmenu", function(e){
            var entity = getEntity(e.pageX, e.pageY);
            clickedEntity = entity;

            if( entity !== undefined  && entity.objectType === "Worker" ){
                $('#workerMenu').css({
                    top: (entity.yCenter) + 'px',
                    left: (entity.xCenter - 125) + 'px'
                }).show();
            }
            return false;
        });

        $('#deactivateWorker').click(function (){
            if(  clickedEntity !== undefined  && clickedEntity.objectType === "Worker" ){
                CMA.Core.postShutdownWorker(clickedEntity.fullName, viewer.shutdownWorker);
                console.log("deactivate clicked");
                clickedEntity = false;
            }
        });
    } else {
        canvasElement.bind("contextmenu", function(e){
            return false;
        });
    }
    
    canvasElement.click(handleClick);
    canvasElement.mousemove(handleHover);

};

CMA.SystemDisplay.Renderer = function(canvas, height){
    var context = canvas.getContext("2d"),
        drawShapes = CMA.SystemDisplay.DrawShapes(context);

    context.lineJoin = "bevel";
    canvas.height = height;
   
    return {
        drawTask: function(task){
            drawShapes.roundedRect(task.x, task.y, task.width, task.height, task.getFill());
            context.textBaseline = "middle";
            context.textAlign = "start";
            context.font = "13px sans-serif";
            context.fillStyle = "black";
            context.fillText(task.displayName, task.x + 5, task.y + 12);
            context.font = "11px sans-serif";
            context.fillStyle = "black";
            context.fillText("Pending: " + task.pending, task.x + 5, task.y + 12 + 15);
        },
        drawWorker: function(worker){
            drawShapes.roundedRect(worker.x, worker.y, worker.width, worker.height, worker.getFill());
            context.textBaseline = "middle";
            context.textAlign = "start";
            context.font = "13px sans-serif";
            context.fillStyle = "black";
            context.fillText(worker.displayName, worker.x + 5, worker.y + 12);
            context.font = "11px sans-serif";
            context.fillStyle = "black";
            context.fillText("Worker Processes: " + worker.processes, worker.x + 5, worker.y + 12 + 15);
        },
        drawConnector: function(connector, weight){
            connector.x2 = connector.worker.xCenter - (connector.worker.width / 2);
            context.lineWidth = weight;
            context.beginPath();
            context.moveTo(connector.x1, connector.y1);
            context.lineTo(connector.x2, connector.y2);
            context.closePath();
            context.strokeStyle = connector.getFill();
            context.stroke();
        },
        highlightConnector: function(connector, weight){
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
            context.fillText(connector.numTasks, connector.xCenter+10, connector.yCenter+1);
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
        if( stroke === undefined ){
            stroke = true;
        }
        if( radius === undefined ){
            radius = 5;
        }
        
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
    }

    return {
        roundedRect: roundedRect
    };
};

CMA.SystemDisplay.Task = function(y, name){

    var x = 100,
        y = y,
        width = 200,
        height = 40,
        xCenter = (width / 2) + x,
        yCenter = (height / 2) + y,
        fill = '#FFC028',

        getFill = function(){
            return fill;
        };

    if( name.length > 30 ){
        var displayName = "..." +  name.substring(name.length-29, name.length);
    } else {
        var displayName = name;
    }

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

CMA.SystemDisplay.Worker = function(y, canvasWidth, name, active){

    var width = 200,
        height = 40,
        x = canvasWidth - width - 100;
        y = y,
        activeFill = '#FFC028',
        inactiveFill = '#CCC',
        fullName = name,
        xCenter = (width / 2) + x,
        yCenter = (height / 2) + y,
        active = active,
        processes = 0,
        getFill = function(){
            if( active ){
                return activeFill;
            } else {
                return inactiveFill;
            }
        };
    
    if( name.length > 30 ){
        var displayName = name.substring(0, 27) + "...";
    } else {
        var displayName = name;
    }

    return {
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
    var task = task,
        worker = worker,
        x1 = task.xCenter + (task.width / 2),
        y1 = task.yCenter,
        x2 = worker.xCenter - (worker.width / 2),
        y2 = worker.yCenter,
        numTasks = numTasks,
        xCenter = (x2 - ((x2 - x1) / 2)),
        yCenter = (y2 - ((y2 - y1) / 2)),
        
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
        numTasks: numTasks,
        xCenter: xCenter,
        yCenter: yCenter,
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
