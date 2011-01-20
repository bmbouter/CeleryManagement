CMA.Core.ajax.loadUrls();
        
var c1 = null;
var data = null;
var options = { };
var json = null;
var formatter = null;
var query = null;
var xhr = null;

$(document).ready(function() {
    formatter = new Formatter();
    
    var q = '{"segmentize":{"field":"worker","method":["all"]},"aggregate":[{"field":"waittime","methods":["average","max","min"]}]}';
    
    submit_query(q);
    
    $(':checkbox').change(function() {
        if($(this).attr('checked')) {
            $(this).siblings('div').show();
        } else {
            $(this).siblings('div').hide();
        }
    });
    
    $('#segmentize_method').change(function() {
        if($(this).val() == 'range') {
            $('#segmentize_range').show();
            $('#segmentize_values').hide();
            $('#segmentize_taskname').hide();
        } else if($(this).val() == 'values') {
            $('#segmentize_values').show()
            $('#segmentize_range').hide();
            $('#segmentize_taskname').hide();
        } else {
            $('#segmentize_range').hide();
            $('#segmentize_values').hide();
        }
    });
    
    $('#add_aggregation').click(function() {
        var table = $('#aggregate_table tr:last');
        
        if(!$('#aggregate_methods').val()) {
            alert("Select methods for field: " + $('#aggregate_field').val());
        } else {
            table.after(
                '<tr><td>' + $('#aggregate_field').val() + '</td>' +
                '<td>' + $('#aggregate_methods').val() + '</td>' +
                '</tr>'
            );
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
});

function create_query() {
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
    
    if($('#segmentize').attr('checked')) {
        object.segmentize = { };
        object.segmentize.field = $('#segmentize_field').val();
        object.segmentize.method = [ $('#segmentize_method').val() ];
        
        if($('#segmentize_method').val() == 'range') {
            object.segmentize.method.push({});
            
            $.each($('#segmentize_range').children('div').children('input'), function(i, v) {
                object.segmentize.method[1][$(v).attr('name')] = parseFloat($(v).val());
            });
        } else if($('#segmentize_method').val() == 'values') {
            object.segmentize.method.push($('#segmentize_values').children('div').children('input').val().split(/[\s,]+/));
        }
    }
    
    if($('#aggregate').attr('checked')) {
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
    }
    
    console.log(JSON.stringify(object));
    submit_query(JSON.stringify(object));
}

function submit_query(query) {
    CMA.Core.ajax.getDispatchedTasksData(query, format_data);
}

$(document).ready(function() {
    //xhr = $.getJSON(CMA.Core.ajax.urls.chart_data_url, format_data);
});

function format_data(response) {
    console.log(response);
    data = formatter.formatData(response);
    show_chart();
}

function show_chart() {
    c1 = new Chart("#chart", data, options);
    c1.displayBarChart(true);
    c1.enableTooltips();
    c1.disableLegend();
}

