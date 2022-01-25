from django.core.management import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Print values of test settings.'

    def handle(self, *args, **options):
        for k in dir(settings):
            if k.startswith('TEST_SETTING_'):
                self.stdout.write(f'{k} = {getattr(settings, k)}')
