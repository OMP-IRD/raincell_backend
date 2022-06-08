from django.core.management.base import BaseCommand, CommandError

from . import _import_tools

import glob
from os import environ
from time import perf_counter

class Command(BaseCommand):
    help = 'Recursively batch import raincell netcdf files'

    def add_arguments(self, parser):
        parser.add_argument('folder_path')

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
        global_start_time = perf_counter()

        folder_path = kwargs['folder_path']
        verbose = kwargs.get('verbose', False)

        # get mask path value. Best practice would be to use environ variable. But allow also as argument
        mask_path = kwargs.get('mask_path') or environ.get('RAINCELL_NETCDF_MASK_PATH')
        if not mask_path:
            raise CommandError("Path to mask file should be defined. Either use the env. var `RAINCELL_NETCDF_MASK_PATH` of the command option `mask_path`")

        files_counter = 0
        for file_path in glob.iglob(folder_path + '**/20*.nc', recursive=True):
            start_time = perf_counter()
            print(file_path)
            files_counter += 1
            counter = _import_tools.import_file(file_path, mask_path, verbose)
            end_time = perf_counter()
            self.stdout.write(self.style.SUCCESS('{} processed in {} seconds ({} records) '.format(file_path, end_time - start_time, counter)))

        global_end_time = perf_counter()
        self.stdout.write(self.style.SUCCESS('Elapsed time: {}'.format(global_end_time - global_start_time)))
        self.stdout.write(self.style.SUCCESS('Processed files: {}'.format(files_counter)))
