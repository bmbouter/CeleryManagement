import os
import json
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from celerymanagementapp.taskcontrol import demo_dispatch


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--id',
            action='store',
            type='str',
            dest='id',
            default='',
            help='The demo group id.'),
        make_option('--tmpfile',
            action='store',
            type='str',
            dest='tmpfile',
            default='',
            help='The file containing the json data.  This file will be deleted once the data has been read from it.'),
        )
    
    args = ''
    help = 'Launches several tasks, the results of which can be viewed using CeleryManagement'
    
    def handle(self, *args, **options):
        dispatchid = options['id']
        tmpfile = options['tmpfile']
        if not dispatchid:
            msg = 'A demo group id is required.'
            raise CommandError(msg)
        if not tmpfile:
            msg = 'The name of a tempfile containing the json data is required.'
            raise CommandError(msg)
        
        try:
            f = open(tmpfile, 'rb')
        except IOError as e:
            msg =  'An error occurred while trying to open the tmpfile:\n'
            if e.filename:
                msg += '{0}: {1}'.format(e.strerror, e.filename)
            else:
                msg += '{0}'.format(e.strerror)
            raise CommandError(msg)
            
        rawjson = f.read()
        f.close()
        os.remove(tmpfile)
        
        jsondata = json.loads(rawjson)
        
        taskname = jsondata['name']
        args = jsondata.get('args', [])
        kwargs = jsondata.get('kwargs', {})
        options = jsondata.get('options', {})
        rate = jsondata['rate']
        runfor = jsondata['runfor']
        
        demo_dispatch(taskname, dispatchid, runfor, rate, options, args, kwargs)




