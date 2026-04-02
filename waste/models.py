from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class WasteRecord(models.Model):
    class WasteType(models.TextChoices):
        DRY = 'DRY', 'Dry'
        WET = 'WET', 'Wet'
        PLASTIC = 'PLASTIC', 'Plastic'
        E_WASTE = 'E_WASTE', 'E-waste'

    waste_type = models.CharField(max_length=20, choices=WasteType.choices)
    quantity_kg = models.FloatField(validators=[MinValueValidator(0.0)])
    date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_waste_type_display()} - {self.quantity_kg}kg ({self.date})"
