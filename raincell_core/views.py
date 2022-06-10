from django.shortcuts import render
from rest_framework import views
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from rest_framework.reverse import reverse
from django.contrib.gis.geos import Point,Polygon
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from datetime import date, timedelta

from .serializers import CellRecordDailyValueSerializer, CellsSerializer
from .models import CellRecord


# @api_view(['GET'])
# def records_list_lastyear(request, lat, lon, format=None):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     lon = float(lon)
#     lat = float(lat)
#     side = 0.025
#     if request.method == 'GET':
#         poly = Point(lon, lat).buffer(0.025/2).envelope
#         today = date.today()
#         last_year = today - timedelta(days=365)
#         recs = CellRecord.objects.filter(location__intersects=poly,
#                                          recorded_day__gte=last_year,
#                                          recorded_day__lte=today,
#                                          ).order_by('-recorded_day')
#         serializer = CellRecordDailyValueSerializer(recs, many=True)
#         return Response(serializer.data)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'cells': reverse('get-cells-list', request=request, format=format),
    })

def format_daily_cell_records(records):
    cell_record = {
        'cell_id': '',
        'lat': None,
        'lon': None,
        'data': []
    }
    for rec in records:
        if not cell_record['cell_id']:
            cell_record['cell_id'] = rec.cell_id
            cell_record['lat'] = rec.location.y
            cell_record['lon'] = rec.location.x
        cell_record['data'].append({
            'day': rec.recorded_day,
            'daily_mean': rec.daily_mean
        })
    return cell_record



class CellsList(generics.ListAPIView):
    """
    Get Raincell cells ("pixels") list
    """
    serializer_class = CellsSerializer
    queryset = CellRecord.objects.raw('SELECT DISTINCT id, cell_id, ST_X(location) AS lon, ST_Y(location) AS lat FROM raincell_core_cellrecord WHERE recorded_day IN (SELECT Max(recorded_day) FROM raincell_core_cellrecord)')
    # def get_queryset(self):
    #     """
    #     This view should return a list of all the purchases
    #     for the currently authenticated user.
    #     """
    #     recs = CellRecord.objects.raw('SELECT DISTINCT id, cell_id, location FROM raincell_core_cellrecord')
    #     return recs




class CellDailyRecordsById(generics.GenericAPIView):
    """
    Get Raincell records
    """
    @extend_schema(
        # extra parameters added to the schema
        parameters=[
            OpenApiParameter(name='duration', description='Duration time to extract, in days', required=False, type=int),
            OpenApiParameter(name='date_ref',
                             description='The last date to show (format yyyy-mm-dd). Defaults to current day. Ex.: "2022-06-09"',
                             required=False, type=str),
        ],
    )
    def get(self, request, cell_id, format=None):
        ref_date = request.query_params.get('date_ref')
        if not ref_date:
            ref_date = date.today()
        else:
            ref_date = date.fromisoformat(ref_date)
        duration = request.query_params.get('duration')
        if not duration:
            duration = 365
        else:
            duration = int(duration)
        from_date = ref_date - timedelta(days=duration)
        recs = CellRecord.objects.filter(cell_id__exact=cell_id,
                                         recorded_day__gte=from_date,
                                         recorded_day__lte=ref_date,
                                         ).order_by('-recorded_day')
        cell_record = format_daily_cell_records(recs)
        serializer = CellRecordDailyValueSerializer(cell_record, many=False)
        return Response(serializer.data)


class CellDailyRecordsByCoordinates(generics.GenericAPIView):
    """
    Get Raincell records
    """
    def get(self, request, lat, lon, format=None):
        lon = float(lon)
        lat = float(lat)
        side = 0.025
        poly = Point(lon, lat).buffer(0.025 / 2).envelope
        today = date.today()
        last_year = today - timedelta(days=365)
        recs = CellRecord.objects.filter(location__intersects=poly,
                                         recorded_day__gte=last_year,
                                         recorded_day__lte=today,
                                         ).order_by('-recorded_day')
        cell_record = format_daily_cell_records(recs)
        serializer = CellRecordDailyValueSerializer(cell_record, many=False)
        return Response(serializer.data)

# class YearlyRecordsAtPointView(views.APIView):
#     """
#     Get the daily mean, over the last year
#     """
#
#     def get(self, request, lat, lon):
#         # yourdata= [{"likes": 10, "comments": 0}, {"likes": 4, "comments": 23}]
#         yearlydata
#         results = CellRecordDailyValueSerializer(yourdata, many=True).data
#         return Response(results)

# @csrf_exempt
# def records_list_yearly(request, lat, lon, ref_day):
#     """
#     List all code snippets, or create a new snippet.
#     """
#     lon = float(lon)
#     lat = float(lat)
#     side = 0.025
#     if request.method == 'GET':
#         poly = Point(lon, lat).buffer(0.025/2).envelope
#         today = date.today()
#         last_year = today - timedelta(days=365)
#         recs = CellRecord.objects.filter(location__intersects=poly,
#                                          recorded_day__gte=last_year,
#                                          recorded_day__lte=today,
#                                          ).order_by('-recorded_day')
#         serializer = CellRecordDailyValueSerializer(recs, many=True)
#         return JsonResponse(serializer.data, safe=False)
