# core/admin.py
from django.contrib import admin
from .models import Department, Employee, Attendance, Performance, Salary

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'manager')
    search_fields = ('name', 'location')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'position', 'department', 'is_active')
    list_filter = ('is_active', 'department', 'hire_date')
    search_fields = ('first_name', 'last_name', 'email', 'position')
    date_hierarchy = 'hire_date'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'clock_in', 'clock_out')
    list_filter = ('status', 'date')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'date'

@admin.register(Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'review_date', 'rating', 'goals_met', 'reviewer')
    list_filter = ('rating', 'goals_met', 'review_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'comments')
    date_hierarchy = 'review_date'

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'amount', 'bonus', 'effective_date', 'salary_type')
    list_filter = ('salary_type', 'effective_date')
    search_fields = ('employee__first_name', 'employee__last_name')
    date_hierarchy = 'effective_date'