from rest_framework import serializers

from .models import CellRecord

class CellRecordDailyValueSerializer(serializers.ModelSerializer):
   class Meta:
        model = CellRecord
        fields = ['cell_id', 'location', 'recorded_day', 'daily_mean']