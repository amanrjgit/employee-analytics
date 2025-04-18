# core/tests.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date, timedelta

from .models import Department, Employee, Attendance, Performance, Salary


class ModelTests(TestCase):
    def setUp(self):
        # Create department
        self.department = Department.objects.create(
            name="Engineering",
            location="San Francisco"
        )

        # Create employee
        self.employee = Employee.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="555-1234",
            hire_date=date.today() - timedelta(days=365),
            position="Developer",
            department=self.department
        )

        # Set department manager
        self.department.manager = self.employee
        self.department.save()

    def test_department_creation(self):
        self.assertEqual(self.department.name, "Engineering")
        self.assertEqual(self.department.location, "San Francisco")
        self.assertEqual(self.department.manager, self.employee)

    def test_employee_creation(self):
        self.assertEqual(self.employee.full_name, "John Doe")
        self.assertEqual(self.employee.department, self.department)
        self.assertTrue(self.employee.is_active)

    def test_employee_attendance(self):
        attendance = Attendance.objects.create(
            employee=self.employee,
            date=date.today(),
            clock_in="09:00:00",
            clock_out="17:00:00",
            status="present"
        )
        self.assertEqual(attendance.employee, self.employee)
        self.assertEqual(attendance.status, "present")


class APITests(TestCase):
    def setUp(self):
        # Create a user for authentication
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Create API client
        self.client = APIClient()

        # Create department
        self.department = Department.objects.create(
            name="Engineering",
            location="San Francisco"
        )

        # Create employee
        self.employee = Employee.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="555-1234",
            hire_date=date.today() - timedelta(days=365),
            position="Developer",
            department=self.department
        )

    def test_api_authentication(self):
        # Try to access without authentication
        response = self.client.get(reverse('department-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Authenticate
        self.client.force_authenticate(user=self.user)

        # Try again with authentication
        response = self.client.get(reverse('department-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_employee_list(self):
        # Authenticate
        self.client.force_authenticate(user=self.user)

        # Get employee list
        response = self.client.get(reverse('employee-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['first_name'], "John")

    def test_department_analytics(self):
        # Authenticate
        self.client.force_authenticate(user=self.user)

        # Get department analytics
        response = self.client.get(reverse('department-analytics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check there's data for our department
        department_data = next(
            (d for d in response.data if d['name'] == "Engineering"),
            None
        )
        self.assertIsNotNone(department_data)
        self.assertEqual(department_data['employee_count'], 1)