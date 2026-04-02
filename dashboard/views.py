from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from energy.models import EnergyUsage
from water.models import WaterUsage
from waste.models import WasteRecord
from .utils import calculate_sustainability_score, get_sustainability_status, get_monthly_trends


def dashboard_view(request):
    return render(request, 'dashboard.html')


def sdg_goals_view(request):
    return render(request, 'sdg_goals.html')


def records_energy_view(request):
    return render(request, 'records_energy.html')


def records_water_view(request):
    return render(request, 'records_water.html')


def records_waste_view(request):
    return render(request, 'records_waste.html')


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month_filter = request.query_params.get('month_filter')
        
        energy_qs = EnergyUsage.objects.all()
        water_qs = WaterUsage.objects.all()
        waste_qs_raw = WasteRecord.objects.all()
        
        if month_filter:
            energy_qs = energy_qs.filter(month__startswith=month_filter)
            water_qs = water_qs.filter(date__startswith=month_filter)
            waste_qs_raw = waste_qs_raw.filter(date__startswith=month_filter)

        total_energy = energy_qs.aggregate(total=Sum('units_consumed'))['total'] or 0.0
        total_carbon = energy_qs.aggregate(total=Sum('carbon_emission'))['total'] or 0.0
        total_water = water_qs.aggregate(total=Sum('litres_consumed'))['total'] or 0.0

        waste_qs = waste_qs_raw.values('waste_type').annotate(total_kg=Sum('quantity_kg'))
        waste_by_type = {item['waste_type']: float(item['total_kg'] or 0) for item in waste_qs}
        waste_total = sum(waste_by_type.values())

        energy_trend = get_monthly_trends(energy_qs, 'month', 'units_consumed')
        water_trend = get_monthly_trends(water_qs, 'date', 'litres_consumed')

        sustainability_score = calculate_sustainability_score(total_carbon, waste_total)
        sustainability_status = get_sustainability_status(sustainability_score)

        # Building breakdown — top buildings by energy consumption
        building_data = list(
            energy_qs.values('building_name')
            .annotate(
                total_energy=Sum('units_consumed'),
                total_carbon=Sum('carbon_emission')
            )
            .order_by('-total_energy')[:10]
        )
        for b in building_data:
            b['total_energy'] = float(b['total_energy'] or 0)
            b['total_carbon'] = float(b['total_carbon'] or 0)

        # Recent activity — latest records from all modules, filtered by month
        recent_activity = []
        now = timezone.now()

        for rec in energy_qs.order_by('-id')[:5]:
            recent_activity.append({
                'type': 'energy',
                'building': rec.building_name,
                'description': f'{rec.units_consumed} kWh consumed in {rec.month.strftime("%b %Y")}',
                'time_ago': _time_ago(rec.month, now),
                'sort_key': rec.id
            })

        for rec in water_qs.order_by('-id')[:5]:
            recent_activity.append({
                'type': 'water',
                'building': rec.building_name,
                'description': f'{rec.litres_consumed} litres consumed on {rec.date.strftime("%b %d, %Y")}',
                'time_ago': _time_ago(rec.date, now),
                'sort_key': rec.id
            })

        for rec in waste_qs_raw.order_by('-id')[:5]:
            recent_activity.append({
                'type': 'waste',
                'waste_type': rec.get_waste_type_display(),
                'description': f'{rec.quantity_kg} kg of {rec.get_waste_type_display()} waste on {rec.date.strftime("%b %d, %Y")}',
                'time_ago': _time_ago(rec.date, now),
                'sort_key': rec.id
            })

        recent_activity.sort(key=lambda x: x['sort_key'], reverse=True)
        for a in recent_activity:
            a.pop('sort_key', None)

        return Response({
            "total_energy_consumption": total_energy,
            "total_carbon_emission": round(total_carbon, 2),
            "total_water_usage": total_water,
            "waste_by_type": waste_by_type,
            "sustainability_score": round(sustainability_score, 2),
            "sustainability_status": sustainability_status,
            "trends": {
                "energy": energy_trend,
                "water": water_trend
            },
            "building_breakdown": building_data,
            "recent_activity": recent_activity[:10]
        })


def _time_ago(date_val, now):
    """Generate a simple time-ago string from a date."""
    try:
        if hasattr(date_val, 'date'):
            diff = now.date() - date_val.date()
        else:
            diff = now.date() - date_val
        days = diff.days
        if days == 0:
            return 'Today'
        elif days == 1:
            return 'Yesterday'
        elif days < 7:
            return f'{days} days ago'
        elif days < 30:
            weeks = days // 7
            return f'{weeks} week{"s" if weeks > 1 else ""} ago'
        elif days < 365:
            months = days // 30
            return f'{months} month{"s" if months > 1 else ""} ago'
        else:
            return f'{days // 365} year{"s" if days // 365 > 1 else ""} ago'
    except Exception:
        return ''
