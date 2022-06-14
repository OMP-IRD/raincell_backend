from django.contrib.gis.db import models
from django.db.models import JSONField
import statistics

from .utils import latlon_to_cellid


def json_empty_default():
    return {}


class Cell(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    # geographical position
    location = models.PointField()
    class Meta:
        verbose_name = 'Geographical cell ("pixel")'
        constraints = [
            models.UniqueConstraint(fields=["location"], name="unique_location"),
        ]
        indexes = [
            models.Index(fields=['location']),
            models.Index(fields=['id']),
        ]

    def save(self, *args, **kwargs):
        self.id = latlon_to_cellid(self.location.y, self.location.x)
        super().save(*args, **kwargs)  # Call the "real" save() method.


class RainRecord(models.Model):
    cell_id = models.CharField(max_length=16, unique_for_date="recorded_day")
    recorded_day = models.DateField("Day")
    quantile25 = JSONField("Quantile25", null=True, default=json_empty_default)
    quantile50 = JSONField("Quantile50", null=True, default=json_empty_default, help_text="This is the value we will use")
    quantile75 = JSONField("Quantile75", null=True, default=json_empty_default)
    daily_mean = models.FloatField("Daily Mean", null=True, blank=True, help_text="to be computed, based on quantile50 values")

    class Meta:
        verbose_name = 'Rain record: 1 rain record per cell and per day'
        constraints = [
            models.UniqueConstraint(fields=["cell_id", "recorded_day"], name="rainrecord_unique_cellid_day"),
        ]
        indexes = [
            models.Index(fields=['-recorded_day']),
            models.Index(fields=['cell_id', '-recorded_day']),
        ]

    def save(self, *args, **kwargs):
        if self.quantile50.values():
            self.daily_mean = statistics.mean(self.quantile50.values())
        super().save(*args, **kwargs)  # Call the "real" save() method.

