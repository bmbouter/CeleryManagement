import datetime
import time

#==============================================================================#
# Conversions

def noop_conv(x):
    return x
    
## Not using the following custom functions because correcting for DST is too 
## complicated.
# _epoch_datetime = datetime.datetime.fromtimestamp(0)
# _epoch_date = datetime.date.fromtimestamp(0)
    
# def _date_to_timestamp(d):
    # x = d - _epoch_date
    # return x.days*86400000 # 86,400,000 ms in a day
    # #return int((x.days*86400 + x.seconds)*1000. + x.microseconds/1000.)
    
# def _datetime_to_timestamp(d):
    # x = d - _epoch_datetime
    # return int((x.days*86400 + x.seconds)*1000. + x.microseconds/1000.)
    
def date_to_python(val):
    """ Convert an int representing milliseconds since Jan 1, 1970 to a Python 
        datetime.date.  The given int must be in UTC.  The return value is in 
        local time.
    """
    return datetime.date.fromtimestamp(val/1000.)

def datetime_to_python(val):
    """ Convert an int representing milliseconds since Jan 1, 1970 to a Python 
        datetime.datetime.  The given int must be in UTC.  The return value is 
        in local time.
    """
    return datetime.datetime.fromtimestamp(val/1000.)
    
def date_from_python(val):
    """ Convert a Python datetime.date to an int representing the number of 
        milliseconds since midnight Jan 1, 1970.  The given date must be in 
        local time.  The return value is in UTC. 
    """
    tt = val.timetuple()
    unixtime = time.mktime(tt)
    return int(unixtime*1000)
    
def datetime_from_python(val):
    """ Convert a Python datetime.datetime to an int representing the number of 
        milliseconds since midnight Jan 1, 1970.  The given datetime must be in 
        local time.  The return value is in UTC. 
    """
    tt = val.timetuple()
    unixtime = time.mktime(tt)
    return int(unixtime*1000)

#==============================================================================#


