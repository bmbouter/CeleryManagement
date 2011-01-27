var System = (typeof System === "undefined" || !System) ? {} : System;

System.EventBus = (function() {
    var _handlers = { };
    
    var addEventHandler = function(type, callback) {
        if(!_handlers[type]) {
            _handlers[type] = [];
        }

        _handlers[type].push(callback);
    };

    var fireEvent = function(type, arg) {
        if(!_handlers[type]) {
            console.error("No such handler for event type: " + type);
            return;
        }

        var i, handler;
        var length = _handlers[type].length;

        for(i = 0; i < length; i++) {
            handler = _handlers[type][i];

            if(typeof handler === 'function') {
                handler.call(this, arg);
            }
        }
    };

    var isArray = function(array) {
        return Object.prototype.toString.apply(array) === '[object Array]';
    };

    return {
        addEventHandler: addEventHandler,
        fireEvent: fireEvent
    };
}());

