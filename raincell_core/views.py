from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from rest_framework.reverse import reverse
from django.contrib.gis.geos import Point,Polygon
from datetime import date, timedelta

from rest_framework.views import APIView

from .serializers import CellRecordDailyValueSerializer
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
        'records': reverse('get-records', request=request, format=format),
    })

class CellRecordsList(APIView):
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
        serializer = CellRecordDailyValueSerializer(recs, many=True)
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
