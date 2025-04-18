# Employee Analytics API

A Django REST Framework based web application that generates synthetic employee data, stores it in PostgreSQL, and provides REST API endpoints for analytical summaries and data visualization.

## Features

- Synthetic employee data generation
- PostgreSQL database integration
- RESTful API with filtering, pagination, and throttling
- Interactive API documentation with Swagger UI
- Data visualization endpoints
- Authentication
- Docker and Docker Compose support
- Health check endpoint

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker and Docker Compose (optional)

### Installation

#### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/employee-analytics.git
   cd employee-analytics
   ```

2. Start the application with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. The application will be available at: http://localhost:8000/

#### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/amanrjgit/employee-analytics.git
   cd employee-analytics
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL:
   - Create a database named `employee_db`
   - Update `.env` file with your database credentials

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Generate sample data:
   ```bash
   python manage.py generate_data --employees 5 --departments 3
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. The application will be available at: http://localhost:8000/

## API Documentation

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## API Endpoints

### Authentication

- Login: `/api-auth/login/`
- Logout: `/api-auth/logout/`

### Core Endpoints

- Departments: `/api/departments/`
- Employees: `/api/employees/`
- Attendance: `/api/attendance/`
- Performance: `/api/performance/`
- Salaries: `/api/salaries/`

### Analytics Endpoints

- Department Analytics: `/api/departments/analytics/`
- Employee Attendance Analytics: `/api/employees/{id}/attendance_analytics/`
- Employee Performance Trend: `/api/employees/{id}/performance_trend/`
- Employee Salary Growth: `/api/employees/{id}/salary_growth/`
- Attendance Status Summary: `/api/attendance/status_summary/`
- Department Attendance: `/api/attendance/department_attendance/?department={id}`
- Performance Rating Distribution: `/api/performance/rating_distribution/`
- Department Performance: `/api/performance/department_performance/?department={id}`
- Salary Statistics: `/api/salaries/salary_stats/`
- Department Salaries: `/api/salaries/department_salaries/?department={id}`

### Health Check

- Health Status: `/health/`

## Design Decisions

- **Django REST Framework**: Chosen for its robust feature set for building RESTful APIs quickly.
- **PostgreSQL**: Selected for its reliability, performance, and advanced features.
- **Faker**: Used for generating realistic synthetic employee data.
- **Docker**: Implemented for easy setup and deployment.
- **Swagger UI**: Integrated for interactive API documentation and testing.

## Architecture

- **Models**: Core database models for Employee, Department, Attendance, Performance, and Salary data.
- **Serializers**: Transforms model instances into JSON representations.
- **ViewSets**: Handles API requests and responses with Django REST Framework.
- **Analytics**: Custom endpoints for aggregated data and visualizations.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License.