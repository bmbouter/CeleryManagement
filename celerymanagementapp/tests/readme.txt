Updated: 2010 Oct 27

How to add a test
=================

Test cases are automatically read by the suite() function in __init__.py as 
long as some conditions are met.

    1. The module which contains the test must be imported into __init__.py and 
       also added to the '_testmodules' list.
       
    2. The test case class must derive from base.CeleryManagement_TestCaseBase 
       (directly or indirectly).  This prevents other utility classes from 
       being used as test cases.
       
    3. The name of the test case class must end with: '_TestCase'.  
       For example: 'CalculateThroughput_TestCase'.
       This prevents classes derived from base.CeleryManagement_TestCaseBase 
       from being used as test cases unless specifically desired.  This is 
       useful when you have several test cases with some identical 
       functionality you want to put in a common base class.  This way, this 
       common base class does not need to be loaded as a test case in its own 
       right.
       


Test modules
============

Test cases should be grouped into logical units and placed in modules which 
reflect this grouping.  For instance, put test cases on models in 
tests/models.py.


