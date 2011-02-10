var CMA = (typeof CMA === "undefined" || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

CMA.Core.DataParser = (function() {
    var formattedData = { };
    var ticks = { };

    var formatData = function(data) {        
        var dataArray = data.data;

        console.log(data);
        console.log(dataArray);
        
        //if(dataArray[0][1] !== NaN) {
            if(typeof(dataArray[0][0]) === 'string') {
                if(dataArray[0][1][0].fieldname === 'runtime') {
                    formattedData = runtimeDataAlternate(dataArray);
                } else if(dataArray[0][1][0].fieldname === 'state') {
                    formattedData = stateData(dataArray);
                } else {
                    formattedData = statusData(dataArray);
                }
            } else if(typeof(dataArray[0][0]) === 'number') {
                if(dataArray[0][1][0].fieldname === 'count') {
                    formattedData = countData(dataArray);
                } else {
                    formattedData = dummyData();
                }
            }
        //} else {
            //formattedData = dummyData();
        //}

        System.EventBus.fireEvent('dataFormatted', formattedData);
        //System.EventBus.fireEvent('labelAxis', labels);
        //return formattedData;
    };

    var runtimeData = function(dataArray) {
        var data = [ ];
        var workerLabels = [ ];
        var axisLabels = [ ];
        
        var i;
        var length = dataArray.length;
        var methodsLength = dataArray[0][1][0].methods.length;

        for(var label in dataArray) {
            if(dataArray.hasOwnProperty(label)) {
                workerLabels[label] = dataArray[label][0];
            }
        }
        
        for(i = 0; i < methodsLength; i++) {
            axisLabels[i] = dataArray[0][1][0].methods[i].name;
        }
                
        for(i = 0; i < length; i++) {
            var j;
            
            var obj = { };
            obj.data = [ ];
            obj.label = workerLabels[i];
    
            for(j = 0; j < methodsLength; j++) {
                obj.data.push([j, dataArray[i][1][0].methods[j].value]);
            }
    
            data.push(obj);
            console.log(data);
        }
        
        setTicks(axisLabels);
        
        return data;
    }
    
    var runtimeDataAlternate = function(dataArray) {
        var data = [];
        var workerLabels = [ ];
        var count = 0;

        var i, j;
        var length = dataArray.length;
        var methodsLength = dataArray[0][1][0].methods.length;
        
        for(i = 0; i < length; i++) {
            var obj = { };
            obj.data = [ ];
            obj.label = dataArray[i][0] + ' - Runtime';
            
            for(j = 0; j < methodsLength; j++) {
                obj.data.push([i, dataArray[i][1][0].methods[j].value]);
            }
            
            data.push(obj);
        }
                
        return data;
    }
    
    var stateData = function(dataArray) {
        var data = [ ];
        var workerLabels = [ ];
        var axisLabels = [ ];
        
        var i, j;
        var length = dataArray.length;
        var valueLength = dataArray[0][1][0].methods[0].value.length;
        
        for(i = 0; i < length; i++) {
            workerLabels[i] = dataArray[i][0];
        }
        
        for(i = 0; i < valueLength; i++) {
            axisLabels[i] = dataArray[0][1][0].methods[0].value[i][0];
        }
        
        for(i = 0; i < valueLength; i++) {
            var obj = { };
            obj.data = [ ];
            obj.label = workerLabels[i];
            
            for(j = 0; j < length; j++) {
                obj.data.push([j, dataArray[i][1][0].methods[0].value[j][1]]);
            }
            
            data.push(obj);
            console.log(data);
        }
        
        setTicks(axisLabels);
        
        return data;
    };
        
    var countData = function(dataArray) {
        var data = [];
        var chartData = [];
        var obj = { };
    
        for(var item in dataArray) {
            if(dataArray.hasOwnProperty(item)) {
                var arr = dataArray[item];
                var x = arr[0];            
                var methodsArray = arr[1][0].methods;
            
                for(var object in methodsArray) {
                    if(methodsArray.hasOwnProperty(object)) {
                        chartData.push([x, methodsArray[object].value]);
                    }
                }
            }
        }
    
        obj.data = chartData;
        obj.label = dataArray[0][1][0].fieldname;
    
        data.push(obj);
    
        return data;
    };
    
    
    var statusData = function(dataArray) {
        var data = [];
        var count = 0;
    
        for(var item in dataArray) {
            if(dataArray.hasOwnProperty(item)) {
                var obj = { };
    
                obj.label = dataArray[item][0];
                obj.data = [[count+=1, dataArray[item][1][0].methods[0].value]];
    
                data.push(obj);
            }
        }
    
        return data;
    };
    
    var dummyData = function() {
        var data = [];
        var chartData = [];
        var obj = { };
        
        var i;
    
        for(i = 0; i < 14; i += 0.5) {
            chartData.push([i, Math.sin(i)]);
        }
        
        obj.label = "Malformed data returned by server";
        obj.data = chartData;
        data.push(obj);
    
        return data;
    };
    
    var setTicks = function(labels) {
        ticks = {xaxis: { ticks: [] }};
        
        var length = labels.length, i;
        
        for(i = 0; i < length; i++) {
            ticks.xaxis.ticks.push([i, labels[i]]);
        }
        
        //console.log(ticks);
    };
    
    var getTicks = function() {
        return ticks;  
    };
    
    return {
        formatData: formatData,
        getTicks: getTicks
    };
}());
