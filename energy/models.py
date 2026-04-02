from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class EnergyUsage(models.Model):
    building_name = models.CharField(max_length=100)
    units_consumed = models.FloatField(validators=[MinValueValidator(0.0)])
    month = models.DateField()
    carbon_emission = models.FloatField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Assuming emission factor of 0.82 kg CO2 per unit (kWh)
        if self.units_consumed is not None:
            self.carbon_emission = self.units_consumed * 0.82
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.building_name} - {self.month.strftime('%Y-%m')}"
