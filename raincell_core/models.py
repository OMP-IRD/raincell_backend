from django.contrib.gis.db import models
from django.db.models import JSONField


def json_empty_default():
    return {}

class CellRecord(models.Model):
    recorded_day = models.DateField("Day")
    quantile25 = JSONField("Quantile25", null=True, default=json_empty_default)
    quantile50 = JSONField("Quantile50", null=True, default=json_empty_default, help_text="This is the value we will use")
    quantile75 = JSONField("Quantile75", null=True, default=json_empty_default)
    daily_mean = models.FloatField("Daily Mean", null=True, blank=True, help_text="to be computed, based on quantile50 values")
    # geographical position
    location = models.PointField()

    class Meta:
        verbose_name = 'Cell records: 1 cell record per pixel and per day'
        constraints = [
            models.UniqueConstraint(
                fields=["location", "recorded_day"], name="unique_location_day"
            )
        ]
        indexes = [
            models.Index(fields=['location', '-recorded_day']),
            models.Index(fields=['-recorded_day']),
        ]
