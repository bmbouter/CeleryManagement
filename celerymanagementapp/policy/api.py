import datetime
from celerymanagementapp.policy import exceptions

class TimeIntervalError(exceptions.Error):
    clsname = 'PolicyTimeIntervalError'


def make_time_interval(arg):
    now = datetime.datetime.now()
    if isinstance(arg, datetime.timedelta):
        result = (now-arg, now)
    elif isinstance(arg, (tuple, list)):
        if len(arg) != 2:
            msg = 'Sequence arguments must have a length of two.'
            raise TimeIntervalError(msg)
        a,b = arg
        if isinstance(a, datetime.timedelta):
            if isinstance(b, datetime.timedelta):
            # (timedelta 'a' before now,  timedelta 'b' before now)
                result = (now-a, now-b)
            else:
            # (timedelta 'a' before time 'b',  time 'b')
                result = (b-a, b)
        elif isinstance(b, datetime.timedelta):
            # (time 'a',  timedelta 'b' after time 'a')
            result = (a, a+b)
        else:
            # (time 'a', time'b')
            result = arg
    else:
        msg = 'Argument must be a datetime.timedelta or a sequence of length two.'
        raise TimeIntervalError(msg)
    return (min(result), max(result))

def string_or_sequence(arg):
    if isinstance(arg, basestring):
        arg = [arg]
    return arg
    
def get_filter_seq_arg(field, arg):
    if arg:
        if isinstance(arg, (list, tuple)):
            return { '{0}__in'.format(field): arg }
        else:
            return { field: arg }
    return {}
    
def filter(interval=None, workers=None, tasks=None):
    filterargs = {}
    if interval is not None:
        interval = make_time_interval(interval)
        filterargs['senttime__gte'] = interval[0]
        filterargs['senttime__lt'] = interval[1]
    filterargs.update(get_filter_seq_arg('worker', workers))
    filterargs.update(get_filter_seq_arg('taskname', tasks))
    qs = Model.objects.filter(**filterargs)
    
    
    
    
    
    
    
    if workers:
        if isinstance(workers, (list, tuple)):
            q = {'?__in': workers}
        else:
            q = {'?': workers}




