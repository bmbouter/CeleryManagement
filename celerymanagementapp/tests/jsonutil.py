import json
import datetime
import time

from celerymanagementapp.tests import base

from celerymanagementapp import jsonutil



class EncodeDatetime_TestCase(base.CeleryManagement_TestCaseBase):
    def test_basic(self):
        d = datetime.datetime(year= 2010,month=12, day=5)
        expected_timestamp = time.mktime(d.timetuple())
        dct = jsonutil.encode_datetime_datetime(d)
        self.assertEquals(dct, {'__type__': 'datetime.datetime', 
                                'timestamp': expected_timestamp})
        
    
class DecodeDatetime_TestCase(base.CeleryManagement_TestCaseBase):
    def test_from_timestamp(self):
        expected_date = datetime.datetime(year= 2010,month=12, day=5)
        ts = time.mktime(expected_date.timetuple())
        dct = {'__type__': 'datetime.datetime', 'timestamp': ts}
        o = jsonutil.decode_datetime_datetime(dct)
        self.assertEquals(o, expected_date)
        
    

class Encode_TestCase(base.CeleryManagement_TestCaseBase):
    def test_datetime(self):
        d = datetime.datetime(year= 2010,month=12, day=5)
        expected_timestamp = time.mktime(d.timetuple())
        s = jsonutil.dumps(d)
        dct = json.loads(s)
        self.assertEquals(dct, {'__type__': 'datetime.datetime', 
                                'timestamp': expected_timestamp})
    
class Decode_TestCase(base.CeleryManagement_TestCaseBase):
    def test_datetime(self):
        expected_date = datetime.datetime(year= 2010,month=12, day=5)
        ts = time.mktime(expected_date.timetuple())
        dct = {'__type__': 'datetime.datetime', 'timestamp': ts}
        s = json.dumps(dct)
        o = jsonutil.loads(s)
        self.assertEquals(o, expected_date)
        

    
