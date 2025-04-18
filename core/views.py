# core/views.py
from django.db.models import Count, Avg, Sum, F, Q, FloatField, Case, When, Value
from django.db.models import Min, Max, OuterRef, Subquery
from django.db.models.functions import Coalesce
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle

from .models import Department, Employee, Attendance, Performance, Salary
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, AttendanceSerializer,
    PerformanceSerializer, SalarySerializer, DepartmentAnalyticsSerializer,
    EmployeeAttendanceAnalyticsSerializer, PerformanceTrendSerializer,
    SalaryGrowthSerializer
)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['name', 'location']
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'location']

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        departments = Department.objects.annotate(
            employee_count=Count('employees', distinct=True),
            average_salary=Coalesce(
                Avg('employees__salaries__amount', filter=Q(
                    employees__salaries__effective_date=F('employees__salaries__employee__salaries__effective_date')
                )),
                0,
                output_field=FloatField()
            )
        )
        serializer = DepartmentAnalyticsSerializer(departments, many=True)
        return Response(serializer.data)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'position']
    ordering_fields = ['first_name', 'last_name', 'hire_date']

    @action(detail=True, methods=['get'])
    def attendance_analytics(self, request, pk=None):
        employee = self.get_object()
        analytics = Employee.objects.filter(id=employee.id).annotate(
            present_count=Count('attendances', filter=Q(attendances__status='present')),
            absent_count=Count('attendances', filter=Q(attendances__status='absent')),
            late_count=Count('attendances', filter=Q(attendances__status='late')),
            total_days=Count('attendances'),
            attendance_rate=Coalesce(
                Count('attendances', filter=Q(attendances__status='present')) * 100.0 /
                Count('attendances'),
                0,
                output_field=FloatField()
            )
        ).first()

        serializer = EmployeeAttendanceAnalyticsSerializer(analytics)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def performance_trend(self, request, pk=None):
        employee = self.get_object()
        trend = Employee.objects.filter(id=employee.id).annotate(
            average_rating=Coalesce(Avg('performances__rating'), 0, output_field=FloatField()),
            goals_met_count=Count('performances', filter=Q(performances__goals_met=True)),
            total_reviews=Count('performances')
        ).first()

        serializer = PerformanceTrendSerializer(trend)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def salary_growth(self, request, pk=None):
        employee = self.get_object()

        # Get initial and current salary
        initial_salary = Salary.objects.filter(employee=employee).order_by('effective_date').first()
        current_salary = Salary.objects.filter(employee=employee).order_by('-effective_date').first()

        if initial_salary and current_salary:
            growth = Employee.objects.filter(id=employee.id).annotate(
                initial_salary=Value(initial_salary.amount),
                current_salary=Value(current_salary.amount),
                growth_percentage=(
                        (Value(current_salary.amount) - Value(initial_salary.amount)) * 100.0 /
                        Value(initial_salary.amount)
                ),
                total_bonus=Coalesce(Sum('salaries__bonus'), 0)
            ).first()

            serializer = SalaryGrowthSerializer(growth)
            return Response(serializer.data)
        else:
            return Response({"error": "Salary data not available"}, status=404)


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'date', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'notes']
    ordering_fields = ['date', 'status']

    @action(detail=False, methods=['get'])
    def status_summary(self, request):
        summary = Attendance.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')

        return Response(summary)

    @action(detail=False, methods=['get'])
    def department_attendance(self, request):
        department_id = request.query_params.get('department')

        if not department_id:
            return Response({"error": "Department ID is required"}, status=400)

        summary = Attendance.objects.filter(
            employee__department_id=department_id
        ).values('status').annotate(
            count=Count('id')
        ).order_by('status')

        return Response(summary)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'review_date', 'rating', 'goals_met']
    search_fields = ['employee__first_name', 'employee__last_name', 'comments']
    ordering_fields = ['review_date', 'rating']

    @action(detail=False, methods=['get'])
    def rating_distribution(self, request):
        distribution = Performance.objects.values('rating').annotate(
            count=Count('id')
        ).order_by('rating')

        return Response(distribution)

    @action(detail=False, methods=['get'])
    def department_performance(self, request):
        department_id = request.query_params.get('department')

        if not department_id:
            return Response({"error": "Department ID is required"}, status=400)

        performance = Performance.objects.filter(
            employee__department_id=department_id
        ).values('employee__department__name').annotate(
            average_rating=Avg('rating'),
            goals_met_percentage=Count(
                Case(When(goals_met=True, then=1))
            ) * 100.0 / Count('id'),
            review_count=Count('id')
        )

        return Response(performance)


class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'effective_date', 'salary_type']
    search_fields = ['employee__first_name', 'employee__last_name', 'notes']
    ordering_fields = ['effective_date', 'amount']

    @action(detail=False, methods=['get'])
    def salary_stats(self, request):
        stats = {
            'average_salary': Salary.objects.filter(
                id__in=Subquery(
                    Salary.objects.filter(employee=OuterRef('employee'))
                    .order_by('-effective_date')
                    .values('id')[:1]
                )
            ).aggregate(avg=Avg('amount'))['avg'],
            'min_salary': Salary.objects.filter(
                id__in=Subquery(
                    Salary.objects.filter(employee=OuterRef('employee'))
                    .order_by('-effective_date')
                    .values('id')[:1]
                )
            ).aggregate(min=Min('amount'))['min'],
            'max_salary': Salary.objects.filter(
                id__in=Subquery(
                    Salary.objects.filter(employee=OuterRef('employee'))
                    .order_by('-effective_date')
                    .values('id')[:1]
                )
            ).aggregate(max=Max('amount'))['max'],
            'total_bonus_paid': Salary.objects.aggregate(total=Sum('bonus'))['total']
        }

        return Response(stats)

    @action(detail=False, methods=['get'])
    def department_salaries(self, request):
        department_id = request.query_params.get('department')

        if not department_id:
            return Response({"error": "Department ID is required"}, status=400)

        dept_salaries = Salary.objects.filter(
            employee__department_id=department_id,
            id__in=Subquery(
                Salary.objects.filter(employee=OuterRef('employee'))
                .order_by('-effective_date')
                .values('id')[:1]
            )
        ).values('employee__department__name').annotate(
            average_salary=Avg('amount'),
            total_employees=Count('employee', distinct=True),
            total_bonus=Sum('bonus')
        )

        return Response(dept_salaries)