var Formatter = function() {
    var formattedData = { };

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

        return formattedData;
    };

    function runtimeData(dataArray) {
        var data = [];
        var count = 0;

        var item;

        for(item in dataArray) {
            var arr = dataArray[item];
            
            var method;
                                    
            for(method in arr[1]) {
                var obj = { };
                var methodsArray = arr[1][method].methods;

                var object;

                obj.label = arr[0] + ' - ' + arr[1][method].fieldname;
                obj.data = [];

                for(object in methodsArray) {
                    obj.data.push([count, methodsArray[object].value]);
                }

                data.push(obj);
            }

            count++;
        }
                
        return data;
    }

    function stateData(dataArray) {
        var data = [];
        var count = 0;

        var item, method;
        
        for(item in dataArray) {
            var arr = dataArray[item];
            
            var label = arr[0];
            
            for(method in arr[1]) {
                var methodsArray = arr[1][method].methods;
                
                if(methodsArray[0].name === 'enumerate') {
                    valueArray = methodsArray[0].value;

                    
                    for(value in valueArray) {
                        var obj = { };
                        obj.data = [];

                        obj.label = label + ' - ' + valueArray[value][0];
                        obj.data.push([count, valueArray[value][1]]);

                        data.push(obj);
                    }
                    
                    count+=1;
                }
            }
        }

        return data;
    }

    function countData(dataArray) {
        var data = [];
        var chartData = [];
        var obj = { };

        var item;

        for(item in dataArray) {
            var arr = dataArray[item];
            var x = arr[0];            
            var methodsArray = arr[1][0].methods;
            
            for(object in methodsArray) {
                chartData.push([x, methodsArray[object].value]);
            }

        }

        obj.data = chartData;
        obj.label = dataArray[0][1][0].fieldname;

        data.push(obj);

        return data;
    }

    function statusData(dataArray) {
        var data = [];
        var count = 0;

        var item;

        for(item in dataArray) {
            var obj = { };

            obj.label = dataArray[item][0];
            obj.data = [[count+=1, dataArray[item][1][0].methods[0].value]];

            data.push(obj);
        }

        return data;
    }

    function dummyData() {
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
    }

    return {
        formatData: formatData
    };
};

