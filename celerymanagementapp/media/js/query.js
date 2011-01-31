if(CMA.Core.testUrls) {
        CMA.Core.ajax.loadTestUrls();
} else {
    CMA.Core.ajax.loadUrls(); 
}

var c1 = null;

$(document).ready(function() {
    System.Handlers.loadHandlers();
    
    var q = '{"segmentize":{"field":"worker","method":["all"]},"aggregate":[{"field":"waittime","methods":["average","max","min"]}]}';
    
    submitQuery(q);
    
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
                '<td><a href="#" class="' + aggregate_field +
                    '-delete"><strong>x</strong></span></td>' + 
                '</tr>'
            );
            
            $('.' + aggregate_field + '-delete').click(function() {
                $(this).parent().parent().remove(); 
            });
        }
    }
    
    $('#add_aggregation').click(add_aggregation);
    
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
    submitQuery(JSON.stringify(object));
}

function submitQuery(query) {
    CMA.Core.ajax.getDispatchedTasksData(query, formatData);
}

function formatData(response) {
    if(CMA.Core.testUrls) {
        response = JSON.parse(response);
    }
    
    System.EventBus.fireEvent('formatData', response);
}

function startChart(data) {
    var options = CMA.Core.DataParser.getTicks();
    c1 = Chart("#chart", data, options);
    c1.displayBarChart(true);
    c1.enableTooltips();
}

