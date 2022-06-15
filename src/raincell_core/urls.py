from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('api/v1/raincell/', views.api_root),
    path('api/v1/raincell/cells/', views.CellsList.as_view(), name="get-cells-list"),
    re_path(r'^api/v1/raincell/cells/(?P<lat>\d+\.\d+)/(?P<lon>\d+\.\d+)/data/(?P<mode>all|daily)$', views.CellDailyRecordsByCoordinates.as_view(), name="get-records-by-coordinates"),
    re_path(r'^api/v1/raincell/cells/(?P<cell_id>[0-9]{16})/data/(?P<mode>all|daily)$', views.CellDailyRecordsById.as_view(), name="get-records-by-id"),
    path('api/schema/', SpectacularAPIView.as_view(), name='openapi-schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='openapi-schema'), name='swagger-ui'),
    # path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns = format_suffix_patterns(urlpatterns)