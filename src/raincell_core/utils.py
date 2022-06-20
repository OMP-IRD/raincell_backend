import datetime

from django.conf import settings


def latlon_to_cellid(lat, lon, max_decimals=5):
    """
    Generate an identifier (string) based on latitude/longitude (EPSG:4326)
    We add 90 deg. so that we don't have to deal with negative values. Same idea for longitude
    :param lat:
    :param lon:
    :return: a string identifier. the first 3 digits are the latitude integer value +90, padded with zeros.
    The 5 next digits are the decimal part of the latitude. The next digits deal with longitude in the same way
    """
    # We add 90 deg. so that we don't have to deal with negative values. Same idea for longitude
    lat = lat+90
    lon = lon+180

    rlat = round(lat, max_decimals)
    rlon = round(lon, max_decimals)

    if lat != rlat or lon != rlon:
        print("WARN: we are trimming the number of decimals, identifier might uniquely identify this set of coordinates. You might want to augment the max_decimals argument")


    lat_parts=str(rlat).split('.')
    lon_parts=str(rlon).split('.')

    # Using the Python format mini-language (https://docs.python.org/2/library/string.html#format-specification-mini-language)
    cell_id = '{latl:0>3}{latr:0<{nb_dec}}{lonl:0>3}{lonr:0<{nb_dec}}'.format(latl=lat_parts[0],
                                                                              latr=lat_parts[1],
                                                                              lonl=lon_parts[0],
                                                                              lonr=lon_parts[1],
                                                                              nb_dec=max_decimals)
    return cell_id


def roundit(value):
    """
    Rounds value to the number of decimals given by the RAINCELL_SETTINGS.RECORD_DECIMALS django setting
    :param value:
    :return:
    """
    return round(value, settings.RAINCELL_SETTINGS.get('RECORD_DECIMALS', 2))


def date_from_filename(filename):
    """
    Get a netcdf raincell file name, and extract the datetime out of it
    :param filename: (string)
    :return: datetime object
    """
    dt_string = filename.split('_')[0] + "" + filename.split('_')[1]
    dt = datetime.datetime.strptime(dt_string, "%Y%m%d %H%M")
    return dt