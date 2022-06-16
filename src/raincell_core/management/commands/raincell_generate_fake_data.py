import datetime
import random

from django.core.management.base import BaseCommand

from time import perf_counter

from raincell_core.models import Cell, RainRecord
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

        mask = list(Cell.objects.all().values('id'))
        mask_ids = [o['id'] for o in mask]

        start = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(to_date, "%Y-%m-%d").date()
        dates_list = [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]
        times_list = ["{}{}".format(str(a).zfill(2), b) for a in range(0,23) for b in [10, 25, 40, 55]]

        counter = 0
        for d in dates_list:
            for id in mask_ids:
                quantile50_values_list = [ roundit(abs(random.gauss(2,2))) for i in range (96)]
                quantile75_values_list = [ roundit(q + abs(random.gauss(2,2)/20)) for q in quantile50_values_list ]
                quantile25_values_list = [ roundit(max(0, q - abs(random.gauss(2,2)/20))) for q in quantile50_values_list ]
                recs = RainRecord.objects.filter(cell_id__exact=id,
                                                 recorded_day=d,
                                                 )
                rec = recs.first()
                if rec is None:  # queryset was empty
                    rec = RainRecord(
                        cell_id = id,
                        recorded_day = d,
                        quantile25 = dict(zip(times_list, quantile25_values_list)),
                        quantile50 = dict(zip(times_list, quantile50_values_list)),
                        quantile75 = dict(zip(times_list, quantile75_values_list)),
                        is_fake = True,
                    )
                    rec.save()
                elif overwrite:
                    rec.quantile25 = dict(zip(times_list, quantile25_values_list))
                    rec.quantile50 = dict(zip(times_list, quantile50_values_list))
                    rec.quantile75 = dict(zip(times_list, quantile75_values_list))
                    rec.is_fake = True
            if verbose:
                print("Created fake data for day {}".format(d))
            counter += 1

        end_time = perf_counter()
        self.stdout.write(self.style.SUCCESS('Generated fake data for {} days in {} seconds'.format(counter, end_time - start_time)))
