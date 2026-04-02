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

def time_ago_str(date_val, now):
    """Generate a simple time-ago string from a date."""
    try:
        if hasattr(date_val, 'date'):
            diff = now.date() - date_val.date()
        else:
            diff = now.date() - date_val
        days = diff.days
        if days <= 0:
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
