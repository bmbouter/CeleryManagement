import sys

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from djcelery.app import app
from celery.bin import celeryev


class CmEvCommand(celeryev.EvCommand):
    def run_evcam(self, *args, **kwargs):
        from celerymanagementapp.camera import evcam
        self.set_process_status("cam")
        kwargs["app"] = self.app
        return evcam(*args, **kwargs)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        )
    
    args = '<...>'
    help = 'todo...'
    
    def handle(self, *args, **options):
        options['camera'] = 'celerymanagementapp.camera.Camera'
        ev = CmEvCommand(app=app)
        ev.run(*args, **options)


