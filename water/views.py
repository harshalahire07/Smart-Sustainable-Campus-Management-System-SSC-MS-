from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse
import csv
from .models import WaterUsage
from .serializers import WaterUsageSerializer
from accounts.permissions import IsAdminOrStaffReadOnlyCreate


class WaterUsageViewSet(viewsets.ModelViewSet):
    serializer_class = WaterUsageSerializer
    permission_classes = [IsAdminOrStaffReadOnlyCreate]

    def get_queryset(self):
        qs = WaterUsage.objects.all().order_by('-date', '-id')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        building = self.request.query_params.get('building')
        month_filter = self.request.query_params.get('month_filter')
        if month_filter:
            qs = qs.filter(date__startswith=month_filter)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if building:
            qs = qs.filter(building_name__icontains=building)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="water_records.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Building Name', 'Litres Consumed', 'Date', 'Created By'])
        for obj in queryset:
            writer.writerow([
                obj.id, obj.building_name, obj.litres_consumed, obj.date.strftime('%Y-%m-%d'), 
                obj.created_by.username if obj.created_by else '',
            ])
        return response
