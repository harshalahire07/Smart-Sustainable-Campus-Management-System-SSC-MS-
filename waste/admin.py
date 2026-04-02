from django.contrib import admin
from .models import WasteRecord

@admin.register(WasteRecord)
class WasteRecordAdmin(admin.ModelAdmin):
    list_display = ('waste_type', 'quantity_kg', 'date', 'created_by')
    list_filter = ('waste_type', 'date', 'created_by')
    search_fields = ('waste_type',)
