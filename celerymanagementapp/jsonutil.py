import json

import datetime
import time


#==============================================================================#
def decode_datetime_datetime(dct):
    """ Convert from a Json dict to a datetime.datetime object. """
    assert dct['__type__'] == 'datetime.datetime'
    
    timestamp = dct.get('timestamp',None)
    if timestamp is not None:
        return datetime.datetime.fromtimestamp(timestamp)
    
    year = dct['year']
    month = dct['month']
    day = dct['day']
    
    keys = ['hour','minute','second','microsecond']
    xdct = dict((k,dct[k]) for k in keys if k in dct)
    return datetime.datetime(year,month,day,**xdct)

def encode_datetime_datetime(o):
    """ Convert from a datetime.datetime object to a Json dict. """
    assert isinstance(o, datetime.datetime)
    return { '__type__': 'datetime.datetime', 
             'timestamp': time.mktime(o.timetuple()) }


#==============================================================================#
_object_decoder_lookup = {
    'datetime.datetime': decode_datetime_datetime,
    }

_object_encoder_lookup = {
    datetime.datetime: encode_datetime_datetime, 
    }

#==============================================================================#
class JsonEncoderError(Exception):
    pass
class JsonDecoderError(Exception):
    pass

class Encoder(json.JSONEncoder):
    def default(self, o):
        try:
            return _object_encoder_lookup[type(o)](o)
        except KeyError:
            pass
        return json.JSONEncoder.default(self, o)


def json_object_decoder(dct):
    tp = dct.get('__type__',None)
    if tp and tp in _object_decoder_lookup:
        try:
            return _object_decoder_lookup[tp](dct)
        except KeyError:
            msg = 'Unrecognized __type__ argument: {0}'.format(tp)
            raise JsonDecoderError(msg)
    return dct


#==============================================================================#
def dumps(obj, *args, **kwargs):
    """ Convert from Python to a Json byte string.  This extends the standard 
        library json.dumps() function to handle more types.  
        
        The arguments are the same as the standard library json.dumps() 
        function. 
    """
    kwargs['cls'] = Encoder
    return json.dumps(obj, *args, **kwargs)

def loads(s, *args, **kwargs):
    """ Convert from a Json byte string to Python objects.  If a dictionary 
        contains a key '__type__', and the value is the name of a recognized 
        type, the dictionary will be converted to the corresponding Python 
        object.  For example, if '__type__'=='datetime.datetime' and the other 
        keys in the dictionary are correct, the result will be a Python 
        datetime.datetime object.  
        
        The arguments to this function are the same as they are for the 
        standard library json.loads() function. 
    """
    kwargs['object_hook'] = json_object_decoder
    return json.loads(s, *args, **kwargs)
    

#==============================================================================#


