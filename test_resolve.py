import os
import django
from django.urls import resolve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ssc_ms.settings')
django.setup()

paths = ['/api/energy/', '/api/energy/1/']
for path in paths:
    try:
        match = resolve(path)
        print(f"Path: {path}")
        print(f"  View Name: {match.view_name}")
        print(f"  Url Name: {match.url_name}")
        print(f"  App Name: {match.app_name}")
        print(f"  Namespace: {match.namespace}")
        print(f"  Func: {match.func}")
    except Exception as e:
        print(f"Path: {path} - Error: {e}")
