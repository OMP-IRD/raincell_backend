from django.contrib.gis.geos import Point
from raincell_core.models import CellRecord
from django.db import transaction

import netCDF4
import datetime
import os


@transaction.atomic
def import_file(file_path, mask_path, verbose=False):
    coordinates_decimals = os.environ.get('RAINCELL_COORDINATES_ROUND_DECIMALS')

    nc = netCDF4.Dataset(file_path, "r", format="netCDF4")
    nc_mask = netCDF4.Dataset(mask_path, "r", format="netCDF4")
    # ds = xr.open_dataset(file_path)
    # df = ds.to_dataframe()
    counter = 0
    for ilon in range(nc.variables['longitude'].size):
        for ilat in range(nc.variables['latitude'].size):
            # print("{},{}".format(ilon, ilat))
            # print(nc_mask.variables['mask'][ilat, ilon])
            lat = nc.variables['latitude'][ilat].item()
            lon = nc.variables['longitude'][ilon].item()
            if coordinates_decimals:
                lat = round(lat, int(coordinates_decimals))
                lon = round(lon, int(coordinates_decimals))
            if nc_mask.variables['mask'][ilat, ilon].item() > 0:
                if (verbose):
                    print("Coordinates: {} (lon) / {} (lat): {},{},{}".
                        format(
                            lat,
                            lon,
                            nc.variables['Rainfall'][0, ilat, ilon].item(),
                            nc.variables['Rainfall'][1, ilat, ilon].item(),
                            nc.variables['Rainfall'][2, ilat, ilon].item()
                        )
                    )
                filename = os.path.basename(file_path)
                file_day = filename.split('_')[0]
                file_day_date = datetime.datetime.strptime(file_day, "%Y%m%d").date()
                file_time = filename.split('_')[1]
                location = Point(lon, lat)
                recs = CellRecord.objects.filter(location__equals=location,
                                                 recorded_day=file_day_date,
                                                 # day__year=file_day[0:4],
                                                 # day__month=file_day[4:6],
                                                 # day__day=file_day[6:8],
                                                 )
                rec = recs.first()
                if rec is None:  # queryset was empty
                    rec = CellRecord.objects.create(location=location,
                                                    recorded_day=file_day_date,
                                                    )
                rec.quantile25[file_time] = nc.variables['Rainfall'][0, ilat, ilon].item()
                rec.quantile50[file_time] = nc.variables['Rainfall'][1, ilat, ilon].item()
                rec.quantile75[file_time] = nc.variables['Rainfall'][2, ilat, ilon].item()
                rec.save()
                counter += 1
    return counter