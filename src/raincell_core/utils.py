
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