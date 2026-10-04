# Volunteer Task Manager

Volunteer Task Manager is a Django-based web application for managing coordinators, volunteers, tasks, and volunteer reports.

Coordinators can create and assign tasks, manage categories and tags, review submitted reports, and track general task statistics. Volunteers can view assigned tasks, submit completion reports, and track their own task progress.

## Live Demo

Deployed project:
https://volunteer-task-manager.onrender.com/accounts/login/

## Demo Accounts

Coordinator:

- Login: `administrator1`
- Password: `Me262VoV`

Volunteer:

- Login: `vol_tanya`
- Password: `GoodPass123!`

These accounts are for demo testing only.

## Features

- Role-based access for coordinators and volunteers.
- Task management with categories, tags, statuses, deadlines, and assigned volunteers.
- Volunteer reports with coordinator review and approval flow.
- Global task statistics for coordinators.
- Personal task statistics for volunteers.
- Search and filtering for tasks, volunteers, categories, tags, and reports.
- Pagination for list views.
- Email notifications when a task is assigned or a report is approved.
- Automated tests for models, forms, views, templates, and email-related logic.
- Separate development and production settings.
- Deployment configuration for Render.

## Tech Stack

- Python 3.12
- Django 5.2
- Django ORM
- PostgreSQL for production
- SQLite for local development
- HTML/CSS
- Bootstrap 5
- Crispy Forms
- unittest
- coverage
- SMTP email backend
- Gunicorn
- Whitenoise
- Render
- Git and GitHub

## Project Structure

```text
volunteer-task-manager/
├── docs/                     # Database diagram
├── fixtures/                 # Demo data for local setup
├── static/                   # Source static files
├── tasks/                    # Main app: models, views, forms, notifications
├── templates/                # HTML templates
├── tests/                    # Automated tests
├── volunteer_task_manager/   # Django project settings and URLs
├── build.sh                  # Render build script
├── manage.py
└── requirements.txt
```

## Local Setup

```bash
git clone https://github.com/JustVov4uk/volunteer-task-manager.git
cd volunteer-task-manager
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata fixtures/data.json
python manage.py runserver
```

For Windows:

```bash
venv\Scripts\activate
```

## Environment Variables

Create a `.env` file in the project root. Do not commit real credentials to GitHub.

```env
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_app_password
EMAIL_PORT=587
```

Production deployment uses PostgreSQL environment variables:

```env
POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=your_database_host
POSTGRES_DB_PORT=5432
```

## Tests

```bash
python manage.py test
coverage run manage.py test
coverage report
```

## Deployment

The project is deployed on Render. The `build.sh` script installs dependencies, collects static files, and applies migrations:

```bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

## Author

Volodymyr Budzan

- GitHub: https://github.com/JustVov4uk
- LinkedIn: https://www.linkedin.com/in/volodymyr-budzan-22582b292/
- Email: volodabudzan4@gmail.com
