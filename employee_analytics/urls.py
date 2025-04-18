# employee_analytics/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from core.views import (
    DepartmentViewSet, EmployeeViewSet, AttendanceViewSet,
    PerformanceViewSet, SalaryViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'performance', PerformanceViewSet)
router.register(r'salaries', SalaryViewSet)

# Swagger documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="Employee Analytics API",
        default_version='v1',
        description="API for employee data analysis and visualization",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Health check endpoint
    path('health/', include('core.health_urls')),
]