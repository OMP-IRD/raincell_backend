from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('api/v1/raincell/', views.api_root),
    path('api/v1/raincell/records/<lat>/<lon>', views.CellRecordsList.as_view(), name="get-records"),
]

urlpatterns = format_suffix_patterns(urlpatterns)