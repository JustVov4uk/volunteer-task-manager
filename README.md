# 🧩 Volunteer Task Manager

**Volunteer Task Manager** is a Django-based web application for managing coordinators, volunteers, and tasks.  
Coordinators can create and assign tasks, while volunteers can complete them and submit reports.

---

## 🚀 Features

### 👥 User Roles

- **Coordinator (superuser or user with coordinator rights):**
  - Creates and manages other coordinators and volunteers.  
  - Creates, updates, and deletes **tasks**, **categories**, and **tags**.  
  - Assigns tasks and sets deadlines.  
  - Reviews and manages **volunteer reports** — can approve, edit, or delete them.

- **Volunteer:**
  - Views assigned tasks.  
  - Submits reports upon task completion.  
  - Has a personal statistics page with their own task overview.

### 📊 Statistics
- Global task statistics: completed, active, in progress, paused.  
- Personal task statistics for each volunteer.

### ✉️ Email Notifications
- Automatic email alerts to volunteers when:
  - A new task is assigned.  
  - Their report is approved or edited.

### ✅ Tests
- Full test coverage (~160 tests).  
- Includes model, view, template, and email logic testing.

---

## 🛠️ Tech Stack

- **Python 3.12**  
- **Django 5**  
- **SQLite**  
- **Bootstrap 5**  
- **Django ORM**  
- **unittest**  
- **SMTP email backend**

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/volunteer-task-manager.git
cd volunteer-task-manager
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Environment Variables Example

Create a `.env` file in the project root.  
Below is an example of required variables (do not commit real credentials to GitHub):

```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Email configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_app_password

```

> For Gmail, create an **App Password** in your Google Account and use it instead of your real password.

---

## 🧾 Test Accounts

**Coordinator (admin):**  
- Login: `administrator`  
- Password: `Me262VoV`

**Volunteer:**  
- Login: `vol_tanya`  
- Password: `GoodPass123!`

> These are example accounts for testing only.  
> Use your own credentials when deploying or testing locally.

---

## 📸 Screenshots

> Screenshots of all pages are located in `/screenshots/`  
> (Home, Login, Task list, Task detail, Reports, Statistics, etc.)

---

## 🧩 Project Structure

```
volunteer_task_manager/
│ manage.py
│ requirements.txt
│ .env.example
├── volunteer_task_manager/    # Main Django configuration
├── static/                    # Static files
├── tasks/                     # Tasks models, views, forms, mixins
├── media/                     # Media files
├── templates/                 # HTML templates
└── tests/                     # Test files
```

---

## 🧠 Author

**Volodymyr [JustVov4uk] Budzan**  
Email: [volodabudzan4@gmail.com]  
LinkedIn: [https://www.linkedin.com/in/volodymyr-budzan-22582b292/]

---

## 🧩 Additional Notes

- Commit after each major change (new model, view, or template).  
- Keep commit names descriptive (e.g., `Add Task model`, `Implement report approval view`).  
- Before merging `develop` → `main`, make sure:
  - All tests pass.  
  - The code follows PEP8 formatting.  
  - The README and screenshots are up to date.  
  - Database diagram (draw.io) is included if models changed.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).