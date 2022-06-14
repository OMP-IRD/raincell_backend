from django.core.management.base import BaseCommand, CommandError

from . import _import_tools

from os import environ
from time import perf_counter

class Command(BaseCommand):
    help = 'Import a netcdf data file into the DB (1 file/datetime at a time)'

    def add_arguments(self, parser):
        parser.add_argument('file_path')

        # Named (optional) arguments
        parser.add_argument(
            '--mask_path',
            help='Provide the path to the mask file (alternative is to define it in RAINCELL_NETCDF_MASK_PATH env. var',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='More verbose output',
        )

    def handle(self, *args, **kwargs):
        start_time = perf_counter()

        file_path = kwargs['file_path']
        verbose = kwargs.get('verbose', False)

        counter = _import_tools.import_file(file_path, verbose)

        end_time = perf_counter()
        self.stdout.write(self.style.SUCCESS('{} processed in {} seconds ({} records) '.format(file_path, end_time - start_time, counter)))
