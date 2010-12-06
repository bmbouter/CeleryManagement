from django.core.management.base import BaseCommand, CommandError
from celerymanagementapp.testutil.testcelery_runner import main

class Command(BaseCommand):
    args = ''
    help = 'Runs tests that require a separate celeryd process.'

    def handle(self, *args, **options):
        main(*args, **options)


