from django.db.models import Sum
from django.db.models.functions import TruncMonth

def calculate_sustainability_score(total_carbon, waste_total):
    """Calculate the overall sustainability score based on penalties."""
    score = 100.0 - (total_carbon * 0.0001 + waste_total * 0.0005)
    return max(0.0, min(100.0, score))

def get_sustainability_status(score):
    """Return a simple Sustainability Status based on the score."""
    if score >= 75:
        return 'Green (Good)'
    elif score >= 40:
        return 'Yellow (Moderate)'
    else:
        return 'Red (Poor)'

def get_monthly_trends(queryset, date_field, value_field):
    """Group queryset by month and sum the specified value_field."""
    trends = list(
        queryset.annotate(month_trunc=TruncMonth(date_field))
        .values('month_trunc')
        .annotate(total=Sum(value_field))
        .order_by('month_trunc')
    )
    for t in trends:
        if t['month_trunc']:
            t['month_trunc'] = t['month_trunc'].strftime('%Y-%m')
        t['total'] = float(t['total'] or 0)
    return trends
