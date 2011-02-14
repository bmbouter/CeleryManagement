import datetime
import time
import collections
import calendar

from celerymanagementapp.jsonquery.xyquery import JsonXYQuery
from celerymanagementapp.jsonquery.filter import JsonFilter, BadFilterOpArguments
from celerymanagementapp.jsonquery.modelmap import TestModelModelMap
from celerymanagementapp.jsonquery.exception import JsonQueryError
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
    ##print unixtime
    return unixtime*1000
    
def datetime_timestamp(y,m,d,h=0,mi=0,s=0):
    # takes a python datetime.date and converts into a timestamp in milliseconds
    tt = datetime.datetime(y,m,d,h,mi,s).timetuple()
    unixtime = time.mktime(tt)
    ##print unixtime
    return unixtime*1000
    
def timedelta_ms(days=0, seconds=0, milliseconds=0):
    seconds += days * 60*60*24
    milliseconds += seconds * 1000
    return milliseconds

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
        
    def test_date_range(self):
        D = date_timestamp
        input = {
            "segmentize": {
                "field":"date",
                "method": ["range", {"min": D(2010,1,10), "max": D(2010,1,22), "interval": timedelta_ms(days=6)}]
                },
            "aggregate": [
                { "field":"count",
                  "methods":["enumerate"] }
                ]
            }
        expected_output = {
            'data': [
                (D(2010,1,13), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 2}] }] ),
                (D(2010,1,19), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
        
    def test_date_values(self):
        D = date_timestamp
        input = {
            "segmentize": {
                "field":"date",
                "method": ["values", [D(2010,1,1), D(2010,1,4), D(2010,1,13),]],
                },
            "aggregate": [
                { "field":"count", }
                ]
            }
        expected_output = {
            'data': [
                (D(2010,1,1), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 0}] }] ),
                (D(2010,1,4), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 2}] }] ),
                (D(2010,1,13),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        
        query = JsonXYQuery(TestModelModelMap(), input)
        ##print 'filter args:  {0}\n'.format(query.filter.filter_args)
        ##print 'exclude args: {0}\n'.format(query.filter.exclude_args)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
        
    def test_date_each(self):
        D = date_timestamp
        input = {
            "segmentize": {
                "field":"date",
                "method": ["each"],
                },
            "aggregate": [
                { "field":"count", }
                ]
            }
        expected_output = {
            'data': [
                (D(2010,1,4),  [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,4),  [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,11), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,13), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,20), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,24), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
        

class JsonQuery_DateTimeSegmentize_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_jsonquery']
    
    def test_date_all(self):
        D = datetime_timestamp
        input = {
            'segmentize': {
                'field': 'datetime',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'count', }
                ]
            }
        expected_output = {
            'data': [
                (D(2010,1,4,12), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 2}] }] ),
                (D(2010,1,11,12),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,13,12),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,20,12),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                (D(2010,1,24,12),[{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
        
    def test_date_range(self):
        D = datetime_timestamp
        input = {
            "segmentize": {
                "field":"datetime",
                "method": ["range", {"min": D(2010,1,10,12), "max": D(2010,1,22,12), "interval": timedelta_ms(days=6)}]
                },
            "aggregate": [
                { "field":"count",
                  "methods":["enumerate"] }
                ]
            }
        expected_output = {
            'data': [
                (D(2010,1,13,12), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 2}] }] ),
                (D(2010,1,19,12), [{ 'fieldname':'count', 'methods': [{'name':'count', 'value': 1}] }] ),
                ]
            }
        
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
        

class JsonQuery_SimpleAggregate_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_jsonquery']
    
    def is_sqlite3(self):
        # Simple technique for finding database engine.  Will not work in all cases.
        from django.conf import settings
        dbs = settings.DATABASES
        defaultdb = dbs.get('default', None)
        if defaultdb:
            return defaultdb.get('ENGINE') == 'django.db.backends.sqlite3'
        return False  # 
        
    def has_variance(self):
        # Determines if Variance is supported by the underlying database 
        # engine.  It is not supported by SQLite out-of-the-box.
        from django.db import DatabaseError
        from django.db.models import Variance
        qs = TestModel.objects.all()
        try:
            qs.aggregate(Variance('floatval'))['floatval__variance']
        except DatabaseError as e:
            if str(e) == 'no such function: VAR_POP':
                return False
            else:
                return True
        return True
    
    def test_simple_min(self):
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'floatval', 
                  'methods': ['min'] }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'floatval', 'methods': [{'name':'min', 'value': 4.0}] }] ),
                (u'B',[{ 'fieldname':'floatval', 'methods': [{'name':'min', 'value': 3.0}] }] ),
                (u'C',[{ 'fieldname':'floatval', 'methods': [{'name':'min', 'value': 88.0}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
    
    def test_simple_max(self):
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'floatval', 
                  'methods': ['max'] }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'floatval', 'methods': [{'name':'max', 'value': 7.0}] }] ),
                (u'B',[{ 'fieldname':'floatval', 'methods': [{'name':'max', 'value': 5.0}] }] ),
                (u'C',[{ 'fieldname':'floatval', 'methods': [{'name':'max', 'value': 88.0}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
    
    def test_simple_variance(self):
        if not self.has_variance():
            print '\nThis database does not support computing Variance.  Skipping test.'
            return
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'floatval', 
                  'methods': ['variance'] }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'floatval', 'methods': [{'name':'variance', 'value': 5.0}] }] ),
                (u'B',[{ 'fieldname':'floatval', 'methods': [{'name':'variance', 'value': 4.0}] }] ),
                (u'C',[{ 'fieldname':'floatval', 'methods': [{'name':'variance', 'value': 88.0}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals('variance', output['data'][0][1]['methods'][0]['name'])
        self.assertEquals('variance', output['data'][1][1]['methods'][0]['name'])
        self.assertEquals('variance', output['data'][2][1]['methods'][0]['name'])
    
    def test_simple_average(self):
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'floatval', 
                  'methods': ['average'] }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'floatval', 'methods': [{'name':'average', 'value': 5.0}] }] ),
                (u'B',[{ 'fieldname':'floatval', 'methods': [{'name':'average', 'value': 4.0}] }] ),
                (u'C',[{ 'fieldname':'floatval', 'methods': [{'name':'average', 'value': 88.0}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
    
    def test_simple_sum(self):
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'floatval', 
                  'methods': ['sum'] }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'floatval', 'methods': [{'name':'sum', 'value': 15.0}] }] ),
                (u'B',[{ 'fieldname':'floatval', 'methods': [{'name':'sum', 'value': 8.0}] }] ),
                (u'C',[{ 'fieldname':'floatval', 'methods': [{'name':'sum', 'value': 88.0}] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
    
    def test_simple_enumerate(self):
        input = {
            'segmentize': {
                'field': 'enumval',
                'method': ['all'],
                },
            'aggregate': [
                { 'field': 'floatval', 
                  'methods': ['enumerate'] }
                ]
            }
        expected_output = {
            'data': [
                (u'A',[{ 'fieldname':'floatval', 'methods': [{'name':'enumerate', 'value': {4.0: 2, 7.0: 1}}] }] ),
                (u'B',[{ 'fieldname':'floatval', 'methods': [{'name':'enumerate', 'value': {3.0: 1, 5.0: 1}}] }] ),
                (u'C',[{ 'fieldname':'floatval', 'methods': [{'name':'enumerate', 'value': {88.0: 1}       }] }] ),
                ]
            }
        query = JsonXYQuery(TestModelModelMap(), input)
        output = query.do_query()
        output = sort_result(output)
        self.assertEquals(expected_output, output)
        
        
class JsonQuery_Filter_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_jsonquery']
    
    def test_empty_filter(self):
        input = {}
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        self.assertEquals(6, qs.count())
    
    def test_filter_eq1(self):
        input = { 'filter': [['enumval','A'],], }
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        
        self.assertEquals(3, qs.count())
        pks = [obj.pk for obj in qs]
        pks.sort()
        self.assertEquals([1,4,6], pks)
    
    def test_filter_eq2(self):
        input = { 'filter': [['enumval','==','A'],], }
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        
        self.assertEquals(3, qs.count())
        pks = [obj.pk for obj in qs]
        pks.sort()
        self.assertEquals([1,4,6], pks)
    
    def test_filter_ne(self):
        input = { 'filter': [['enumval','!=','A'],], }
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        
        self.assertEquals(3, qs.count())
        pks = [obj.pk for obj in qs]
        pks.sort()
        self.assertEquals([2,3,5], pks)
    
    def test_filter_gt(self):
        input = { 'filter': [['intval','>',4],], }
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        
        self.assertEquals(3, qs.count())
        pks = [obj.pk for obj in qs]
        pks.sort()
        self.assertEquals([3,4,5], pks)
    
    def test_filter_lt(self):
        input = { 'filter': [['intval','<',4],], }
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        
        self.assertEquals(2, qs.count())
        pks = [obj.pk for obj in qs]
        pks.sort()
        self.assertEquals([1,2], pks)
    
    def test_filter_gte(self):
        input = { 'filter': [['intval','>=',4],], }
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        
        self.assertEquals(4, qs.count())
        pks = [obj.pk for obj in qs]
        pks.sort()
        self.assertEquals([3,4,5,6], pks)
    
    def test_filter_lte(self):
        input = { 'filter': [['intval','<=',4],], }
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        
        self.assertEquals(3, qs.count())
        pks = [obj.pk for obj in qs]
        pks.sort()
        self.assertEquals([1,2,6], pks)
        
    def test_filter_range(self):
        input = { 'filter': [['intval','range',4,6],], }
        filter = JsonFilter(TestModelModelMap(), input)
        qs = filter(TestModel.objects.all())
        
        self.assertEquals(3, qs.count())
        pks = [obj.pk for obj in qs]
        pks.sort()
        self.assertEquals([3,4,6], pks)
        
    def test_bad_filter_args(self):
        input = { 'filter': [['enumval','==','A','B'],], }
        self.assertRaises(BadFilterOpArguments, JsonFilter, TestModelModelMap(), input)
        input = { 'filter': [['enumval','range','A'],], }
        self.assertRaises(BadFilterOpArguments, JsonFilter, TestModelModelMap(), input)
        
    def test_bad_filter_op(self):
        input = { 'filter': [['enumval','=','A'],], }
        self.assertRaises(JsonQueryError, JsonFilter, TestModelModelMap(), input)
    

class JsonQuery_ModelMap_TestCase(base.CeleryManagement_TestCaseBase):
    fixtures = ['test_jsonquery']
    
    
        # 'date':         agg_methods_numeric,
        # 'datetime':     agg_methods_numeric,
        # 'floatval':     agg_methods_numeric,
        # 'intval':       agg_methods_numeric,
        
        # 'charval':      ['count', 'enumerate',],
        # 'enumval':      ['count', 'enumerate',],
        
    # segmentization_methods = {
        # 'date':         ['each', 'range',],
        # 'datetime':     ['each', 'range',],
        # 'floatval':     ['each', 'range',],
        # 'intval':       ['each', 'range',],
        
        # 'charval':      ['each', 'values', 'all',],
        # 'enumval':      ['each', 'values', 'all',],
    
    def test_metadata_keys(self):
        expected = {
            'date': {},
            'datetime': {},
            'floatval': {},
            'intval': {},
            'charval': {},
            'enumval': {},
            }
        meta = TestModelModelMap().get_metadata()
        keys = meta.keys()
        keys.sort()
        self.assertEquals(['charval','count','date','datetime','enumval',
                           'floatval','intval'], keys)
    
    def test_metadata(self):
        meta = TestModelModelMap().get_metadata()
        
        # charval
        self.assertEquals({
            'type':         'string',
            'allow_null':   False,
            'segmentize':   {'methods': ['each', 'values', 'all',]},
            'aggregate':    {'methods': ['count', 'enumerate',]},
            },
            meta['charval'])
        
        # count
        self.assertEquals({
            'type':         'int',
            'allow_null':   False,
            'segmentize':   {'methods': []},
            'aggregate':    {'methods': ['count',]},
            },
            meta['count'])
        
        # date
        self.assertEquals({
            'type':         'datetime',
            'allow_null':   True,
            'segmentize':   {'methods': ['each', 'range',]},
            'aggregate':    {'methods': ['count', 'average', 'min', 'max', 'sum', 'variance',]},
            },
            meta['date'])
        
        # datetime
        self.assertEquals({
            'type':         'datetime',
            'allow_null':   True,
            'segmentize':   {'methods': ['each', 'range',]},
            'aggregate':    {'methods': ['count', 'average', 'min', 'max', 'sum', 'variance',]},
            },
            meta['datetime'])
        
        # enumval
        self.assertEquals({
            'type':         'string',
            'allow_null':   False,
            'segmentize':   {'methods': ['each', 'values', 'all',]},
            'aggregate':    {'methods': ['count', 'enumerate',]},
            },
            meta['enumval'])
        
        # floatval
        self.assertEquals({
            'type':         'float',
            'allow_null':   False,
            'segmentize':   {'methods': ['each', 'range',]},
            'aggregate':    {'methods': ['count', 'average', 'min', 'max', 'sum', 'variance',]},
            },
            meta['floatval'])
        
        # intval
        self.assertEquals({
            'type':         'int',
            'allow_null':   False,
            'segmentize':   {'methods': ['each', 'range',]},
            'aggregate':    {'methods': ['count', 'average', 'min', 'max', 'sum', 'variance',]},
            },
            meta['intval'])
    
    
class JsonQuery_UtilConv_TestCase(base.CeleryManagement_TestCaseBase):
    # TODO: move this to its own module.  The tested functions no longer reside 
    # in the jsonquery package.
    
    def tz_offset(self):
        """ Offset from GMT in seconds.  Accounts for DST. """
        if time.localtime().tm_isdst:
            assert time.daylight
            return time.altzone
        else:
            return time.timezone
    
    def test_date_to_python(self):
        from celerymanagementapp.timeutil import date_to_python
        today = datetime.date.today()
        ms = int(time.mktime(today.timetuple()) * 1000)
        
        self.assertEquals(today, date_to_python(ms))
        
        
    def test_datetime_to_python(self):
        from celerymanagementapp.timeutil import datetime_to_python
        now = datetime.datetime.now()
        # Resolution is in milliseconds.  Strip off smaller values.
        microsecond = now.microsecond - now.microsecond%1000
        now = now.replace(microsecond=microsecond)
        ms = int(time.mktime(now.timetuple())*1000 + now.microsecond/1000.)
        self.assertEquals(now, datetime_to_python(ms))
        
        
    def test_date_from_python(self):
        from celerymanagementapp.timeutil import date_from_python
        today = datetime.date.today()
        ms = int(time.mktime(today.timetuple()) * 1000)
        
        self.assertEquals(ms, date_from_python(today))
        
        
    def test_datetime_from_python(self):
        from celerymanagementapp.timeutil import datetime_from_python
        now = datetime.datetime.now()
        ms = int(time.mktime(now.timetuple())*1000 + now.microsecond/1000)
        
        self.assertEquals(ms, datetime_from_python(now))
        
    def test_datetime_to_python2(self):
        from celerymanagementapp.timeutil import datetime_to_python
        tz = self.tz_offset()*1000
        D = datetime.datetime
        self.assertEquals(D(1970,1,1), datetime_to_python(0+tz))
        self.assertEquals(D(2000,1,1), datetime_to_python(946684800000+tz))
        
    def test_datetime_from_python2(self):
        from celerymanagementapp.timeutil import datetime_from_python
        tz = self.tz_offset()*1000
        D = datetime.datetime
        self.assertEquals(946684800000+tz, datetime_from_python(D(2000,1,1)))
        

