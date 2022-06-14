from django.core.management.base import BaseCommand, CommandError

from . import _import_tools

import glob
from os import environ
from time import perf_counter

class Command(BaseCommand):
    help = 'Recursively batch import raincell netcdf files'

    def add_arguments(self, parser):
        parser.add_argument('folder_path')

        parser.add_argument(
            '--verbose',
            action='store_true',
            help='More verbose output',
        )

    def handle(self, *args, **kwargs):
        global_start_time = perf_counter()

        folder_path = kwargs['folder_path']
        verbose = kwargs.get('verbose', False)

        files_counter = 0
        # TODO: get all files from a same day and commit only once the model
        for file_path in glob.iglob(folder_path + '**/20*.nc', recursive=True):
            start_time = perf_counter()
            print(file_path)
            files_counter += 1
            counter = _import_tools.import_file(file_path, verbose)
            end_time = perf_counter()
            self.stdout.write(self.style.SUCCESS('{} processed in {} seconds ({} records) '.format(file_path, end_time - start_time, counter)))

        global_end_time = perf_counter()
        self.stdout.write(self.style.SUCCESS('Elapsed time: {}'.format(global_end_time - global_start_time)))
        self.stdout.write(self.style.SUCCESS('Processed files: {}'.format(files_counter)))
