var CMACore = (typeof CMACore == "undefined" || !CMACore) ? {} : CMACore;

function Task(y, name){
    this.x = 200;
    this.y = y;
    this.width = 200;
    this.height = 40;
    this.fill = '#FFC028';
    this.fullName = name;
    this.xCenter = (this.width / 2) + this.x;
    this.yCenter = (this.height / 2) + y;
    
    if( name.length > 25 ){
        this.displayName = name.substring(0, 22) + "...";
    } else {
        this.displayName = name;
    }

    this.getFill = function(){
        return this.fill;
    }
}

function Worker(y, name, active){
    this.x = 1000;
    this.y = y;
    this.width = 200;
    this.height = 40;
    this.activeFill = '#FFC028';
    this.inactiveFill = '#CCC';
    this.fullName = name;
    this.xCenter = (this.width / 2) + this.x;
    this.yCenter = (this.height / 2) + y;
    this.active = active;
    
    if( name.length > 25 ){
        this.displayName = name.substring(0, 22) + "...";
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

function Connector(task, worker, text){
    this.task = task;
    this.worker = worker;
    this.x1 = task.xCenter + (task.width / 2);
    this.y1 = task.yCenter;
    this.x2 = worker.xCenter - (worker.width / 2);
    this.y2 = worker.yCenter;
    this.text = text;
    this.xCenter = (this.x2 - ((this.x2 - this.x1) / 2));
    this.yCenter = (this.y2 - ((this.y2 - this.y1) / 2));
    
    this.getFill = function(){
        return "red";
    }
}

function SystemViewer(){
    var tasks = [];
    var workers = [];
    var connectors = [];
    var expandedTask = false;
    var expandedWorker = false;
    var tasksSet = false;
    var workersSet = false;
    var systemRenderer; 

    this.init = function(){
        $('#systemCanvas').mousemove(handleHover);
        $('#systemCanvas').click(handleClick);
        this.refresh();
    }

    this.refresh = function(){
        CMACore.getTasks(this.createTasks);
        CMACore.getWorkers(this.createWorkers);
    }

    this.createTasks = function(data){
        var y = 20;
        for( item in data ){
            tasks.push(new Task(y, data[item]));
            y += 60;
        }
        tasksSet = true;
        if( workersSet ){
            CMACore.getTasksPerWorker(createConnectors);
        }
    }

    this.createWorkers = function(data){
        var y = 20;
        for ( item in data ){
            workers.push(new Worker(y, data[item], true));
            y += 60;
        }
        workersSet = true;
        if( tasksSet ){
            CMACore.getTasksPerWorker(createConnectors);
        }
    }
    
    function createConnectors(data){
        for( task in tasks ){
            for( worker in workers ){
                var num = data[tasks[task].fullName][workers[worker].fullName];
                if( num ){
                    connectors.push(new Connector(tasks[task], workers[worker], num));
                }
            }
        }
        draw();
    }
    
    function draw(){
        if( workers.length > tasks.length ){
            var height = workers.length * 60 + 20;
        } else {
            var height = tasks.length * 60 + 20;
        }
        systemRenderer = new SystemRenderer(height);
        for( var i = 0; i < connectors.length; i++){
            systemRenderer.drawConnector(connectors[i]);
        }
        for( var i = 0; i < tasks.length; i++){
            systemRenderer.drawEntity(tasks[i]);
        }
        for( var i = 0; i < workers.length; i++){
            systemRenderer.drawEntity(workers[i]);
        }
    }
    
    function handleHover(e){
        var xOffset = 0;
        var yOffset = 115;
        var xMousePos = e.pageX - xOffset;
        var yMousePos = e.pageY - yOffset;
        handleTaskHover(xMousePos, yMousePos);
        handleWorkerHover(xMousePos, yMousePos);
    }

    function handleClick(e){
        var xOffset = 0;
        var yOffset = 115;
        var xMousePos = e.pageX - xOffset;
        var yMousePos = e.pageY - yOffset;
        var entity = getEntity(xMousePos, yMousePos);
        if( entity != undefined ){
            console.log(entity.fullName);
            window.location = CMACore.task_url + entity.fullName + "/";
        }
    }

    function handleTaskHover(xMousePos, yMousePos){
        if( !expandedTask ){
            for( item in tasks ){
                if( xMousePos < (tasks[item].x + tasks[item].width) && xMousePos > tasks[item].x ){
                    if( yMousePos < (tasks[item].y + tasks[item].height) && yMousePos > tasks[item].y ){
                        showTaskConnectors(tasks[item]);
                        expandTask(tasks[item], true);
                        $('#systemCanvas').css("cursor", "pointer");
                        $('#systemCanvas').css("cursor", "hand");
                    }
                }
            }
        } else {
            if( !((xMousePos < (expandedTask.x + expandedTask.width)) && (xMousePos > expandedTask.x)) 
                || !((yMousePos < (expandedTask.y + expandedTask.height)) && (yMousePos > expandedTask.y)) ){
                
                    expandTask(expandedTask, false);
                    $('#systemCanvas').css("cursor", "auto");
            }
        }
    }

    function handleWorkerHover(xMousePos, yMousePos){
        if( !expandedWorker ){
            for( item in workers ){
                if( xMousePos < (workers[item].x + workers[item].width) && xMousePos > workers[item].x ){
                    if( yMousePos < (workers[item].y + workers[item].height) && yMousePos > workers[item].y ){
                        showWorkerConnectors(workers[item]);
                        expandWorker(workers[item], true);
                    }
                }
            }
        } else {
            if( !((xMousePos < (expandedWorker.x + expandedWorker.width)) && (xMousePos > expandedWorker.x)) 
                || !((yMousePos < (expandedWorker.y + expandedWorker.height)) && (yMousePos > expandedWorker.y)) ){
                expandWorker(expandedWorker, false);
            }
        }
    }

    function getEntity(xMousePos, yMousePos){
        for( item in tasks ){
            if( xMousePos < (tasks[item].x + tasks[item].width) && xMousePos > tasks[item].x ){
                if( yMousePos < (tasks[item].y + tasks[item].height) && yMousePos > tasks[item].y ){
                    return tasks[item];
                }
            }
        }
        for( item in workers ){
            if( xMousePos < (workers[item].x + workers[item].width) && xMousePos > workers[item].x ){
                if( yMousePos < (workers[item].y + workers[item].height) && yMousePos > workers[item].y ){
                    return workers[item];
                }
            }
        }
    }

    function expandTask(task, expand){
        if( expand ){
            if( task.fullName != task.displayName ){
                var newTask = new Task(task.y, task.fullName);
                newTask.width = task.fullName.length * 8;
                newTask.x = task.x - ((newTask.width - task.width) / 2);
                newTask.displayName = task.fullName;
                systemRenderer.drawEntity(newTask);
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
                newWorker.width = worker.fullName.length * 8;
                newWorker.x = worker.x - ((newWorker.width - worker.width) / 2);
                newWorker.displayName = worker.fullName;
                systemRenderer.drawEntity(newWorker);
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
                systemRenderer.highlightConnector(connectors[connector]);
            } else {
                //systemRenderer.dimConnector(connectors[connector]);
            }
        }
    }
    
    function showWorkerConnectors(worker){
        for( connector in connectors ){
            if( connectors[connector].worker.fullName == worker.fullName ){
                systemRenderer.highlightConnector(connectors[connector]);
            } else {
                //systemRenderer.dimConnector(connectors[connector]);
            }
        }
    }
}

function SystemRenderer(height){
    var canvas = $('#systemCanvas')[0];
    var context = canvas.getContext("2d");
    canvas.width = $(window).width();
    canvas.height = height;
    var drawShapes = new DrawShapes(context);
   
    this.drawEntity = function(shape){
        context.lineWidth = 1;
        drawShapes.roundedRect(shape.x, shape.y, shape.width, shape.height, shape.getFill());
        context.textBaseline = "middle";
        context.textAlign = "center";
        context.font = "15px sans-serif";
        context.fillStyle = "black";
        context.fillText(shape.displayName, shape.xCenter, shape.yCenter);
    }
    
    this.drawConnector = function(connector){
        context.moveTo(connector.x1, connector.y1);
        context.lineTo(connector.x2, connector.y2);
        context.strokeStyle = connector.getFill();
        context.stroke();
    }

    this.highlightConnector = function(connector){
        context.lineCap = "butt";
        context.lineWidth = 6;
        context.moveTo(connector.x1, connector.y1);
        context.lineTo(connector.x2, connector.y2);
        context.strokeStyle = connector.getFill();
        context.stroke();
        context.textBaseline = "middle";
        context.textAlign = "left";
        context.font = "15px sans-serif";
        context.fillStyle = "black";
        context.fillText(connector.text, connector.xCenter+10, connector.yCenter+1);
    }

    this.dimConnector = function(connector){
        context.lineCap = "butt";
        context.lineWidth = 6;
        context.moveTo(connector.x1, connector.y1);
        context.lineTo(connector.x2, connector.y2);
        context.strokeStyle = '#FFF';
        context.stroke();
        context.fillStyle = '#FFF';
        context.fill();
    }
    
    this.clearCanvas = function(){
        canvas.width = $(window).width();
        canvas.height = $(window).height();
        context.clearRect(0, 0, canvas.width, canvas.height);
    }

}

function DrawShapes(context){
    
    this.roundedRect = function(x, y, width, height, fill, radius, stroke) {
        if( typeof stroke == "undefined" ){
            stroke = false;
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
            context.stroke();
        }
        if( fill ){
            context.fillStyle = fill;
            context.fill();
        }
    }
}
