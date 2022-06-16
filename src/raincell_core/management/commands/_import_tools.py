import netCDF4
import datetime
import os

from django.contrib.gis.geos import Point
from django.db import transaction
from django.db import IntegrityError

from raincell_core.models import Cell, RainRecord
from raincell_core.utils import latlon_to_cellid


# @transaction.atomic
def import_mask_file(file_path):
    # TODO: Should be defined in the projet's settings, to ensure consistency between separate runs
    coordinates_decimals = os.environ.get('RAINCELL_COORDINATES_ROUND_DECIMALS', '5')
    coordinates_decimals = int(coordinates_decimals)
    nc = netCDF4.Dataset(file_path, "r", format="netCDF4")
    counter = 0
    for ilon in range(nc.variables['lon'].size):
        for ilat in range(nc.variables['lat'].size):
            # print("{},{}".format(ilon, ilat))
            # print(nc.variables['mask'][ilat, ilon])
            lat = nc.variables['lat'][ilat].item()
            lon = nc.variables['lon'][ilon].item()
            # Round the lat/lon coordinates. Gets a cleaner output, since a few coords have bad rounding
            # (e.g. 12.50000000001) which might cause some grid cells overlapping in the VT rendering
            lat = round(lat, coordinates_decimals)
            lon = round(lon, coordinates_decimals)
            if nc.variables['mask'][ilat, ilon].item() > 0:
                # Generate a Cell point in the DB
                cell_id_from_coords = latlon_to_cellid(lat, lon, coordinates_decimals)
                location = Point(lon, lat)
                cell_exists = Cell.objects.filter(id__exact=cell_id_from_coords).count()
                if not cell_exists:
                    # no existing cell => we create one
                    try:
                        rec = Cell.objects.create(
                            id=cell_id_from_coords,
                            location=location,
                        )
                    except (IntegrityError):
                        print(
                            "ERR: non-unique relationship between geog coordinates and cell_id. You might need to increase the value of the RAINCELL_COORDINATES_ROUND_DECIMALS env. variable")
                        raise
                counter += 1
    return counter


@transaction.atomic
def import_file(file_path, verbose=False):
    coordinates_decimals = os.environ.get('RAINCELL_COORDINATES_ROUND_DECIMALS', '5')
    coordinates_decimals = int(coordinates_decimals)

    nc = netCDF4.Dataset(file_path, "r", format="netCDF4")
    mask = list(Cell.objects.all().values('id'))
    mask_ids = [o['id'] for o in mask]
    # ds = xr.open_dataset(file_path)
    # df = ds.to_dataframe()
    counter = 0
    for ilon in range(nc.variables['longitude'].size):
        for ilat in range(nc.variables['latitude'].size):
            # print("{},{}".format(ilon, ilat))
            # print(nc_mask.variables['mask'][ilat, ilon])
            lat = nc.variables['latitude'][ilat].item()
            lon = nc.variables['longitude'][ilon].item()
            # Compute the cell_id from lat/lon
            cell_id_from_coords = latlon_to_cellid(lat, lon, coordinates_decimals)
            if cell_id_from_coords in mask_ids:
                if verbose:
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
                recs = RainRecord.objects.filter(cell_id__exact=cell_id_from_coords,
                                                 recorded_day=file_day_date,
                                                 )
                rec = recs.first()
                if rec is None:  # queryset was empty
                    rec = RainRecord(
                        cell_id=cell_id_from_coords,
                        recorded_day=file_day_date,
                    )
                rec.quantile25[file_time] = nc.variables['Rainfall'][0, ilat, ilon].item()
                rec.quantile50[file_time] = nc.variables['Rainfall'][1, ilat, ilon].item()
                rec.quantile75[file_time] = nc.variables['Rainfall'][2, ilat, ilon].item()
                rec.save()
                counter += 1
    return counter
