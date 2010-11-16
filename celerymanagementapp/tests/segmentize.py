import datetime
import time

from celerymanagementapp import segmentize
from celerymanagementapp.models import TestModel
from celerymanagementapp.tests import base

class BasicQuerySequence_TestCase(base.CeleryManagement_DBTestCaseBase):
    #fixtures = ['test_segmentize']
    
    def test_basic(self):
        fieldname = 'thefield'
        labels = ['A','B','C']
        res = segmentize.basic_query_sequence(fieldname, labels)
        qseq = list(res)
        self.assertEquals(qseq, [ ('A',{'thefield':'A'}),
                                  ('B',{'thefield':'B'}),
                                  ('C',{'thefield':'C'})
                                ])
    
    def test_basic_tupleargs(self):
        fieldname = 'thefield'
        labels = [('A','a'),('B','b'),('C','c')]
        res = segmentize.basic_query_sequence(fieldname, labels)
        qseq = list(res)
        self.assertEquals(qseq, [ ('A',{'thefield':'a'}),
                                  ('B',{'thefield':'b'}),
                                  ('C',{'thefield':'c'})
                                ])


class RangeQuerySequence_TestCase(base.CeleryManagement_DBTestCaseBase):
    def test_basic(self):
        fieldname = 'thefield'
        range = (3,8)
        interval_size = 2
        res = segmentize.range_query_sequence(fieldname, range, interval_size)
        qseq = list(res)
        self.assertEquals(qseq, [ (4,{'thefield__range':(3,5)}),
                                  (6,{'thefield__range':(5,7)}),
                                  (8,{'thefield__range':(7,9)}),
                                ])
        

