# core/serializers.py
from rest_framework import serializers
from .models import Department, Employee, Attendance, Performance, Salary


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')

    class Meta:
        model = Employee
        fields = '__all__'
        depth = 1


class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')

    class Meta:
        model = Attendance
        fields = '__all__'


class PerformanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')
    reviewer_name = serializers.ReadOnlyField(source='reviewer.full_name')

    class Meta:
        model = Performance
        fields = '__all__'


class SalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.ReadOnlyField(source='employee.full_name')

    class Meta:
        model = Salary
        fields = '__all__'


# Serializers for analytics
class DepartmentAnalyticsSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField()
    average_salary = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Department
        fields = ('id', 'name', 'location', 'employee_count', 'average_salary')


class EmployeeAttendanceAnalyticsSerializer(serializers.ModelSerializer):
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    attendance_rate = serializers.FloatField()

    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'present_count', 'absent_count',
                  'late_count', 'attendance_rate')


class PerformanceTrendSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField()
    goals_met_count = serializers.IntegerField()
    total_reviews = serializers.IntegerField()

    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'average_rating',
                  'goals_met_count', 'total_reviews')


class SalaryGrowthSerializer(serializers.ModelSerializer):
    initial_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_salary = serializers.DecimalField(max_digits=10, decimal_places=2)
    growth_percentage = serializers.FloatField()
    total_bonus = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'initial_salary',
                  'current_salary', 'growth_percentage', 'total_bonus')