from django.contrib import admin
from .models import WaterUsage

@admin.register(WaterUsage)
class WaterUsageAdmin(admin.ModelAdmin):
    list_display = ('building_name', 'litres_consumed', 'date', 'created_by')
    list_filter = ('date', 'building_name', 'created_by')
    search_fields = ('building_name',)
