from rest_framework import serializers
from .models import WasteRecord

class WasteRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteRecord
        fields = '__all__'
        read_only_fields = ('created_by',)
