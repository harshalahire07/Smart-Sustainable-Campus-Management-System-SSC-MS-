from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EnergyUsageViewSet

router = DefaultRouter()
router.register(r'', EnergyUsageViewSet, basename='energyusage')

urlpatterns = [
    path('', include(router.urls)),
]
