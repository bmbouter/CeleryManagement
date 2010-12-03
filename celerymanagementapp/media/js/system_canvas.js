var CMASystem = (typeof CMASystem == "undefined" || !CMASystem) ? {} : CMASystem;

CMASystem.Task = function(y, height, text){
    this.x = 200;
    this.y = y;
    this.width = 200;
    this.height = height;
    this.fill = '#FFC028';
    this.fullText = text;
    if( text.length > 25 ){
        this.text = text.substring(0, 22) + "...";
    } else {
        this.text = text;
    }
    this.xCenter = (this.width / 2) + this.x;
    this.yCenter = (height / 2) + y;
}

CMASystem.Worker = function(y, height, text){
    this.x = 1000;
    this.y = y;
    this.width = 200;
    this.height = height;
    this.fill = '#FFC028';
    this.fullText = text;
    if( text.length > 25 ){
        this.text = text.substring(0, 22) + "...";
    } else {
        this.text = text;
    }
    this.xCenter = (this.width / 2) + this.x;
    this.yCenter = (height / 2) + y;
}

CMASystem.Connector = function(x1, y1, x2, y2){
    this.x1 = x1;
    this.y1 = y1;
    this.x2 = x2;
    this.y2 = y2;
}

function SystemRenderer(){
    var tasks = [];
    var workers = [];
    var connectors = [];
    var canvas = $('#systemCanvas')[0];
    var context = canvas.getContext("2d");
    var expandedTask = false;
    
    this.init = function(){
        canvas.width = $(window).width();
        canvas.height = $(window).height();
        canvas.onselectstart = function() { return false; }
        context.lineWidth = 2;
        $('#systemCanvas').mousemove(showTaskName);
    }

    function showTaskName(e){
        var xOffset = 0;
        var yOffset = 115;
        var xMousePos = e.pageX - xOffset;
        var yMousePos = e.pageY - yOffset;
        if( !expandedTask ){
            for( item in tasks ){
                if( xMousePos < (tasks[item].x + tasks[item].width) && xMousePos > tasks[item].x ){
                    if( yMousePos < (tasks[item].y + tasks[item].height) && yMousePos > tasks[item].y ){
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

    this.createTasks = function(data){
        var y = 20;
        for( item in data ){
            addTask(y, data[item].length*8, 40, '#FFC028', data[item]);
            addWorker(y, data[item].length*8, 40, '#FFC028', data[item]);
            y += 60;
        }
        createConnector(tasks[2], workers[1]);
        createConnector(tasks[2], workers[3]);
        createConnector(tasks[6], workers[4]);
        createConnector(tasks[3], workers[6]);
        createConnector(tasks[4], workers[6]);
        draw();
    }
    
    function createConnector(task1, task2){
        var connector = new CMASystem.Connector(task1.xCenter, task1.yCenter, task2.xCenter, task2.yCenter);
        connectors.push(connector);
    }

    function draw(){
        drawConnectors();
        for( var i = 0; i < tasks.length; i++){
            drawShape(tasks[i]);
        }
        for( var i = 0; i < workers.length; i++){
            drawShape(workers[i]);
        }
    }

    function drawConnectors(){
        for( var i = 0; i < connectors.length; i++){
            drawConnector(connectors[i]);
        }
    }

    function drawShape(shape){
        context.fillStyle = shape.fill;
        context.fillRect(shape.x, shape.y, shape.width, shape.height);
        context.textBaseline = "middle";
        context.textAlign = "center";
        context.font = "15px sans-serif";
        context.fillStyle = "black";
        context.fillText(shape.text, shape.xCenter, shape.yCenter);
    }
    
    function drawConnector(connector){
        context.moveTo(connector.x1, connector.y1);
        context.lineTo(connector.x2, connector.y2);
        context.strokeStyle = "red";
        context.stroke();
    }

    function clearLocation(shape){
        context.fillStyle = "#FFF";
        context.fillRect(shape.x, shape.y, shape.width*2, shape.height);
    }

    function addTask(y, width, height, fill, text){
        var task = new CMASystem.Task(y, height, text);
        task.fill = fill;
        tasks.push(task);
    }
    
    function addWorker(y, width, height, fill, text){
        var worker = new CMASystem.Worker(y, height, text);
        worker.fill = fill;
        workers.push(worker);
    }

    function expandTask(task, expand){
        if( expand ){
            if( task.fullText != task.text ){
                var newTask = new CMASystem.Task(task.y, 40, task.text);
                newTask.width = task.fullText.length * 8;
                newTask.x = task.x - ((newTask.width - task.width) / 2);
                newTask.text = task.fullText;
                drawShape(newTask);
                expandedTask = newTask;
            }
        } else {
            console.log("unexpanding");
            console.log(task.width);
            console.log(expandedTask.width);
            var newTask = new CMASystem.Task(task.y, 40, task.text);
            clearLocation(task);
            draw();
            expandedTask = false;
        }
    }
}

