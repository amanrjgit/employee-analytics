# core/health_views.py
from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except OperationalError:
        db_status = "unhealthy"

    # Return health status
    return JsonResponse({
        'status': 'healthy',
        'database': db_status,
        'api_version': 'v1'
    })