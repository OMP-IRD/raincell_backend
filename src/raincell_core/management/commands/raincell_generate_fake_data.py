import datetime
import random

from django.core.management.base import BaseCommand

from time import perf_counter

from raincell_core.models import Cell, AtomicRainRecord
from raincell_core.utils import roundit


class Command(BaseCommand):
    help = 'Generate fake data over a period of days. Ex. manage.py raincell_generate_fake_data 2022-05-01 2022-06-30'

    def add_arguments(self, parser):
        parser.add_argument('from_date')
        parser.add_argument('to_date')

        parser.add_argument(
            '--overwrite_existing',
            action='store_true',
            help='Overwrite existing data records. Default to False',
        )
        parser.add_argument(
            '--cell_ids',
            help='Generate only for this comma-separated list of ids',
        )
        parser.set_defaults(overwrite_existing=False)
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='More verbose output',
        )

    def handle(self, *args, **kwargs):
        start_time = perf_counter()

        from_date = kwargs['from_date']
        to_date = kwargs['to_date']
        verbose = kwargs.get('verbose', False)
        overwrite = kwargs.get('overwrite_existing', False)
        cells_list = kwargs.get('cell_ids', '')

        mask = list(Cell.objects.all().values('id'))
        mask_ids = [o['id'] for o in mask]

        list_of_cellids = cells_list.split(',') if cells_list else mask_ids

        # Create full TZ-aware datetime objects
        # start = datetime.datetime.strptime(from_date + " 00:10", "%Y-%m-%d  %H:%M")
        start = datetime.datetime.fromisoformat(from_date + 'T00:10:00+00:00')
        # end = datetime.datetime.strptime(to_date + " 23:55", "%Y-%m-%d  %H:%M")
        end   = datetime.datetime.fromisoformat(to_date + "T23:55:00+00:00")
        counter = 0
        d = start
        while d <= end:
            for id in list_of_cellids:
                recs = AtomicRainRecord.objects.filter(cell_id__exact=id, recorded_time=d)
                rec = recs.first()
                q50 = roundit(abs(random.gauss(2,2)))
                if rec is None:  # queryset was empty
                    rec = AtomicRainRecord(
                        cell_id = id,
                        recorded_time = d,
                        quantile25 = roundit(max(0, q50 - abs(random.gauss(2,2)/20))),
                        quantile50 = q50,
                        quantile75 = roundit(q50 + abs(random.gauss(2,2)/20)),
                        is_fake = True,
                    )
                elif overwrite:
                    rec.quantile25 = roundit(max(0, q50 - abs(random.gauss(2,2)/20)))
                    rec.quantile50 = q50
                    rec.quantile75 = roundit(q50 + abs(random.gauss(2,2)/20))
                    rec.is_fake = True
                rec.save()
            if verbose:
                print("Created fake data for day {}".format(d))
            counter += 1
            # increment the date
            d += datetime.timedelta(minutes=15)

        end_time = perf_counter()
        self.stdout.write(self.style.SUCCESS('Generated fake data for {} days in {} seconds'.format(counter, end_time - start_time)))
