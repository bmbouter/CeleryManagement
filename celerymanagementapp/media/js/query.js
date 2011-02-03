if(CMA.Core.testUrls) {
    CMA.Core.ajax.loadTestUrls();
} else {
    CMA.Core.ajax.loadUrls(); 
}

var c1 = null;

$(document).ready(function() {
    System.Handlers.loadHandlers();
    
    var q = {"segmentize":{"field":"worker","method":["all"]},"aggregate":[{"field":"waittime","methods":["average","max","min"]}]};
    
    submitQuery(JSON.stringify(q));
});

function startChart(data) {
    var options = CMA.Core.DataParser.getTicks();
    c1 = Chart("#chart", data, options);
    c1.displayBarChart(true);
    c1.enableTooltips();
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
                '<td><a href="#" class="' + aggregate_field +
                    '-delete"><strong>x</strong></span></td>' + 
                '</tr>'
            );
            
            $('.' + aggregate_field + '-delete').click(function() {
                $(this).parent().parent().remove(); 
            });
        }
    }
    
    function change_segmentize_method() {
        var that = $('#segmentize_method');
        
        if(that.val() == 'range') {
            $('#segmentize_range').show();
            $('#segmentize_values').hide();
            $('#segmentize_taskname').hide();
        } else if(that.val() == 'values') {
            $('#segmentize_values').show()
            $('#segmentize_range').hide();
            $('#segmentize_taskname').hide();
        } else {
            $('#segmentize_range').hide();
            $('#segmentize_values').hide();
        }
    }
    
    function change_segmentize_field() {
        var enum = $('#segmentize_field optgroup[id=enum]'),
            time = $('#segmentize_field optgroup[id=time]'),
            range = $('#segmentize_method option[value=range]');
        
        if(enum.children('[value=' + $(this).val() + ']').length !== 0) {
            range.attr('disabled', 'disabled');
            range.next().attr('selected', 'selected');
            change_segmentize_method();
        } else {
            range.attr('disabled', false);
            range.attr('selected', 'selected');
            change_segmentize_method();
        }
    }
    
    $(':checkbox').change(function() {
        if($(this).attr('checked')) {
            $(this).siblings('div').show();
        } else {
            $(this).siblings('div').hide();
        }
    });
    
    $('#segmentize_field').change(change_segmentize_field);
    
    $('#segmentize_method').change(change_segmentize_method);
    
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

