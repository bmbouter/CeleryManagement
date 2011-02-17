CMA.Core.QuerySystem = (function() {
    if(CMA.Core.testUrls) {
        CMA.Core.ajax.loadTestUrls();
    } else {
        CMA.Core.ajax.loadUrls(); 
    }
    
    var c1 = null,
        time_factors_milliseconds = {
            seconds: 1000,
            minutes: 60000, 
            hours: 3600000, 
            days: 86400000,
            months: 2.62974383e9,
            years: 3.1556926e10
        },
        time_factors_seconds = {
            seconds: 1,
            minutes: 60, 
            hours: 3600, 
            days: 86400,
            months: 2.62974383e6,
            years: 3.1556926e7
        },
        field_info = undefined,
        labels = {
            range: 'Range',
            values: 'Values',
            all: 'All',
            each: 'Each',
            count: 'Count',
            average: 'Average',
            min: 'Min',
            max: 'Max',
            sum: 'Sum',
            variance: 'Variance',
            enumerate: 'Enumerate'
        };
    
    $(document).ready(onReady);
    
    function onReady() {
        System.Handlers.loadHandlers();
        CMA.Core.ajax.getFieldInfo(loadFieldInfo);
        $.each($('option[value="choose"]'), function(index, element) {
            $(element).attr('disabled', 'disabled');
        });
        $('#segmentize_range').hide();
        
        var q = {"segmentize":{"field":"worker","method":["all"]},"aggregate":[{"field":"waittime","methods":["average","max","min"]}]};
        
        submitQuery(JSON.stringify(q));
    };
    
    function loadFieldInfo(response) {
        field_info = response;
        console.log(field_info);
    }
    
    function parseDate(field) {
        var jsonDate = new AnyTime.Converter(
                {format: '{"year":"%Y","month":"%m","day":"%d","hour":"%H","minute":"%i","second":"%s"}'}
            ),
            converter = new AnyTime.Converter(),
            parsedDate = null,
            date = null;
        
        parsedDate = converter.parse($(field).val());
        obj = JSON.parse(jsonDate.format(parsedDate));
        //console.log(obj);
        
        date = new Date(parseFloat(obj.year), parseFloat(obj.month), parseFloat(obj.day), parseFloat(obj.hour),
                        parseFloat(obj.minute), parseFloat(obj.second));
        //console.log(date.getTime());
        
        return date.getTime();
    };
    
    var startChart = function(data) {
        var displayBarChart = $('#displayBarChart'),
            displayLineChart = $('#displayLineChart'),
            enableTooltips = $('#enableTooltips'),
            disableTooltips = $('#disableTooltips'),
            enableLegend = $('#enableLegend'),
            disableLegend = $('#disableLegend');
        
        var options = CMA.Core.DataParser.getTicks();
        c1 = Chart("#chart", data, options);
        
        if(displayBarChart.attr('checked')) {
            c1.displayBarChart(true);
        } else {
            c1.displayLineChart();
        }
        
        if(enableTooltips.attr('checked')) {
            c1.enableTooltips();
        } else {
            c1.disableTooltips();
        }
        
        if(enableLegend.attr('checked')) {
            c1.enableLegend();
        } else {
            c1.disableLegend();
        }
    }
    
    function formatData(response) {
        var i,
            field = $('#segmentize_field');
        
        if(CMA.Core.testUrls) {
            response = $.parseJSON(response);
        }
        
        System.EventBus.fireEvent('formatData', response);
    }
    
    function submitQuery(query) {
        CMA.Core.ajax.getDispatchedTasksData(query, formatData);
    }
    
    function createQuery() {
        var object = { };
        
        if($('#filter').attr('checked')) {
            object.filter = [[ ]];
            
            $('#filter_options').children('.fields').children().each(function(i, child) {
                if($(child).parent().css('display') !== 'none') {
                    if(parseFloat($(child).val())) {
                        object.filter[0].push(parseFloat($(child).val()));
                    } else {
                        object.filter[0].push($(child).val());
                    }
                }
            });
        }
        
        if($('#exclude').attr('checked')) {
            object.exclude = [[ ]];
            
            $('#exclude_options').children('.fields').children().each(function(i, child) {
                if($(child).parent().css('display') !== 'none') {
                    if(parseFloat($(child).val())) {
                        object.exclude[0].push(parseFloat($(child).val()));
                    } else {
                        object.exclude[0].push($(child).val());
                    }
                }
            });
        }
        
        //Segmentize info
        object.segmentize = { };
        object.segmentize.field = $('#segmentize_field').val();
        object.segmentize.method = [ $('#segmentize_method').val() ];
        
        var field = $('#segmentize_field');
        
        if($('#segmentize_method').val() == 'range') {
            object.segmentize.method.push({});
            
            $.each($('#segmentize_range').children('div').children('input'), function(i, v) {
                if(field.val() === 'runtime' || field.val() === 'totaltime' || field.val() === 'waittime') {
                    if($(v).attr('name') !== 'interval') {
                        object.segmentize.method[1][$(v).attr('name')] = parseFloat($(v).val());
                    } else {
                        object.segmentize.method[1][$(v).attr('name')] = toSeconds($(v).val(), $('#interval_select').val());
                    }
                } else {
                    if($(v).attr('name') !== 'interval') {
                        object.segmentize.method[1][$(v).attr('name')] = parseDate(v);
                    } else {
                        object.segmentize.method[1][$(v).attr('name')] = toMilliseconds($(v).val(), $('#interval_select').val());
                    }
                }
            });
        } else if($('#segmentize_method').val() == 'values') {
            object.segmentize.method.push($('#segmentize_values').children('div').children('input').val().split(/[\s,]+/));
        }
        
        //Aggregate info
        object.aggregate = [ ];
        
        var fields = $('#aggregate_table tr');
        
        fields.each(function(i, f) {
            if(i != 0) {
                var children = $(f).children();
                object.aggregate.push({ });
                object.aggregate[i - 1].field = $.text([children[0]]);
                object.aggregate[i - 1].methods = $.text([children[1]]).split(/[\s,]+/);
            }
        });
        
        console.log(JSON.stringify(object));
        submitQuery(JSON.stringify(object));
    }
    
    function toMilliseconds(time, type) {
        if(type === 'seconds') {
            return time * time_factors_milliseconds.seconds;
        } else if(type === 'minutes') {
            return time * time_factors_milliseconds.minutes;
        } else if(type === 'hours') {
            return time * time_factors_milliseconds.hours;
        } else if(type === 'days') {
            return time * time_factors_milliseconds.days;
        } else if(type === 'months') {
            return time * time_factors_milliseconds.months;
        } else if(type === 'years') {
            return time * time_factors_milliseconds.years;
        } else {
            return null;
        }
    }
    
    function toSeconds(time, type) {
        if(type === 'seconds') {
            return time * time_factors_seconds.seconds;
        } else if(type === 'minutes') {
            return time * time_factors_seconds.minutes;
        } else if(type === 'hours') {
            return time * time_factors_seconds.hours;
        } else if(type === 'days') {
            return time * time_factors_seconds.days;
        } else if(type === 'months') {
            return time * time_factors_seconds.months;
        } else if(type === 'years') {
            return time * time_factors_seconds.years;
        } else {
            return null;
        }
    }
    
    function toRelativeTimeMilliseconds(time, type) {
        if(type === 'seconds') {
            return time / time_factors_milliseconds.seconds;
        } else if(type === 'minutes') {
            return time / time_factors_milliseconds.minutes;
        } else if(type === 'hours') {
            return time / time_factors_milliseconds.hours;
        } else if(type === 'days') {
            return time / time_factors_milliseconds.days;
        } else if(type === 'months') {
            return time / time_factors_milliseconds.months;
        } else if(type === 'years') {
            return time / time_factors_milliseconds.years;
        } else {
            return null;
        }
    }
    
    function toRelativeTimeSeconds(time, type) {
        if(type === 'seconds') {
            return time / time_factors_seconds.seconds;
        } else if(type === 'minutes') {
            return time / time_factors_seconds.minutes;
        } else if(type === 'hours') {
            return time / time_factors_seconds.hours;
        } else if(type === 'days') {
            return time / time_factors_seconds.days;
        } else if(type === 'months') {
            return time / time_factors_seconds.months;
        } else if(type === 'years') {
            return time / time_factors_seconds.years;
        } else {
            return null;
        }
    }
    
    //Query options panel event listeners
    $(function() {
        function add_aggregation() {
            var table = $('#aggregate_table tr:last');
            
            if(!$('#aggregate_methods').val()) {
                alert("Select methods for field: " + $('#aggregate_field').val());
            } else {
                var aggregate_field = $('#aggregate_field').val();
                var aggregate_methods = $('#aggregate_methods').val();
                
                table.after(
                    '<tr><td>' + aggregate_field + '</td>' +
                    '<td>' + aggregate_methods + '</td>' +
                    '<td><span class="' + aggregate_field +
                        '-delete red ' + 'click"><strong>x</strong></span></td>' + 
                    '</tr>'
                );
                
                $('.' + aggregate_field + '-delete').click(function() {
                    $(this).parent().parent().remove(); 
                });
            }
        }
        
        function change_segmentize_method() {
            var method = $('#segmentize_method'),
                field = $('#segmentize_field');
            
            if(method.val() == 'range') {
                if(method.attr('disabled') === 'disabled') {
                    $('#segmentize_range').hide()
                } else {
                    $('#segmentize_range').show();
                }
                
                $('#segmentize_values').hide();
                $('#segmentize_taskname').hide();
            } else if(method.val() == 'values') {
                if(method.attr('disabled') === 'disabled') {
                    $('#segmentize_values').hide();
                } else {
                    $('#segmentize_values').show();
                }
                
                $('#segmentize_range').hide();
                $('#segmentize_taskname').hide();
            } else {
                $('#segmentize_range').hide();
                $('#segmentize_values').hide();
            }
        }
        
        function change_segmentize_field() {
            var method = $('#segmentize_method'),
                field = $('#segmentize_field');
            
            var i,
                value = $(field).val(),
                object = field_info[value],
                segmentize = object.segmentize,
                methods = segmentize.methods,
                length = methods.length;

            method.html("");
            
            for(i = 0; i < length; i++) {
                var html = '<option label="' + labels[methods[i]] + '" value="' + methods[i] + '"></option>';
                method.append(html);
            }
            
            $('#range_min').AnyTime_noPicker();
            $('#range_max').AnyTime_noPicker();
            
            if(value === 'sent' || value === 'received' || value === 'started' ||
                    value === 'succeeded' || value === 'failed') {
                $('#range_min').AnyTime_picker({format: "%Y-%m-%d %T"});
                $('#range_max').AnyTime_picker({format: "%Y-%m-%d %T"});
            }
            
            change_segmentize_method();
        }
        
        function change_aggregate_field() {
            var method = $('#aggregate_methods'),
                field = $('#aggregate_field');
                
            var i,
                value = $(field).val(),
                object = field_info[value],
                aggregate = object.aggregate,
                methods = aggregate.methods,
                length = methods.length;

            method.html("");
            
            if(value === 'count') {
                method.append('<option label="Count" value="count"></option>');
            } else {
                for(i = 0; i < length; i++) {
                    var html = '<option label="' + labels[methods[i]] + '" value="' + methods[i] + '"></option>';
                    method.append(html);
                }
            }
        }
        
        $('#segmentize_field').change(change_segmentize_field);
        
        $('#segmentize_method').change(change_segmentize_method);
        
        $('#aggregate_field').change(change_aggregate_field);
        
        $('#add_aggregation').click(add_aggregation);
        
        $(':checkbox').change(function() {
            if($(this).attr('checked')) {
                $(this).siblings('div').show();
            } else {
                $(this).siblings('div').hide();
            }
        });
        
        $('#filter_option').change(function() {
            var field = $('#filter_arg2');
            
            if($(this).val() === 'range') {
                field.show().next().show();
            } else {
                field.hide().next().hide();
            } 
        });
        
        $('#exclude_option').change(function() {
            var field = $('#exclude_arg2');
            
            if($(this).val() === 'range') {
                field.show().next().show();
            } else {
                field.hide().next().hide();
            }
        });
        
        //$('#range_min').AnyTime_picker({format: "%Y-%m-%d %T"});
        //$('#range_max').AnyTime_picker({format: "%Y-%m-%d %T"});
    });
    
    //Chart options panel event listeners
    $(function() {
        var displayBarChart = $('#displayBarChart'),
            displayLineChart = $('#displayLineChart'),
            enableTooltips = $('#enableTooltips'),
            disableTooltips = $('#disableTooltips'),
            enableLegend = $('#enableLegend'),
            disableLegend = $('#disableLegend');
        
        displayBarChart.click(function() {
            if($(this).attr('checked')) {
                displayLineChart.attr('checked', false);
                c1.displayBarChart();
            } else {
                displayLineChart.attr('checked', true);
                c1.displayLineChart();
            }
        });
        
        displayLineChart.click(function() {
            if($(this).attr('checked')) {
                displayBarChart.attr('checked', false);
                c1.displayLineChart();
            } else {
                displayBarChart.attr('checked', true);
                c1.displayBarChart();
            }
        });
        
        enableTooltips.click(function() {
            if($(this).attr('checked')) {
                disableTooltips.attr('checked', false);
                c1.enableTooltips();
            } else {
                disableTooltips.attr('checked', true);
                c1.disableTooltips();
            }
        });
        
        disableTooltips.click(function() {
            if($(this).attr('checked')) {
                enableTooltips.attr('checked', false);
                c1.disableTooltips();
            } else {
                enableTooltips.attr('checked', true);
                c1.disableTooltips();
            }
        });
        
        enableLegend.click(function() {
            if($(this).attr('checked')) {
                disableLegend.attr('checked', false);
                c1.enableLegend();
            } else {
                disableLegend.attr('checked', true);
                c1.disableLegend();
            }
        });
        
        disableLegend.click(function() {
            if($(this).attr('checked')) {
                enableLegend.attr('checked', false);
                c1.disableLegend();
            } else {
                enableLegend.attr('checked', true);
                c1.enableLegend();
            }
        });
    });
    
    return {
        createQuery: createQuery,
        startChart: startChart
    };
}());
