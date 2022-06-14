from datetime import date, timedelta

from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from django.contrib.gis.geos import Point
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from .serializers import CellsSerializer, RainRecordSerializer
from .models import RainRecord, Cell


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'cells': reverse('get-cells-list', request=request, format=format),
    })


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 10000


class CellsList(generics.ListAPIView):
    """
    Get Raincell cells ("pixels") list
    """
    serializer_class = CellsSerializer
    pagination_class = LargeResultsSetPagination
    queryset = Cell.objects.raw('SELECT id, ST_X(location) AS lon, ST_Y(location) AS lat FROM raincell_core_cell')


def get_records_daily_mode(cell_id, ref_date, duration):
    """
    Extract daily data (daily mean) for given cell
    :param cell_id:
    :param ref_date: this is the most recent date to be collected
    :param duration: (days). This is counted backwards. E.g, if ref_date is '2021-10-04' and duration=365, it will
    retrieve the data from 2020-10-05 to 2021-10-04. Defaults 365 days
    :return: a dict ready to serialize, see format_daily_rain_records function
    """
    if not duration:
        duration = 365
    else:
        duration = int(duration)
    from_date = ref_date - timedelta(days=duration)

    # Get data from DB
    records = RainRecord.objects.filter(cell_id__exact=cell_id,
                                     recorded_day__gt=from_date,
                                     recorded_day__lte=ref_date,
                                     ).order_by('recorded_day')

    # Generate a simpler object structure for output
    rain_record = {
        'cell_id': '',
        'data': [],
        'message': '',
    }
    if len(records) == 0:
        rain_record['message'] = 'no data found'
        return rain_record

    for rec in records:
        if not rain_record['cell_id']:
            rain_record['cell_id'] = rec.cell_id
        rain_record['data'].append({
            'day': rec.recorded_day,
            'daily_mean': rec.daily_mean
        })
    return rain_record


def get_records_full_mode(cell_id, ref_date, duration):
    """
    Extract full data (every 15 minutes) for given cell
    :param cell_id:
    :param ref_date: this is the most recent date to be collected
    :param duration: (days). This is counted backwards. E.g, if ref_date is '2021-10-04' and duration=2, it will
    retrieve the data from 2021-10-02 same time to 2021-10-04 (covers 48h, meaning 48*4 values)
    :return: a dict ready to serialize, see format_daily_rain_records function
    """
    if not duration:
        duration = 2
    else:
        duration = int(duration)
    from_date = ref_date - timedelta(days=duration)

    # Get data from DB
    records = RainRecord.objects.filter(cell_id__exact=cell_id,
                                     recorded_day__gte=from_date,
                                     recorded_day__lte=ref_date,
                                     ).order_by('recorded_day')

    # Generate a simpler object structure for output
    rain_record = {
        'cell_id': cell_id,
        'data': [],
        'message': '',
    }
    if len(records) == 0:
        rain_record['message'] = 'no data found'
        return rain_record

    # Retrieve the latest time available
    # Make sure the records are sorted in the proper order (should be)
    sorted_records = sorted(records, key=lambda o: o.recorded_day)
    latest_time = list(sorted_records[-1].quantile50.keys())[-1]
    oldest_day = from_date

    for rec in records:
        for time in sorted(rec.quantile50.keys()):
            if (rec.recorded_day > oldest_day) or time > latest_time:
                rain_record['data'].append({
                    'day': rec.recorded_day,
                    'time': time,
                    'quantile50': rec.quantile50[time],
                    'uncertainty': rec.quantile50[time] - rec.quantile25[time]
                })
            # else:
            #     print("Max time is {}, discarding {}/{}".format(latest_time, oldest_day, time))
    return rain_record


class CellDailyRecordsById(generics.GenericAPIView):
    """
    Get Raincell records
    """

    @extend_schema(
        # extra parameters added to the schema
        parameters=[
            OpenApiParameter("cell_id", required=True, type=str, location=OpenApiParameter.PATH,
                                 description="Cell identifier, as can be found on /api/v1/raincell/cells/",
                                 examples=[
                                     OpenApiExample(name= 'Cell at (lat=4.025, lon=9.15)' ,value='0940250018915000'),
                                     OpenApiExample(name= 'Cell at (lat=4.625, lon=9.425)',value='0946250018942500'),
                                 ],
                             ),
            OpenApiParameter("mode", required=True, type=str, location=OpenApiParameter.PATH,
                                enum=['all', 'daily'], default="all",
                                description="The records have a granularity of 15 min. By default ('all' mode), it fetches the full data serie. If set to 'daily', it will only retrieve the daily mean (1 value per day)",
                             ),
            OpenApiParameter(name='date_ref',
                             description='The last date to show (format yyyy-mm-dd), e.g. 2021-10-04. Defaults to current day. ',
                             required=False, type=str, default=date.today()),
            OpenApiParameter(name='duration', description='Duration time to extract, in days', required=False,
                             type=int, default=2),
        ],
    )
    def get(self, request, cell_id, mode, format=None):
        ref_date = request.query_params.get('date_ref')
        if not ref_date:
            ref_date = date.today()
        else:
            ref_date = date.fromisoformat(ref_date)
        duration = request.query_params.get('duration')
        if mode == "all":
            rain_record = get_records_full_mode(cell_id, ref_date, duration)
        elif mode == "daily":
            rain_record = get_records_daily_mode(cell_id, ref_date, duration)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = RainRecordSerializer(rain_record, many=False)
        return Response(serializer.data)


class CellDailyRecordsByCoordinates(generics.GenericAPIView):
    """
    Get Raincell records on given lat/lon coordinates
    """
    @extend_schema(
        # extra parameters added to the schema
        parameters=[
            OpenApiParameter("lat", required=True, type=str, location=OpenApiParameter.PATH,
                                 description="Latitude",
                                 examples=[
                                     OpenApiExample(name= '4.025', value= '4.025'),
                                     OpenApiExample(name= '4.625', value= '4.625'),
                                 ],
                             ),
            OpenApiParameter("lon", required=True, type=str, location=OpenApiParameter.PATH,
                                 description="Longitude",
                                 examples=[
                                     OpenApiExample(name= '9.15', value= '9.15'),
                                     OpenApiExample(name= '9.425', value= '9.425'),
                                 ],
                             ),
            OpenApiParameter("mode", required=True, type=str, location=OpenApiParameter.PATH,
                                enum=['all', 'daily'], default="all",
                                description="The records have a granularity of 15 min. By default ('all' mode), it fetches the full data serie. If set to 'daily', it will only retrieve the daily mean (1 value per day)",
                             ),
            OpenApiParameter(name='date_ref',
                             description='The last date to show (format yyyy-mm-dd), e.g. 2021-10-04. Defaults to current day. ',
                             required=False, type=str, default=date.today()),
            OpenApiParameter(name='duration', description='Duration time to extract, in days', required=False,
                             type=int, default=2),
        ],
    )
    def get(self, request, lat, lon, mode, format=None):
        lon = float(lon)
        lat = float(lat)
        side = 0.025
        poly = Point(lon, lat).buffer(0.025 / 2).envelope
        today = date.today()
        last_year = today - timedelta(days=365)
        cells = Cell.objects.filter(location__intersects=poly)
        target_cell = cells.first()
        if not target_cell:
            # means no cell at these coordinates
            return Response(status=status.HTTP_404_NOT_FOUND)
        cell_id = target_cell.id

        ref_date = request.query_params.get('date_ref')
        if not ref_date:
            ref_date = date.today()
        else:
            ref_date = date.fromisoformat(ref_date)
        duration = request.query_params.get('duration')
        if mode == "all":
            rain_record = get_records_full_mode(cell_id, ref_date, duration)
        elif mode == "daily":
            rain_record = get_records_daily_mode(cell_id, ref_date, duration)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = RainRecordSerializer(rain_record, many=False)
        return Response(serializer.data)
