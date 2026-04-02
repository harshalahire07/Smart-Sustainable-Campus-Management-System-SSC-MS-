from django.contrib import admin
from .models import EnergyUsage

@admin.register(EnergyUsage)
class EnergyUsageAdmin(admin.ModelAdmin):
    list_display = ('building_name', 'units_consumed', 'month', 'carbon_emission', 'created_by')
    list_filter = ('month', 'building_name', 'created_by')
    search_fields = ('building_name',)
