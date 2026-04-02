from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse
import csv
from .models import EnergyUsage
from .serializers import EnergyUsageSerializer
from accounts.permissions import IsAdminOrStaffReadOnlyCreate


class EnergyUsageViewSet(viewsets.ModelViewSet):
    serializer_class = EnergyUsageSerializer
    permission_classes = [IsAdminOrStaffReadOnlyCreate]

    def get_queryset(self):
        qs = EnergyUsage.objects.all().order_by('-month', '-id')
        # Optional date filtering via query params
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        building = self.request.query_params.get('building')
        month_filter = self.request.query_params.get('month_filter')
        if month_filter:
            qs = qs.filter(month__startswith=month_filter)
        if date_from:
            qs = qs.filter(month__gte=date_from)
        if date_to:
            qs = qs.filter(month__lte=date_to)
        if building:
            qs = qs.filter(building_name__icontains=building)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="energy_records.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Building Name', 'Units Consumed (kWh)', 'Carbon Emitted (kg)', 'Month', 'Created By', 'Created At'])
        for obj in queryset:
            writer.writerow([
                obj.id, obj.building_name, obj.units_consumed, obj.carbon_emission, 
                obj.month.strftime('%Y-%m'), obj.created_by.username if obj.created_by else '',
            ])
        return response
