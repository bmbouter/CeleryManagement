var CMA = (typeof CMA === "undefined" || !CMA) ? {} : CMA;
CMA.Core = (typeof CMA.Core === "undefined" || !CMA.Core) ? {} : CMA.Core;

CMA.Core.DataParser = (function() {
    var formattedData = { };
    var ticks = { };

    var formatData = function(data) {        
        var dataArray = data.data;

        console.log(data);
        console.log(dataArray);
                        
        if(typeof(dataArray[0][0]) === 'string') {
            if(dataArray[0][1][0].fieldname === 'runtime') {
                formattedData = runtimeData(dataArray);
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
    
    var stateData = function(dataArray) {
        var data = [];
        var count = 0;
        
        for(var item in dataArray) {
            if(dataArray.hasOwnProperty(item)) {
                var arr = dataArray[item];
            
                var label = arr[0];
            
                for(var method in arr[1]) {
                    if(arr[1].hasOwnProperty(method)) {
                        var methodsArray = arr[1][method].methods;
                    
                        if(methodsArray[0].name === 'enumerate') {
                            valueArray = methodsArray[0].value;
                        
                        
                            for(var value in valueArray) {
                                if(valueArray.hasOwnProperty(value)) {
                                    var obj = { };
                                    obj.data = [];
    
                                    obj.label = label + ' - ' + valueArray[value][0];
                                    obj.data.push([count, valueArray[value][1]]);
    
                                    data.push(obj);
                                }
                            }
                         
                            count+=1;
                        }
                    }
                }
            }
        }
        
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
        
        obj.label = "dummy";
        obj.data = chartData;
        data.push(obj);
    
        return data;
    };
    
    var setTicks = function(labels) {
        ticks = {xaxis: { ticks: [] }};
        
        var length = labels.length, i;
        
        for(i = 0; i < length; i++) {
            ticks.xaxis.ticks.push([i + 0.3, labels[i]]);
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
