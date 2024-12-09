# HR Portal - Employee Management System

A comprehensive HR management system built with Django and Docker, featuring real-time notifications, attendance tracking, and leave management.

## 🚀 Features

### Authentication & Authorization
- Multi-role user system (Admin/Staff)
- Secure login with session management
- Role-based access control
- Protected API endpoints

### Attendance Management
- Automated check-in/check-out system
- Late arrival tracking with configurable thresholds
- Automatic leave deduction for tardiness (10 hours = 1 day)
- Monthly attendance reports
- Detailed attendance records with filtering options

### Leave Management
- Multiple leave types (Annual, Sick, Other)
- Leave request workflow
- Admin approval system
- Leave balance tracking
- Date validation and conflict checking

### Real-time Features
- WebSocket-based notifications
- Instant updates for leave request status
- Real-time attendance tracking
- Unread notification counter

### Dashboard & Reports
- Employee-specific dashboard
- Admin overview dashboard
- Monthly attendance statistics
- Filterable attendance records
- Leave request management interface

## 🛠 Technical Stack

### Backend
- Django 5.1.4
- Django REST Framework
- Channels for WebSocket
- Celery with Redis for async tasks
- PostgreSQL database

### Frontend
- Bootstrap 5
- WebSocket client
- Dynamic form handling
- Real-time updates

### Deployment
- Docker & Docker Compose
- Multi-stage build process
- Environment-based configuration
- Health checks for services

## 🏗 Project Structure
```
hr-portal/
├── apps/
│   ├── accounts/        # User management
│   ├── attendance/      # Attendance & leave tracking
│   ├── dashboard/       # Main interface views
│   └── notifications/   # Real-time notifications
├── core/               # Project settings
├── docker/            # Docker configurations
│   ├── development/
│   └── production/
└── templates/         # HTML templates
```


## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 13+
- Redis 6+

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/your-repo/hr-portal.git
cd hr-portal
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
```

3. Create a `.env` file in the root of the project:

```bash
cp .env.example .env
```

4. Run the development server:

if you want to use pgsql in your local machine, you can use the following command:

```bash
cd docker/development
docker compose -f docker-compose.pgsql.yml up --build -d
```

if you want to use redis in your local machine, you can use the following command:

```bash
cd docker/development
docker compose -f docker-compose.redis.yml up --build -d
```

```bash
python manage.py runserver
```
if you want to use notification service, use this instead of the above command:

```bash
python -m daphne core.asgi:application
```

4.1 Run migrations:

```bash
python manage.py migrate
```

4.2 Create superuser:

```bash
python manage.py createsuperuser
```

4.3 Create fake users:

```bash
python manage.py create_fake_users --20 --staff
```

or 
```bash
cd docker/development
docker compose up --build -d
```
if you want to run the application in the docker container, you can use create a superuser in the container:

```bash
docker exec -it hr-portal python manage.py createsuperuser
```

5. Access the application at `http://localhost:8000`.

6. Run tests:

```bash
python manage.py test
```


## 🔐 Security Features

- CSRF protection
- Session-based authentication
- Role-based access control
- Secure password handling
- Environment variable management

## 📊 API Documentation

### Open the swagger ui at `http://localhost:8000/api/docs/`