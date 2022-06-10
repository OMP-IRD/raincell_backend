from time import perf_counter

from django.core.management.base import BaseCommand

from ._import_tools import import_mask_file


class Command(BaseCommand):
    help = 'Load the geographic cells from the netcdf mask file'

    def add_arguments(self, parser):
        parser.add_argument('file_path')

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='More verbose output',
        )

    def handle(self, *args, **kwargs):
        start_time = perf_counter()

        file_path = kwargs['file_path']
        verbose = kwargs.get('verbose', False)

        counter = import_mask_file(file_path)

        end_time = perf_counter()
        self.stdout.write(self.style.SUCCESS('{} processed in {} seconds ({} records) '.format(file_path, end_time - start_time, counter)))

