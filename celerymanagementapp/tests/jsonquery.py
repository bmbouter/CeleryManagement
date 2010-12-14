import datetime
import time
import collections
import calendar

from celerymanagementapp.jsonquery.xyquery import JsonXYQuery
from celerymanagementapp.jsonquery.modelmap import TestModelModelMap
from celerymanagementapp.models import TestModel
from celerymanagementapp.tests import base

#==============================================================================#
TMArgs = collections.namedtuple('TMArgs', 'date floatval intval charval enumval')

def _create(args):
    x = TestModel(**args._asdict())
    x.save()
    return x
        
def loaddata(data):
    for item in data:
        _create(item)

#==============================================================================#
def sort_result(resdict):
    data = resdict['data']
    data.sort(key=lambda x: x[0])
    resdict['data'] = data
    return resdict
    
def date_timestamp(y,m,d):
    # takes a python datetime.date and converts into a timestamp in milliseconds
    tt = datetime.date(y,m,d).timetuple()
    unixtime = time.mktime(tt)
    return unixtime*1000

#==============================================================================#
class JsonQuery_SimpleSegmentize_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_jsonquery']
    
    def test_simple_all(self):
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'count', }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 3}] }] ),
                (u'B',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 2}] }] ),
                (u'C',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        #expected_output = {
        #    'data': [
        #        [x, {'field': {'method': ''} } ],
        #        ]
        #    }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
        
    def test_simple_range(self):
        input = {
            'segmentize': {
                'field': 'intval',
                'method': ['range', {'min': 1, 'max':8, 'interval':3}],
                },
            'aggregate': [
                { 'field': 'count', }
                ]
            }
        expected_output = {
            'data': [
                (2,[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 2}] }] ),
                (5,[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 3}] }] ),
                (8,[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
    
    def test_simple_values(self):
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['values',['A','B','C','D']],
                },
            'aggregate': [
                { 'field': 'count', }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 3}] }] ),
                (u'B',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 2}] }] ),
                (u'C',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (u'D',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 0}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
    
    def test_simple_each(self):
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['each'],
                },
            'aggregate': [
                { 'field': 'count', }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (u'A',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (u'A',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (u'B',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (u'B',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (u'C',[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)


class JsonQuery_DateSegmentize_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_jsonquery']
    
    def test_date_all(self):
        D = date_timestamp
        input = {
            'segmentize': {
                'field': 'date',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'count', }
                ]
            }
        expected_output = {
            'data': [
                (D(2010,1,4), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 2}] }] ),
                (D(2010,1,11),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,13),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,20),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,24),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
    
    
class JsonQuery_UtilConv_TestCase(base.CeleryManagement_TestCaseBase):
    def test_date_to_python(self):
        from celerymanagementapp.jsonquery.util import date_to_python
        today = datetime.date.today()
        ms = int(time.mktime(today.timetuple()) * 1000)
        
        self.assertEquals(today, date_to_python(ms))
        
        
    def test_datetime_to_python(self):
        from celerymanagementapp.jsonquery.util import datetime_to_python
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)
        ms = int(time.mktime(now.timetuple()) * 1000)
        
        self.assertEquals(now, datetime_to_python(ms))
        
        
    def test_date_from_python(self):
        from celerymanagementapp.jsonquery.util import date_from_python
        today = datetime.date.today()
        ms = int(time.mktime(today.timetuple()) * 1000)
        
        self.assertEquals(ms, date_from_python(today))
        
        
    def test_datetime_from_python(self):
        from celerymanagementapp.jsonquery.util import datetime_from_python
        now = datetime.datetime.now()
        now = now.replace(microsecond=0)
        ms = int(time.mktime(now.timetuple()) * 1000)
        
        self.assertEquals(ms, datetime_from_python(now))
        
        

