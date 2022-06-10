from rest_framework import serializers


class CellsSerializer(serializers.Serializer):
    id = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()


class CellRecordDailyValueSerializer(serializers.Serializer):
    # Custom serializers that won't be tied to a model
    # cf https://stackoverflow.com/questions/45532965/django-rest-framework-serializer-without-a-model
    cell_id = serializers.CharField()
    lat = serializers.FloatField()
    lon = serializers.FloatField()
    data = serializers.JSONField()
