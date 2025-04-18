# core/health_urls.py
from django.urls import path
from employee_analytics.health_views import health_check

urlpatterns = [
    path('', health_check, name='health_check'),
]