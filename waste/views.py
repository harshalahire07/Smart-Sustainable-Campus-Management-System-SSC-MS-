from rest_framework import viewsets
from rest_framework.decorators import action
from django.http import HttpResponse
import csv
from .models import WasteRecord
from .serializers import WasteRecordSerializer
from accounts.permissions import IsAdminOrStaffReadOnlyCreate


class WasteRecordViewSet(viewsets.ModelViewSet):
    serializer_class = WasteRecordSerializer
    permission_classes = [IsAdminOrStaffReadOnlyCreate]

    def get_queryset(self):
        qs = WasteRecord.objects.all().order_by('-date', '-id')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        waste_type = self.request.query_params.get('waste_type')
        month_filter = self.request.query_params.get('month_filter')
        if month_filter:
            qs = qs.filter(date__startswith=month_filter)
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)
        if waste_type:
            qs = qs.filter(waste_type=waste_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="waste_records.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Waste Type', 'Quantity (kg)', 'Date', 'Created By'])
        for obj in queryset:
            writer.writerow([
                obj.id, obj.get_waste_type_display(), obj.quantity_kg, obj.date.strftime('%Y-%m-%d'), 
                obj.created_by.username if obj.created_by else '',
            ])
        return response
