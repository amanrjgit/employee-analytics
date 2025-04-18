# core/management/commands/generate_data.py
import random
from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from core.models import Department, Employee, Attendance, Performance, Salary


class Command(BaseCommand):
    help = 'Generate synthetic employee data'

    def add_arguments(self, parser):
        parser.add_argument('--employees', type=int, default=5, help='Number of employees to generate')
        parser.add_argument('--departments', type=int, default=3, help='Number of departments to generate')
        parser.add_argument('--attendance_days', type=int, default=30, help='Number of attendance days to generate')
        parser.add_argument('--clear', action='store_true', help='Clear existing data before generation')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Salary.objects.all().delete()
            Performance.objects.all().delete()
            Attendance.objects.all().delete()
            Employee.objects.all().delete()
            Department.objects.all().delete()

        fake = Faker()
        num_employees = options['employees']
        num_departments = options['departments']
        attendance_days = options['attendance_days']

        # Create departments
        self.stdout.write('Creating departments...')
        departments = []
        department_names = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'IT']
        locations = ['New York', 'San Francisco', 'Chicago', 'Austin', 'Seattle', 'Boston', 'Denver']

        for i in range(min(num_departments, len(department_names))):
            department = Department.objects.create(
                name=department_names[i],
                location=random.choice(locations)
            )
            departments.append(department)
            self.stdout.write(f'Created department: {department.name}')

        # Create employees
        self.stdout.write('Creating employees...')
        employees = []
        positions = ['Manager', 'Developer', 'Designer', 'Analyst', 'Specialist', 'Coordinator', 'Director']

        for i in range(num_employees):
            first_name = fake.first_name()
            last_name = fake.last_name()
            department = random.choice(departments)

            employee = Employee.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}@example.com",
                phone_number=fake.phone_number(),
                hire_date=fake.date_between(start_date='-5y', end_date='today'),
                position=random.choice(positions),
                department=department,
                is_active=random.random() > 0.1,  # 90% active
            )
            employees.append(employee)
            self.stdout.write(f'Created employee: {employee.full_name}')

        # Set department managers
        for department in departments:
            department_employees = [e for e in employees if e.department == department]
            if department_employees:
                manager = random.choice(department_employees)
                department.manager = manager
                department.save()
                self.stdout.write(f'Set {manager.full_name} as manager of {department.name}')

        # Create attendance records
        self.stdout.write('Creating attendance records...')
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=attendance_days)
        current_date = start_date

        while current_date <= end_date:
            # Skip weekends
            if current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
                current_date += timedelta(days=1)
                continue

            for employee in employees:
                # Randomize attendance status
                status_weights = {
                    'present': 0.8,  # 80% present
                    'absent': 0.1,  # 10% absent
                    'late': 0.05,  # 5% late
                    'half_day': 0.03,  # 3% half-day
                    'leave': 0.02,  # 2% leave
                }
                status = random.choices(
                    list(status_weights.keys()),
                    weights=list(status_weights.values())
                )[0]

                clock_in = None
                clock_out = None

                if status in ['present', 'late']:
                    base_clock_in = time(9, 0)  # 9:00 AM
                    base_clock_out = time(17, 0)  # 5:00 PM

                    # Adjust clock-in time based on status
                    if status == 'present':
                        hour_variance = random.randint(-1, 1)
                        minute_variance = random.randint(-15, 15)
                    else:  # late
                        hour_variance = random.randint(0, 2)
                        minute_variance = random.randint(15, 45)

                    clock_in_hour = max(7, min(11, base_clock_in.hour + hour_variance))
                    clock_in_minute = max(0, min(59, base_clock_in.minute + minute_variance))
                    clock_in = time(clock_in_hour, clock_in_minute)

                    # Adjust clock-out time
                    hour_variance = random.randint(-1, 2)
                    minute_variance = random.randint(-15, 30)
                    clock_out_hour = max(16, min(20, base_clock_out.hour + hour_variance))
                    clock_out_minute = max(0, min(59, base_clock_out.minute + minute_variance))
                    clock_out = time(clock_out_hour, clock_out_minute)

                elif status == 'half_day':
                    if random.random() > 0.5:  # morning half-day
                        clock_in = time(9, random.randint(0, 30))
                        clock_out = time(13, random.randint(0, 30))
                    else:  # afternoon half-day
                        clock_in = time(13, random.randint(0, 30))
                        clock_out = time(17, random.randint(0, 30))

                Attendance.objects.create(
                    employee=employee,
                    date=current_date,
                    clock_in=clock_in,
                    clock_out=clock_out,
                    status=status,
                    notes=fake.sentence() if random.random() > 0.7 else ''
                )

            current_date += timedelta(days=1)

        self.stdout.write(f'Created attendance records from {start_date} to {end_date}')

        # Create performance reviews
        self.stdout.write('Creating performance reviews...')
        for employee in employees:
            # Create 1-3 performance reviews per employee
            num_reviews = random.randint(1, 3)
            review_dates = sorted([fake.date_between(start_date='-2y', end_date='today') for _ in range(num_reviews)])

            for review_date in review_dates:
                # Avoid self-review
                potential_reviewers = [e for e in employees if e != employee]
                reviewer = random.choice(potential_reviewers) if potential_reviewers else None

                rating = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[0.05, 0.1, 0.2, 0.4, 0.25]  # Weighted towards higher ratings
                )[0]

                goals_met = rating >= 3

                comments = []
                if rating <= 2:
                    comments.append(fake.paragraph(nb_sentences=2, variable_nb_sentences=True))
                    comments.append("Needs significant improvement.")
                elif rating == 3:
                    comments.append(fake.paragraph(nb_sentences=2, variable_nb_sentences=True))
                    comments.append("Meeting expectations but has room for growth.")
                else:
                    comments.append(fake.paragraph(nb_sentences=2, variable_nb_sentences=True))
                    comments.append("Exceeding expectations in most areas.")

                Performance.objects.create(
                    employee=employee,
                    review_date=review_date,
                    reviewer=reviewer,
                    rating=rating,
                    comments="\n".join(comments),
                    goals_met=goals_met,
                    improvement_areas=fake.paragraph(nb_sentences=3) if rating < 5 else "",
                    strengths=fake.paragraph(nb_sentences=3)
                )

            self.stdout.write(f'Created {num_reviews} performance reviews for {employee.full_name}')

        # Create salary records
        self.stdout.write('Creating salary records...')
        for employee in employees:
            # Base salary depends on position
            base_salary = {
                'Manager': random.randint(85000, 120000),
                'Director': random.randint(120000, 170000),
                'Developer': random.randint(70000, 110000),
                'Designer': random.randint(65000, 95000),
                'Analyst': random.randint(60000, 90000),
                'Specialist': random.randint(55000, 85000),
                'Coordinator': random.randint(50000, 70000),
            }.get(employee.position, random.randint(50000, 100000))

            # Create initial salary
            hire_date = employee.hire_date
            initial_salary = base_salary * (0.8 + random.random() * 0.2)  # 80-100% of base salary

            Salary.objects.create(
                employee=employee,
                amount=initial_salary,
                effective_date=hire_date,
                bonus=0,
                salary_type='annual'
            )

            # Create salary increases (0-3 per employee)
            num_increases = random.randint(0, 3)
            last_salary = initial_salary
            last_date = hire_date

            for i in range(num_increases):
                # Increase effective date (6-18 months after previous)
                months_after = random.randint(6, 18)
                effective_date = last_date.replace(year=last_date.year + (last_date.month + months_after) // 12,
                                                   month=((last_date.month + months_after) % 12) or 12,
                                                   day=min(last_date.day, 28))

                # Stop if effective date is in the future
                if effective_date > datetime.now().date():
                    break

                # Calculate increase (3-15%)
                increase_percentage = 0.03 + random.random() * 0.12
                new_salary = last_salary * (1 + increase_percentage)

                # Calculate bonus (0-20% of salary)
                bonus_percentage = random.random() * 0.2
                bonus = last_salary * bonus_percentage

                Salary.objects.create(
                    employee=employee,
                    amount=new_salary,
                    effective_date=effective_date,
                    bonus=bonus,
                    salary_type='annual',
                    notes=f"{increase_percentage:.1%} increase from previous salary"
                )

                last_salary = new_salary
                last_date = effective_date

            self.stdout.write(f'Created {num_increases + 1} salary records for {employee.full_name}')

        self.stdout.write(self.style.SUCCESS('Successfully generated employee data'))