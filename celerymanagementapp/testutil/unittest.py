import sys as sys

if ((sys.version_info[0] == 2 and sys.version_info[1] < 7) or 
   (sys.version_info[0] == 3 and sys.version_info[1] < 2)):
    try:
        import unittest2 as unittest
    except ImportError:
        msg =  'The test_celery subpackage requires the unittest2 package '
        msg += 'or Python 2.7+ or Python 3.2+.'
        print '*** {0} ***'.format(msg)
        raise
else:
    import unittest

__all__ = ['unittest',]
