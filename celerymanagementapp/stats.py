import datetime
import math
import operator

from django.db.models import Max, Min

from djcelery.models import WorkerState
from celerymanagementapp.models import DispatchedTask
from celerymanagementapp.segmentize import make_segments, Segmentizer
from celerymanagementapp.segmentize import range_query_sequence


def calculate_throughputs(taskname, timerange, interval=1):
    """ Calculates the throughputs for a given task for each interval over the 
        given timerange.
        
        timerange = Range over which to calculate throughputs.  Must be a tuple 
                    of two datetime.datetime or datetime.date objects.
        interval = How often (in seconds) to calculate throughputs.
        
        Returns a list of throughputs.  Each throughput is calculated over the 
        given interval.  The throughputs collectively span the given time 
        range.
    """
    start = timerange[0]
    stop = timerange[1]
    qargs = { 'state': 'SUCCESS', 'tstamp__range': timerange }
    if taskname:
        qargs['name'] = taskname
    
    states_in_range = DispatchedTask.objects.filter(**qargs)
    
    def rate_aggregator(seconds_span):
        def _rate_aggregator(seg):
            return seg.count() / seconds_span
        return _rate_aggregator
    
    interval_secs = datetime.timedelta(seconds=interval)
    segmentizer = Segmentizer(range_query_sequence('tstamp', timerange, interval_secs))
    aggregator = rate_aggregator(float(interval))
    
    segments = make_segments(states_in_range, segmentizer, aggregator)
    # segments contains tuple pairs: (label, value).  We only want the value...
    return map(operator.itemgetter(1), segments)
    

def _calculate_runtimes_fillbins(runtimes, runtime_min, bin_size, bin_count):
    bins = [0 for i in xrange(bin_count)]
    try:
        runtime_iter = iter(runtimes)
        t = runtime_iter.next()
        for i in xrange(len(bins)):
            binmax = (i+1)*bin_size+runtime_min
            while t < binmax:
                bins[i] += 1
                t = runtime_iter.next()
    except StopIteration:
        # catch exception from raw iter.next() method
        pass
    
    for i in xrange(len(bins)):
        binmin = i*bin_size+runtime_min
        binmax = (i+1)*bin_size+runtime_min
        bins[i] = ((binmin, binmax), bins[i])
    
    return bins

    
def _calculate_runtimes_query(taskname, runtime_range=None, search_range=(None,None)):
    #import pdb; pdb.set_trace()
    
    if runtime_range and runtime_range!=(None,None):
        if taskname:
            qs = DispatchedTask.objects.filter(state='SUCCESS', name=taskname, runtime__range=runtime_range)
        else:
            qs = DispatchedTask.objects.filter(state='SUCCESS', runtime__range=runtime_range)
    elif taskname:
        qs = DispatchedTask.objects.filter(state='SUCCESS', name=taskname)
    else:
        qs = DispatchedTask.objects.filter(state='SUCCESS')
    
    # limit results based on the time that the task ran
    if search_range[0] and search_range[1]:
        qs = qs.filter(tstamp__range=search_range)
    elif search_range[0]:
        qs = qs.filter(tstamp__gte=search_range[0])
    elif search_range[1]:
        qs = qs.filter(tstamp__lte=search_range[1])
        
    return qs
    ##return qs.values_list('runtime', flat=True).order_by('runtime')
    
    
class RuntimeInfo(object):
    def __init__(self, vals):
        self._list = vals
    def __iter__(self):
        return self._list.__iter__()
        

def calculate_auto_runtimes(taskname, search_range=(None,None), bin_count=None):
    # Get the 
    runtimeq = _calculate_runtimes_query(taskname, search_range)
    agg = runtimeq.aggregate(Max('runtime'), Min('runtime'))
    runtime_min = agg['runtime__min']  if agg['runtime__min'] is not None else  0.
    runtime_max = agg['runtime__max']  if agg['runtime__max'] is not None else  1.
    runtimes = runtimeq.values_list('runtime', flat=True).order_by('runtime')
    
    if bin_count:
        bin_size = (runtime_max - runtime_min) / bin_count
    else:
        e = "Bad arguments to calculate_autoruntimes().  "
        e += "The argument bin_count must be given."
        raise RuntimeError(e)
    
    bins = _calculate_runtimes_fillbins(runtimes, runtime_min, bin_size, bin_count)
    return bins
    
    
def calculate_explicit_runtimes(taskname, search_range=(None,None), 
                                runtime_range=(0.,None), bin_size=None, 
                                bin_count=None):
    runtime_min = runtime_range[0]  if runtime_range[0] else  0.
    runtime_max = runtime_range[1]  if runtime_range[1] else  0.
    if bin_size and bin_count:
        runtime_max = runtime_min + bin_size*bin_count
    elif runtime_max and bin_size:
        # use math.ceil so the bins always never exclude runtime_max
        bin_count = int(math.ceil((runtime_max - runtime_min) / bin_size))
    elif runtime_max and bin_count:
        bin_size = (runtime_max - runtime_min) / bin_count
    else:
        e = "Bad arguments to calculate_runtimes().  "
        e += "When the maximum runtime_range is given, "
        e += "either bin_size or bin_count must be supplied, "
        e += "and if no maximum runtime_range is given, both must be supplied."
        raise RuntimeError(e)
        
    runtime_range = (runtime_min,runtime_max)
    
    runtimeq = _calculate_runtimes_query( taskname, runtime_range, 
                                          search_range )
    runtimes = runtimeq.values_list('runtime', flat=True).order_by('runtime')
    bins = _calculate_runtimes_fillbins(runtimes, runtime_min, bin_size, bin_count)
    return bins
    
    

    
def calculate_runtimes(taskname, search_range=(None,None), 
                       runtime_range=(0.,None), bin_size=None, bin_count=None, 
                       auto_runtime_range=False):
    """
        Calculate the number of tasks that executed within the given runtime_range.
        
        taskname: 
            The name of the task to calculate for.  If it evaluates to false, 
            all tasks are included.
        search_range: 
            Limit the tasks to those that completed within this range.  This 
            should be a pair of datetime.datetime objects.  If either is None, 
            then no limit is placed on that end of the range.
        runtime_range:
            The range of runtimes to include in the result.  If left at the 
            default (with only a minimum given) then both bin_size and 
            bin_count must be given.  If the range contains both the min and 
            max, then only one of bin_size and bin_count must be given.
            Runtimes are given in seconds, and may be floats.
        bin_size:
            The size of a bin, in seconds.
        bin_count:
            The number of bins to use.  Required if auto_runtime_range is given.
        auto_runtime_range:
            Set the runtime_range automatically absed on other parameters.
            
        Returns a list of tuples where the ith tuple contains information about 
        the ith bin.  The tuples contain: ((binmin,binmax),count).
    """
    if auto_runtime_range:
        return calculate_auto_runtimes(taskname, search_range, bin_count)
    else:
        return calculate_explicit_runtimes(taskname, search_range, runtime_range, bin_size, bin_count)
    
    
    #binmins = [(i*bin_size+runtime_min) for i in range(bin_count)]
    #binmaxs = [((i+1)*bin_size+runtime_min) for i in range(bin_count)]
    #bins = [0 for i in range(bin_count)]
    
    #bins = _calculate_runtimes_fillbins(runtimes, bins, binmaxs)
    #return [((a,b),count) for (a,b,count) in itertools.izip(binmins,binmaxs,bins)]
    












