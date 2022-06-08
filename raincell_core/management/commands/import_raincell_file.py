from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.gis.geos import Point
from raincell_core.models import CellRecord

import netCDF4
import xarray as xr
import re
import datetime
import os
import statistics
from time import perf_counter

class Command(BaseCommand):
    help = 'Import a netcdf data file into the DB (1 file/datetime at a time)'

    def add_arguments(self, parser):
        parser.add_argument('file_path')
        parser.add_argument('mask_path')

    # @transaction.atomic
    def handle(self, *args, **kwargs):
        start_time = perf_counter()
        file_path = kwargs['file_path']
        mask_path = kwargs['mask_path']
        # for poll_id in options['poll_ids']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)
        #
        #     poll.opened = False
        #     poll.save()
        #
        #     self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
        nc = netCDF4.Dataset(file_path, "r", format="netCDF4")
        nc_mask = netCDF4.Dataset(mask_path, "r", format="netCDF4")
        # ds = xr.open_dataset(file_path)
        # df = ds.to_dataframe()
        counter = 0
        for ilon in range(nc.variables['longitude'].size):
            for ilat in range(nc.variables['latitude'].size):
                # print("{},{}".format(ilon, ilat))
                # print(nc_mask.variables['mask'][ilat, ilon])
                if nc_mask.variables['mask'][ilat, ilon].item() > 0:
                    print("Coordinates: {} (lon) / {} (lat): {},{},{}".
                        format(
                            nc.variables['longitude'][ilon].item(),
                            nc.variables['latitude'][ilat].item(),
                            nc.variables['Rainfall'][0, ilat, ilon].item(),
                            nc.variables['Rainfall'][1, ilat, ilon].item(),
                            nc.variables['Rainfall'][2, ilat, ilon].item()
                        )
                    )
                    filename = os.path.basename(file_path)
                    file_day = filename.split('_')[0]
                    file_day_date = datetime.datetime.strptime(file_day, "%Y%m%d").date()
                    file_time = filename.split('_')[1]
                    location = Point(nc.variables['latitude'][ilat].item(), nc.variables['longitude'][ilon].item())
                    recs = CellRecord.objects.filter(location__equals=location,
                                                    day__year=file_day[0:4],
                                                    day__month=file_day[4:6],
                                                    day__day=file_day[6:8],
                                                    )
                    rec = recs.first()
                    if rec is None: # queryset was empty
                        rec = CellRecord.objects.create(location=location,
                                                  day=file_day_date,
                                                  )
                    rec.quantile25[file_time] = nc.variables['Rainfall'][0, ilat, ilon].item()
                    rec.quantile50[file_time] = nc.variables['Rainfall'][1, ilat, ilon].item()
                    rec.quantile75[file_time] = nc.variables['Rainfall'][2, ilat, ilon].item()
                    rec.daily_mean = statistics.mean(rec.quantile50.values())
                    rec.save()
                    counter += 1

        self.stdout.write(self.style.SUCCESS('Processed {} records for date {}/{}'.format(counter, file_day, file_time)))
        end_time = perf_counter()
        self.stdout.write(self.style.SUCCESS('Elapsed time: {}'.format(end_time - start_time)))

    def _add_15m_record(self, quantiles_tuple, location, filename):
        """
        Utility to handle adding a new record (15m raincell dataset) to the CellRecord
        Knowing that the CellRecord stores quantiles values as dayly array of values, you have to be careful
        to where and how you introduce the data
        The day and time are extracted from the file name (we could get it from the data,
        but the frequency would be less consistent)
        :param quantiles_tuple: A 3-tuple of the quantile 25, 50 , 75 values
        :param location: django.contrib.gis.geos import Point from lat/lon
        :param filename:
        :return: the cell record
        """
        # Get cellRecord at that point and day if it exists
        file_day = re.search("^\d+", filename)[0]
        if len(file_day) is not 8:
            print("Error extracting day from filename")
        file_day_date = datetime.datetime.strptime(file_day, "%Y%m%d").date()

        file_time = filename.split('_')[1]
        rec = CellRecord.objects.filter(location__equals = location,
                                        day__year = file_day[0:4],
                                        day__month = file_day[4:6],
                                        day__day = file_day[6:8],
                                        )
        if rec is None:
            CellRecord.objects.create(location=location,
                                      day = file_day_date,
                                      quantile25 = '{}',
                                      quantile50 = '{}',
                                      quantile75 = '{}',
                                      )

