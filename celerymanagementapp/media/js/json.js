function json() {
    var query = '{"segmentize": {"field": "state","method": [ "all" ]},"aggregate": [{"field": "count"}]}';
    
    $.post(
        '../../xy_query/dispatched_tasks/',
        query,
        function(data) {
            alert("Data loaded: " + data);
            alert(data.data);
            alert(data.data[0]);
        },
        'json'
    );
    
    /*$.ajax({
        type: 'POST',
        url: '../../xy_query/dispatched_tasks/',
        data: query,
        success: function(data) {
            alert(data);
        },
        contentType: 'application/json',
        dataType: 'application/json',
        processData: false
    });*/
}