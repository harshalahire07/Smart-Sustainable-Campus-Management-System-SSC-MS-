import os
import django
from django.urls import get_resolver, URLPattern, URLResolver

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssc_ms.settings')
django.setup()

def show_urls(patterns, prefix=''):
    for pattern in patterns:
        if isinstance(pattern, URLResolver):
            show_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        elif isinstance(pattern, URLPattern):
            print(f"{prefix}{str(pattern.pattern)}")

show_urls(get_resolver().url_patterns)
