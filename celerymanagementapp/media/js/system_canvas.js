var CMASystem = (typeof CMASystem == "undefined" || !CMASystem) ? {} : CMASystem;

CMASystem.Task = function(x, y, width, height, text){
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.fill = '#CCCCCC';
    this.text = text;
}

CMASystem.Queue = function(x, y, width, height, text){
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.fill = '#CCCCCC';
    this.text = text;
}

function SystemRenderer(){
    var tasks = [];
    var canvas = $('#systemCanvas')[0];
    var context = canvas.getContext("2d");
    
    this.init = function(){
        canvas.width = $(window).width();
        canvas.height = $(window).height();
        canvas.onselectstart = function() { return false; }
    }

    this.createTasks = function(data){
        var y = 20;
        for( item in data ){
            addRect(200, y, data[item].length*8, 40, '#FFC028', data[item]);
            y += 60;
        }
        draw();
    }

    function drawshape(shape){
        context.fillStyle = shape.fill;
        context.fillRect(shape.x, shape.y, shape.width, shape.height);
        context.textBaseline = "top";
        context.textAlign = "start";
        context.font = "15px sans-serif";
        context.fillStyle = "black";
        context.fillText(shape.text, shape.x, shape.y);
    }
    
    function draw(){
        for( var i = 0; i < tasks.length; i++){
            drawshape(tasks[i]);
        }
    }

    function addRect(x, y, width, height, fill, text){
        var task = new CMASystem.Task(x, y, width, height, text);
        task.fill = fill;
        tasks.push(task);
    }

}

