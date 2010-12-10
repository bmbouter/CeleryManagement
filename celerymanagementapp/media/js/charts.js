var CMAChart = (typeof CMAChart == 'undefined' || ! CMAChart) ? {} : CMAChart;

function Chart(loc, data, options) {
    var chart = loc; //The location of the chart in the DOM (div, span, etc)
    var data = data; //The data in the chart
    var options = options; //The options used to display the data
    var plot = null; //A variable to hold the Flot object
    var overview = null; //A variable to hold the Flot object that displays an overview
    this.test = null; //Test variable, not necessary for functioning class
    
    /**
     * Display the chart using the global data and options
     * This should be called whenever changes are made to the chart
     */
    this.displayChart = function() {
        plot = $.plot(chart, data, options);
    }
    
    /**
     * Change the value of a point on the chart
     *
     * @param {String} label the data plot containing the point
     * @param {Double} point the point (x-value) to change
     * @param {Double} value the new value (y-value)
     */
    this.changePoint = function(label, point, value) {
        $.each(data, function(i, obj) {
            if(obj.label == label) {
                $.each(obj.data, function(j, arr) {
                    if(arr[0] == point) {
                        arr[1] = value;
                        return;
                    }
                });

                return;
            }
        });

        displayChart();
    }
    
    /**
     * Change a data plot in its entirety (destroys the previous data plot)
     *
     * @param {String} label the data plot to change
     * @param {Array} data the new data
     */
    this.changeDataPlot = function(label, data) {
        $.each(this.data, function(i, obj) {
            if(obj.label == label) {
                obj.data = data;
                return;
            }
        });

        displayChart();
    }
    
    /**
     * Add a data plot to the chart
     *
     * @param {Object} data the data object containing a label and array of data
     */
    this.addDataPlot = function(data) {
        this.data.push(data);

        displayChart();
    }
    
    /**
     * Displays a bar chart of the current data, using the current options
     */
    this.displayBarChart = function() {
        if(options.series.lines != null) {
            options.series.lines.show = false;
        }

        options.series.bars = {show: true};

        displayChart();
    }
    
    /**
     * Displays a line chart of the current data, using the current options
     */
    this.displayLineChart = function() {
        if(options.series.bars != null) {
            options.series.bars.show = false;
        }

        options.series.lines = {show: true};

        displayChart();
        this.test = plot;
    }
    
    /**
     * Enables points on the chart
     */
    this.enablePoints = function() {
        options.series.points = {show: true};

        displayChart();
    }
    
    /**
     * Disables points on the chart
     */
    this.disablePoints = function() {
        options.series.points = {show: false};

        displayChart();
    }
    
    /**
     * Enable an overview chart at a certain location in the DOM
     * ZOOM CURRENTLY NOT WORKING
     * THIS CAN BREAK GRAPH FUNCTIONALITY AT THE MOMENT 
     *
     * @param {String} loc the location of the overview graph in the DOM
     */
    this.enableOverview = function(loc) {
        var opt = {
            series: {
                lines: { show: true, lineWidth: 1 },
                shadowSize: 0
            },
            xaxis: { ticks: [] },
            yaxis: { ticks: [], autoscaleMargin: 0.1 },
            y2axis: { ticks: [], autoscaleMargin: 0.1 },
            selection: { mode: "x" },
            legend: { show: false }
        };

        overview = $.plot($(loc), data, opt);
    
        //Need references to the global objects to access them inside inner functions
        var plotRef = plot;
        var overviewRef = overview;
        var optionsRef = options;
        var dataRef = data;
        var chartRef = chart;
        
        $(chart).bind('plotselected', function(event, ranges) {
            plotRef = $.plot($(chartRef), dataRef, 
                $.extend(true, {}, optionsRef, {
                    xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to },
                }));
            
            overviewRef.setSelection(ranges, true);
        });

        $(loc).bind('plotselected', function(event, ranges) {
            plotRef.setSelection(ranges);
        });

        /*$(this.chart).bind('plotselected', function(event, ranges) {
            overviewRef.setSelection(ranges);
        });*/
    }
    
    /**
     * Disable an overview chart at a certain location in the DOM
     * 
     * @param {String} loc the location of the overview chart in the DOM
     */
    this.disableOverview = function(loc) {
        $(loc).html("");

        options.selection.mode = 'none';

        displayChart();
    }
    
    /**
     * Add a secondary y-axis with some initial data
     * 
     * @param {Object} obj the data to add to the secondary y-axis
     */
    this.addSecondaryAxis = function(obj) {
        if(options.y2axis == null) {
            obj.yaxis = 2;
            data.push(obj);
            options.y2axis = { }
        }
            
        displayChart();
    }
    
    /**
     * Remove the secondary y-axis and any data associated with it
     */
    this.removeSecondaryAxis = function() {
        if(options.y2axis != null) {
            $.each(data, function(i, obj) {
                if(obj.yaxis == 2) {
                    data.splice(i, 1);
                }
            });

            delete options.y2axis;
        }

        displayChart();
    }
    
    /**
     * Display a checkbox selection for the data that allows you to enable/disable
     * data plots
     * 
     * @param {String} loc the location in the dom to insert the list of checkboxes
     */
    this.enableDataSelection = function(loc) {
        alert("Not implemented yet!");
    }
    
    /**
     * Enable a tooltip display on the chart when you hover over points
     */
    this.enableTooltips = function() {
        if(options.grid == null) {
            options.grid = { hoverable: true, clickable: true };
        }
        
        displayChart();

        function showTooltip(x, y, contents) {
            $('<div id="tooltip">' + contents + '</div>').css({
                position: 'absolute',
                display: 'none',
                top: y + 5,
                left: x + 5,
                border: '1px solid #fdd',
                padding: '2px',
                'background-color': '#fee',
                opacity: 0.80
            }).appendTo("body").fadeIn(200); 
        }
        
        var previousPoint = null;

        $(chart).bind('plothover', function(event, pos, item) {
            if(item) {
                if($('#tooltip').length != 0) {
                    //Do nothing if the tooltip is displayed on a point
                    //This makes the tooltip not redraw when we hover on the same point
                } else if(previousPoint != item.datapoint) {
                    previousPoint = item.datapoint;

                    $('#tooltip').remove();
                    var x = item.datapoint[0].toFixed(2);
                    var y = item.datapoint[1].toFixed(2);

                    showTooltip(item.pageX, item.pageY,
                        item.series.label + ': (' + x + ', ' + y + ')');
                } else {
                    $('#tooltip').remove();
                    previousPoint = null;
                }
            } else {
                $('#tooltip').remove();
            }
        });
    }
    
    /**
     * Disable the tooltip display
     */
    this.disableTooltips = function() {
        $('#tooltip').remove();

        if(options.grid != null) {
            delete options.grid;
        }

        displayChart();
    }

    /**
     * Enable an annotation on a point on a specific data plot
     * 
     * @param {String} label the label of the data plot containing the point
     * @param {Double} point the x-value to add an annotation to
     * @param {String} text the string of text to use in the annotation
     */
    this.addAnnotation = function(label, point, text) {
        var value = null;

        $.each(data, function(i, obj) {
            if(obj.label == label) {
                $.each(obj.data, function(j, arr) {
                    if(arr[0] == point) {
                        value = arr[1];
                        return;
                    }
                });

                return;
            }
        });
        
        var pos = plot.pointOffset({x: point, y: value});
        
        var arrow = {left: pos.left - 4, top: pos.top - 4};
        
        var offset = 6;

        var context = plot.getCanvas().getContext('2d');
        context.moveTo(arrow.left, arrow.top);
        context.lineTo(arrow.left - offset, arrow.top);
        context.lineTo(arrow.left - offset/3, arrow.top - offset/3);
        context.lineTo(arrow.left, arrow.top - offset);
        //context.lineTo(arrow.left + 6, arrow.top);
        context.lineTo(arrow.left, arrow.top);
        context.fillStyle = '#222';
        context.fill();

        context.moveTo(arrow.left - offset/2 + 2, arrow.top - offset/2 + 2);
        context.lineTo(arrow.left - offset*2, arrow.top - offset*2);
        context.strokeStyle = '#222';
        context.stroke();

        /*$(chart).append('<div class="' + label + '_' + point +
            '" style="position: absolute; left: ' + (pos.left + 16) + 'px; ' +
            'top: ' + (pos.top + 16) + 'px; color: #000; font-size: smaller">' + 
            text + '</div>');*/
        
        context.fillText(text, arrow.left - offset*4, arrow.top - offset*3 + offset/2);
    }
    
    /**
     * Remove an annotation that is on a point on a specific data plot
     *
     * @param {String} label the label of the data plot containing the point
     * @param {Double} point the x-value the has the annotation
     */
    this.removeAnnotation = function(label, point) {
        $('.' + label + '_' + point).remove();
    }
};
