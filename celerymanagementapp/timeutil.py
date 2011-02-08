import datetime
import time

#==============================================================================#
# Conversions    
def date_to_python(datestamp):
    """ Convert an int representing milliseconds since Jan 1, 1970 to a Python 
        datetime.date.
        
        :param datestamp: An int represeting UTC time in milliseconds since 
            Jan 1, 1970, or None.
        
        :returns: A Python datetime.date object in local time corresponding to 
            the datestamp parameter, or None if datestamp was None.
    """
    if datestamp is not None:
        return datetime.date.fromtimestamp(datestamp/1000.)
    return datestamp

def datetime_to_python(timestamp):
    """ Convert an int representing milliseconds since Jan 1, 1970 to a Python 
        datetime.datetime.  
        
        :param timestamp: An int represeting UTC time in milliseconds since 
            Jan 1, 1970, or None.
        
        :returns: A Python datetime.datetime object in local time corresponding 
            to the timestamp parameter, or None if timestamp was None.
    """
    if timestamp is not None:
        return datetime.datetime.fromtimestamp(timestamp/1000.)
    return timestamp
    
def date_from_python(dateobj):
    """ Convert a Python datetime.date to an int representing the number of 
        milliseconds since midnight Jan 1, 1970.  
        
        :param dateobj: A Python datetime.date object in local time, or None.
        
        :returns: An int represeting UTC time in milliseconds since Jan 1, 1970 
            corresponding to the dateobj parameter, or None if dateobj was None.
    """
    if dateobj is not None:
        tt = dateobj.timetuple()
        unixtime = time.mktime(tt)
        return int(unixtime*1000)
    return dateobj
    
def datetime_from_python(datetimeobj):
    """ Convert a Python datetime.datetime to an int representing the number of 
        milliseconds since midnight Jan 1, 1970.  
        
        :param datetimeobj: A Python datetime.datetime object in local time, or 
            None.
        
        :returns: An int represeting UTC time in milliseconds since Jan 1, 1970 
            corresponding to the datetimeobj parameter, or None if datetimeobj 
            was None.
    """
    if datetimeobj is not None:
        tt = datetimeobj.timetuple()  # removes fractional seconds
        unixtime = time.mktime(tt)
        # use datetime.microsecond to reapply fractional seconds:
        return int(unixtime*1000 + datetimeobj.microsecond/1000)
    return datetimeobj

#==============================================================================#


