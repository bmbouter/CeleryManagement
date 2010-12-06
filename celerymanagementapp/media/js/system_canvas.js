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

function SystemRenderer(){
    var tasks = [];
    var workers = [];
    var connectors = [];
    var canvas = $('#systemCanvas')[0];
    var context = canvas.getContext("2d");
    var expandedTask = false;
    var tasksSet = false;
    var workersSet = false;
    
    this.init = function(){
        canvas.width = $(window).width();
        canvas.height = $(window).height();
        canvas.onselectstart = function() { return false; }
        $('#systemCanvas').mousemove(handleTaskHover);
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
        for( item in data ){
            workers.push(new Worker(y, item, true));
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
                    createConnector(tasks[task], workers[worker], num);
                }
            }
        }
        draw();
    }

    function createConnector(task, worker, text){
        var connector = new Connector(task, worker, text);
        connectors.push(connector);
    }

    function draw(){
        for( var i = 0; i < connectors.length; i++){
            drawConnector(connectors[i]);
        }
        for( var i = 0; i < tasks.length; i++){
            drawShape(tasks[i]);
        }
        for( var i = 0; i < workers.length; i++){
            drawShape(workers[i]);
        }
    }
    
    function drawShape(shape){
        context.lineWidth = 1;
        context.fillStyle = shape.getFill();
        context.fillRect(shape.x, shape.y, shape.width, shape.height);
        context.textBaseline = "middle";
        context.textAlign = "center";
        context.font = "15px sans-serif";
        context.fillStyle = "black";
        context.fillText(shape.displayName, shape.xCenter, shape.yCenter);
    }
    
    function drawConnector(connector){
        context.moveTo(connector.x1, connector.y1);
        context.lineTo(connector.x2, connector.y2);
        context.strokeStyle = connector.getFill();
        context.stroke();
    }

    function highlightConnector(connector){
        console.log("highlighting connector");
        context.lineWidth = 4;
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

    function clearCanvas(){
        canvas.width = $(window).width();
        canvas.height = $(window).height();
        context.clearRect(0, 0, canvas.width, canvas.height);
    }

    function handleTaskHover(e){
        var xOffset = 0;
        var yOffset = 115;
        var xMousePos = e.pageX - xOffset;
        var yMousePos = e.pageY - yOffset;
        if( !expandedTask ){
            for( item in tasks ){
                if( xMousePos < (tasks[item].x + tasks[item].width) && xMousePos > tasks[item].x ){
                    if( yMousePos < (tasks[item].y + tasks[item].height) && yMousePos > tasks[item].y ){
                        showConnectors(tasks[item]);
                        expandTask(tasks[item], true);
                    }
                }
            }
        } else {
            if( !((xMousePos < (expandedTask.x + expandedTask.width)) && (xMousePos > expandedTask.x)) 
                || !((yMousePos < (expandedTask.y + expandedTask.height)) && (yMousePos > expandedTask.y)) ){
                
                expandTask(expandedTask, false);
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
                drawShape(newTask);
                expandedTask = newTask;
            }
        } else {
            var newTask = new Task(task.y, task.displayName);
            clearCanvas();
            draw();
            expandedTask = false;
        }
    }

    function showConnectors(task){
        for( connector in connectors ){
            if( connectors[connector].task.fullName == task.fullName ){
                highlightConnector(connectors[connector]);
            }
        }
    }
}
