from rest_framework import serializers
from .models import WaterUsage

class WaterUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaterUsage
        fields = '__all__'
        read_only_fields = ('created_by',)
