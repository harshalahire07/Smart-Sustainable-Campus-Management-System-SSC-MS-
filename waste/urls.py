from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WasteRecordViewSet

router = DefaultRouter()
router.register(r'', WasteRecordViewSet, basename='wasterecord')

urlpatterns = [
    path('', include(router.urls)),
]
