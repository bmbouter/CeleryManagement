import datetime
import math

from djcelery.models import WorkerState, TaskState

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
    if taskname:
        states_in_range = TaskState.objects.filter(name=taskname, state='SUCCESS', 
                                                   tstamp__range=(start, stop))
    else:
        states_in_range = TaskState.objects.filter(state='SUCCESS', 
                                                   tstamp__range=(start, stop))
    
    # TODO: clean up the following code
    throughputs = []
    finterval = float(interval)
    interval_secs = datetime.timedelta(seconds=interval)
    mintime = start
    while mintime < stop:
        maxtime = mintime + interval_secs
        qs = states_in_range.filter(tstamp__range=(mintime, maxtime))
        throughputs.append(qs.count()/finterval)
        mintime = maxtime
    
    return throughputs
    
    
def _calculate_runtimes_filterobjects(taskname, runtime_range, search_range):
    if taskname:
        qs = TaskState.objects.filter(name=taskname, state='SUCCESS', 
                                      runtime__range=runtime_range)
    else:
        qs = TaskState.objects.filter(state='SUCCESS', 
                                      runtime__range=runtime_range)
    
    # limit results based on the time that the task ran
    if search_range[0] and search_range[1]:
        qs = qs.filter(tstamp__range=search_range)
    elif search_range[0]:
        qs = qs.filter(tstamp__gte=search_range[0])
    elif search_range[1]:
        qs = qs.filter(tstamp__lte=search_range[1])
    
    # get sorted list of runtimes
    return qs.values_list('runtime', flat=True).order_by('runtime')
    
    
def _calculate_runtimes_fillbins(runtimes, bins, binmaxs):
    try:
        runtime_iter = iter(runtimes)
        t = runtime_iter.next()
        for i in range(len(bins)):
            binmax = binmaxs[i]
            while t < binmax:
                bins[i] += 1
                t = runtime_iter.next()
    except StopIteration:
        # catch exception from raw iter.next() method
        pass
    return bins
    
def calculate_runtimes(taskname, search_range=(None,None), runtime_range=(0.,None), bin_size=None, bin_count=None):
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
            The number of bins to use.
            
        Returns a list of counts.  Each count is one bin.
    """
    runtime_min = runtime_range[0] if runtime_range[0]  else 0.
    runtime_max = runtime_range[1] if runtime_range[1]  else 0.
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
    
    runtimes = _calculate_runtimes_filterobjects(taskname, runtime_range, 
                                                 search_range)
    ##print 'len(runtimes): {0}'.format(len(runtimes))
    ##print runtimes
    binmaxs = [((i+1)*bin_size+runtime_min) for i in range(bin_count)]
    bins = [0 for i in range(bin_count)]
    
    return _calculate_runtimes_fillbins(runtimes, bins, binmaxs)

    