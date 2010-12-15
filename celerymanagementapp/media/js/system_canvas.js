var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

var systemViewer;

$(document).ready(function() {
    
    $('#systemCanvas')[0].width = $(window).width() - $('#dummy').css("width").split("px")[0];
    systemViewer = new SystemViewer();
    systemViewer.init();
     
    $(window).resize(function(e) {
        $('#systemCanvas')[0].width = $(window).width() - $('#dummy').css("width").split("px")[0];
        systemViewer.redraw();
    });
    
});

function refresh(){
    systemViewer.refresh();
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
}

function Task(y, name){
    this.x = 100;
    this.y = y;
    this.width = 200;
    this.height = 40;
    this.fill = '#FFC028';
    this.fullName = name;
    this.xCenter = (this.width / 2) + this.x;
    this.yCenter = (this.height / 2) + y;
    this.pending = 0;
    
    if( name.length > 30 ){
        this.displayName = "..." +  name.substring(name.length-29, name.length);
    } else {
        this.displayName = name;
    }

    this.getFill = function(){
        return this.fill;
    }
}

function Worker(y, name, active){
    this.width = 200;
    this.height = 40;
    this.x = $('#systemCanvas')[0].width - this.width - 100;
    this.y = y;
    this.activeFill = '#FFC028';
    this.inactiveFill = '#CCC';
    this.fullName = name;
    this.xCenter = (this.width / 2) + this.x;
    this.yCenter = (this.height / 2) + y;
    this.active = active;
    this.processes = 0;
    
    if( name.length > 30 ){
        this.displayName = name.substring(0, 27) + "...";
    } else {
        this.displayName = name;
    }

    this.getFill = function(){
        if( this.active ){
            return this.activeFill;
        } else {
            return this.inactiveFill;
        }
    }
}

function Connector(task, worker, numTasks){
    this.task = task;
    this.worker = worker;
    this.x1 = task.xCenter + (task.width / 2);
    this.y1 = task.yCenter;
    this.x2 = worker.xCenter - (worker.width / 2);
    this.y2 = worker.yCenter;
    this.numTasks = numTasks;
    this.xCenter = (this.x2 - ((this.x2 - this.x1) / 2));
    this.yCenter = (this.y2 - ((this.y2 - this.y1) / 2));
    
    this.getFill = function(){
        return "#CCC";
    }
}

function SystemViewer(){
    var tasks = {};
    var workers = {};
    var connectors = [];
    var expandedTask = false;
    var expandedWorker = false;
    var tasksSet = false;
    var workersSet = false;
    var canvasHeight = 0;
    var systemRenderer;
    var systemEventHandler;
    var yOffset = $('#header').css("height").split("px")[0];
    var xOffset = $('#dummy').css("width").split("px")[0];
    var clickedEntity = false;
    var connectorWeight = 0;

    function connectorWeightingFunction(size){
        return (size / connectorWeight + 0.30) * 4;
    }

    $('#systemCanvas').bind("contextmenu", function(e){
        var entity = getEntity(e.pageX, e.pageY);
        clickedEntity = entity;

        if( typeof entity != "undefined"  && entity.constructor.name == "Worker" ){
            $('#workerMenu').css({
                top: (entity.yCenter) + 'px',
                left: (entity.xCenter - 125) + 'px'
            }).show();
        }
        return false;
    });

    $('#deactivateWorker').click(function (){
        if( typeof clickedEntity != "undefined"  && clickedEntity.constructor.name == "Worker" ){
            CMACore.postShutdownWorker(clickedEntity.fullName, shutdownWorker);
            console.log("deactivate clicked");
            clickedEntity = false;
        }
    });

    function shutdownWorker(data){
        if( data != "failed" || typeof data != "undefined" ){
            for( connector in connectors ){
                if( connectors[connector].worker.fullName == data ){
                    connectorWeight -= connectors[connector].numTasks;
                    delete connectors[connector];
                }
            }
            delete workers[data];
            draw();
        }
    }

    this.init = function(){
        systemEventHandler = new SystemEventHandler();
        $('#systemCanvas').mousemove(handleHover);
        $('#systemCanvas').click(handleClick);
        this.refresh();
    }

    this.refresh = function(){
        CMACore.getTasks(this.createTasks);
        CMACore.getWorkers(this.createWorkers);
    }

    this.createTasks = function(data){
        tasks = {};
        var y = 40;
        for( item in data ){
            tasks[data[item]] = new Task(y, data[item]);
            y += 60;
        }
        if( y > canvasHeight ){
            canvasHeight = y;
        }
        tasksSet = true;
        if( workersSet ){
            CMACore.getTasksPerWorker(createConnectors);
        }
    }

    this.createWorkers = function(data){
        workers = {};
        var y = 40;
        for ( item in data ){
            workers[data[item]] = new Worker(y, data[item], true);
            y += 60;
        }
        if( y > canvasHeight ){
            canvasHeight = y;
        }
        workersSet = true;
        if( tasksSet ){
            CMACore.getTasksPerWorker(createConnectors);
        }
    }
    
    function createConnectors(data){
        connectors = [];
        connectorWeight = 0;
        for( task in tasks ){
            for( worker in workers ){
                var num = data[task][worker];
                if( num ){
                    connectors.push(new Connector(tasks[task], workers[worker], num));
                    connectorWeight += num;
                }
            }
        }
        CMACore.getPendingTasks(setPendingTasks);
        CMACore.getWorkerProcesses(setWorkerProcesses);
    }
    
    function setPendingTasks(data){
        for( item in data ){
            tasks[item].pending = data[item];
        }
        draw();
    }

    function setWorkerProcesses(data){
        for( item in data ){
            workers[item].processes = data[item];
        }
        draw();
    }
    
    this.redraw = function(){
        $('#systemCanvas')[0].width = $(window).width() - $('#dummy').css("width").split("px")[0];
        if( $(window).width() > $('#container').css("min-width").split("px")[0] ){
            for( wrkr in workers ){
                worker = workers[wrkr];
                worker.x = $('#systemCanvas')[0].width - worker.width - 100;
                worker.xCenter = (worker.width / 2) + worker.x;
            }
        }
        draw();
    }

    function draw(){
        systemRenderer = new SystemRenderer(canvasHeight + 60);
        $('#systemCanvas')[0].width = $(window).width() - $('#dummy').css("width").split("px")[0];
        console.log(connectorWeight);
        for( connector in connectors ){
            systemRenderer.drawConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
        }
        for( task in tasks ){
            systemRenderer.drawTask(tasks[task]);
        }
        for( worker in workers ){
            systemRenderer.drawWorker(workers[worker]);
        }
    }
    
    function handleClick(e){
        var entity = getEntity(e.pageX, e.pageY);
        if( typeof entity != "undefined" && entity.constructor.name == "Task" ){
            window.location = CMACore.task_url + entity.fullName + "/";
        } else if( typeof entity != "undefined" && entity.constructor.name == "Worker" ){
            window.location = CMACore.worker_url + entity.fullName + "/";
        }
    }
 
    function handleHover(e){
        var entity = getEntity(e.pageX, e.pageY);
        if( typeof entity != "undefined" && entity.constructor.name == "Task" ){
            handleTaskHover(entity);
        } else if( typeof entity != "undefined" && entity.constructor.name == "Worker" ){
            handleWorkerHover(entity);
        } else {
            unexpandEntity();
        }
    }

    function handleTaskHover(task){
        if( !expandedTask ){
            showTaskConnectors(task);
            expandTask(task, true);
            $('#systemCanvas').css("cursor", "pointer");
            $('#systemCanvas').css("cursor", "hand");
        }
    }

    function handleWorkerHover(worker){
        if( !expandedWorker ){
            showWorkerConnectors(worker);
            expandWorker(worker, true);
            $('#systemCanvas').css("cursor", "pointer");
            $('#systemCanvas').css("cursor", "hand");
        }
    }

    function unexpandEntity(){
        if( expandedTask ){
            expandTask(expandedTask, false);   
            $('#systemCanvas').css("cursor", "auto");
        } else if( expandedWorker ){
            expandWorker(expandedWorker, false);   
            $('#systemCanvas').css("cursor", "auto");
        }
    }

    function getEntity(xPos, yPos){
        var xMousePos = xPos - xOffset;
        var yMousePos = yPos - yOffset;
        for( task in tasks ){
            if( xMousePos < (tasks[task].x + tasks[task].width) && xMousePos > tasks[task].x ){
                if( yMousePos < (tasks[task].y + tasks[task].height) && yMousePos > tasks[task].y ){
                    return tasks[task];
                }
            }
        }
        for( worker in workers ){
            if( xMousePos < (workers[worker].x + workers[worker].width) && xMousePos > workers[worker].x ){
                if( yMousePos < (workers[worker].y + workers[worker].height) && yMousePos > workers[worker].y ){
                    return workers[worker];
                }
            }
        }
    }

    function expandTask(task, expand){
        if( expand ){
            if( task.fullName != task.displayName ){
                var newTask = new Task(task.y, task.fullName);
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
            var newTask = new Task(task.y, task.displayName);
            systemRenderer.clearCanvas();
            draw();
            expandedTask = false;
        }
    }
    
    function expandWorker(worker, expand){
        if( expand ){
            if( worker.fullName != worker.displayName ){
                var newWorker = new Worker(worker.y, worker.fullName, worker.active);
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
            var newWorker = new Worker(worker.y, worker.displayName, worker.active);
            systemRenderer.clearCanvas();
            draw();
            expandedWorker = false;
        }
    }

    function showTaskConnectors(task){
        for( connector in connectors ){
            if( connectors[connector].task.fullName == task.fullName ){
                systemRenderer.highlightConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
            }
        }
    }
    
    function showWorkerConnectors(worker){
        for( connector in connectors ){
            if( connectors[connector].worker.fullName == worker.fullName ){
                systemRenderer.highlightConnector(connectors[connector], connectorWeightingFunction(connectors[connector].numTasks));
            }
        }
    }
}

function SystemEventHandler(){
    $(document).ready(function() {
        $('#workerMenu').click(function() {
            $('#workerMenu').hide();
        });
        $(document).click(function() {
            $('#workerMenu').hide();
        });
    });
}

function SystemRenderer(height){
    var canvas = $('#systemCanvas')[0];
    var context = canvas.getContext("2d");
    canvas.height = height;
    context.lineJoin = "bevel";
    var drawShapes = new DrawShapes(context);
   
    this.drawTask = function(task){
        drawShapes.roundedRect(task.x, task.y, task.width, task.height, task.getFill());
        context.textBaseline = "middle";
        context.textAlign = "start";
        context.font = "13px sans-serif";
        context.fillStyle = "black";
        context.fillText(task.displayName, task.x + 5, task.y + 12);
        context.font = "11px sans-serif";
        context.fillStyle = "black";
        context.fillText("Pending: " + task.pending, task.x + 5, task.y + 12 + 15);
    }
    
    this.drawWorker = function(worker){
        drawShapes.roundedRect(worker.x, worker.y, worker.width, worker.height, worker.getFill());
        context.textBaseline = "middle";
        context.textAlign = "start";
        context.font = "13px sans-serif";
        context.fillStyle = "black";
        context.fillText(worker.displayName, worker.x + 5, worker.y + 12);
        context.font = "11px sans-serif";
        context.fillStyle = "black";
        context.fillText("Worker Processes: " + worker.processes, worker.x + 5, worker.y + 12 + 15);
    }
    
    this.drawConnector = function(connector, weight){
        connector.x2 = connector.worker.xCenter - (connector.worker.width / 2);
        context.lineWidth = weight;
        context.beginPath();
        context.moveTo(connector.x1, connector.y1);
        context.lineTo(connector.x2, connector.y2);
        context.closePath();
        context.strokeStyle = connector.getFill();
        context.stroke();
    }

    this.highlightConnector = function(connector, weight){
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
    }

    this.dimConnector = function(connector){
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
    }
    
    this.clearCanvas = function(){
        $('#systemCanvas')[0].width = $(window).width() - $('#dummy').css("width").split("px")[0];
        canvas.height = height;
        context.clearRect(0, 0, canvas.width, canvas.height);
    }

}

function DrawShapes(context){
    
    this.roundedRect = function(x, y, width, height, fill, radius, stroke) {
        if( typeof stroke == "undefined" ){
            stroke = true;
        }
        if( typeof radius == "undefined" ){
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
}
