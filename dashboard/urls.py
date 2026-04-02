from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('sdg-goals/', views.sdg_goals_view, name='sdg_goals'),
    path('records/energy/', views.records_energy_view, name='records_energy'),
    path('records/water/', views.records_water_view, name='records_water'),
    path('records/waste/', views.records_waste_view, name='records_waste'),
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='dashboard_api'),
]
