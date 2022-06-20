from rest_framework import serializers

from raincell_core.models import AtomicRainRecord

class CellsSerializer(serializers.Serializer):
    id = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()


class RainRecordSerializer(serializers.Serializer):
    # Custom serializers that won't be tied to a model
    # cf https://stackoverflow.com/questions/45532965/django-rest-framework-serializer-without-a-model
    cell_id = serializers.CharField()
    data = serializers.JSONField()
    message = serializers.CharField()


class AtomicRainRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AtomicRainRecord
        fields = ['cell_id', 'recorded_time', 'quantile25', 'quantile50', 'quantile75']
