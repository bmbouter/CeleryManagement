import datetime
import time

from celerymanagementapp import segmentize
from celerymanagementapp.models import TestModel
from celerymanagementapp.tests import base

#==============================================================================#
class BasicQuerySequence_TestCase(base.CeleryManagement_DBTestCaseBase):
    
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

#==============================================================================#
class RangeQuerySequence_TestCase(base.CeleryManagement_DBTestCaseBase):
    def test_basic(self):
        fieldname = 'thefield'
        range = (3,8)
        interval_size = 2
        res = segmentize.range_query_sequence(fieldname, range, interval_size)
        qseq = list(res)
        
        self.assertEquals(len(qseq), 3)
        self.assertEquals(qseq[0], (4,{'thefield__gte': 3, 'thefield__lt': 5}))
        self.assertEquals(qseq[1], (6,{'thefield__gte': 5, 'thefield__lt': 7}))
        self.assertEquals(qseq[2], (8,{'thefield__gte': 7, 'thefield__lt': 9}))
    
    def test_dates(self):
        fieldname = 'date'
        d = datetime.date
        range = (d(2010,10,1),d(2010,10,20))
        interval_size = datetime.timedelta(days=7)
        res = segmentize.range_query_sequence(fieldname, range, interval_size)
        qseq = list(res)
        
        self.assertEquals(len(qseq), 3)
        self.assertEquals(qseq[0], ( d(2010,10,4), 
                                     {'date__gte': d(2010,10,1), 
                                      'date__lt':  d(2010,10,8)} )
                         )
        self.assertEquals(qseq[1], ( d(2010,10,11),
                                     {'date__gte': d(2010,10,8), 
                                      'date__lt':  d(2010,10,15)} )
                         )
        self.assertEquals(qseq[2], ( d(2010,10,18),
                                     {'date__gte': d(2010,10,15), 
                                      'date__lt': d(2010,10,22)} )
                         )
        
        
#==============================================================================#
class Segmentizer_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_segmentize']
    
    def test_basic(self):
        from celerymanagementapp.segmentize import Segmentizer
        from celerymanagementapp.segmentize import basic_query_sequence
        
        fieldname = 'enumval'
        labels = ['A','B','C','D']
        szr = Segmentizer( basic_query_sequence(fieldname, labels) )
        res = szr(TestModel.objects.all())
        segments = list(res)
        
        self.assertEquals(len(segments), 4)
        
        lbl0, qs0 = segments[0]
        lbl1, qs1 = segments[1]
        lbl2, qs2 = segments[2]
        lbl3, qs3 = segments[3]
        
        self.assertEquals(lbl0, 'A')
        self.assertEquals(qs0.count(), 3)
        self.assertEquals(lbl1, 'B')
        self.assertEquals(qs1.count(), 2)
        self.assertEquals(lbl2, 'C')
        self.assertEquals(qs2.count(), 1)
        self.assertEquals(lbl3, 'D')
        self.assertEquals(qs3.count(), 0)
        

#==============================================================================#
class AvgAggregator_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_segmentize']
    
    def test_basic(self):
        from celerymanagementapp.segmentize import avg_aggregator
        
        fieldname = 'floatval'
        agg = avg_aggregator(fieldname)  # this returns another function
        
        qs = TestModel.objects.filter(enumval='A')
        self.assertAlmostEqual(agg(qs), 5.0)
        
        qs = TestModel.objects.filter(enumval='B')
        self.assertAlmostEqual(agg(qs), 4.0)
        
        qs = TestModel.objects.filter(enumval='C')
        self.assertAlmostEqual(agg(qs), 88.0)
        
        qs = TestModel.objects.filter(enumval='D')
        self.assertEqual(agg(qs), None)


class MakeSegments_TestCase(base.CeleryManagement_DBTestCaseBase):
    fixtures = ['test_segmentize']
    
    def test_basic(self):
        from celerymanagementapp.segmentize import make_segments, Segmentizer
        from celerymanagementapp.segmentize import basic_query_sequence
        from celerymanagementapp.segmentize import avg_aggregator
        
        seq_fieldname = 'enumval'
        agg_fieldname = 'floatval'
        labels = ['A','B','C','D']
        
        qs = TestModel.objects.all()
        
        segmentizer = Segmentizer( basic_query_sequence(seq_fieldname, labels) )
        aggregator = avg_aggregator(agg_fieldname)
        segs = make_segments(qs, segmentizer, aggregator)
        
        self.assertEquals(len(segs), 4)
        
        self.assertEquals(segs[0], ('A',5.0))
        self.assertEquals(segs[1], ('B',4.0))
        self.assertEquals(segs[2], ('C',88.))
        self.assertEquals(segs[3], ('D',None))
        
    def test_daterange(self):
        from celerymanagementapp.segmentize import make_segments, Segmentizer
        from celerymanagementapp.segmentize import range_query_sequence
        from celerymanagementapp.segmentize import count_aggregator
        d = datetime.date
        
        seq_fieldname = 'date'
        range = (d(2010,1,1),d(2010,1,25))
        interval_size = datetime.timedelta(days=5)
        
        qs = TestModel.objects.all()
        
        segmentizer = Segmentizer( range_query_sequence(seq_fieldname, range, interval_size) )
        aggregator = count_aggregator()
        segs = make_segments(qs, segmentizer, aggregator)
        
        self.assertEquals(len(segs), 5)
        
        self.assertEquals(segs[0], (d(2010,1,3),  2))
        self.assertEquals(segs[1], (d(2010,1,8),  0))
        self.assertEquals(segs[2], (d(2010,1,13), 2))
        self.assertEquals(segs[3], (d(2010,1,18), 1))
        self.assertEquals(segs[4], (d(2010,1,23), 1))
        
        
        
        
        


