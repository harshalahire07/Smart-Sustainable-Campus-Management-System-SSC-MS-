from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WaterUsageViewSet

router = DefaultRouter()
router.register(r'', WaterUsageViewSet, basename='waterusage')

urlpatterns = [
    path('', include(router.urls)),
]
