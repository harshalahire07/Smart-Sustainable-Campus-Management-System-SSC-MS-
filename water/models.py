from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class WaterUsage(models.Model):
    building_name = models.CharField(max_length=100)
    litres_consumed = models.FloatField(validators=[MinValueValidator(0.0)])
    date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.building_name} - {self.date}"
