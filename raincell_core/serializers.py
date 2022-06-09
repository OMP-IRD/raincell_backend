from rest_framework import serializers

from .models import CellRecord

class CellRecordDailyValueSerializer(serializers.ModelSerializer):
   class Meta:
        model = CellRecord
        fields = ['recorded_day', 'daily_mean']