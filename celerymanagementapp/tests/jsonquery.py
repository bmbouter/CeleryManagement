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
    # takes a python datetime.date and converts it to a float
    tt = datetime.date(y,m,d).timetuple()
    unixtime = calendar.timegm(tt)
    return unixtime

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
                (u'A',{'count': 3}),
                (u'B',{'count': 2}),
                (u'C',{'count': 1}),
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
                (2,{'count': 2}), # 1..4
                (5,{'count': 3}), # 4..7
                (8,{'count': 1}), # 7..10
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
                (u'A',{'count': 3}),
                (u'B',{'count': 2}),
                (u'C',{'count': 1}),
                (u'D',{'count': 0}),
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
                (u'A',{'count': 1}),
                (u'A',{'count': 1}),
                (u'A',{'count': 1}),
                (u'B',{'count': 1}),
                (u'B',{'count': 1}),
                (u'C',{'count': 1}),
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
                (D(2010,1,4),{'count': 2}),
                (D(2010,1,11),{'count': 1}),
                (D(2010,1,13),{'count': 1}),
                (D(2010,1,20),{'count': 1}),
                (D(2010,1,24),{'count': 1}),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
    
    
    
    

