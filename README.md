# 📚 Django Library Management System

A modern and feature-rich **Library Management System** built with **Django** and **MySQL**. This project helps libraries efficiently manage books, members, book issuing/returning, fines, email notifications, and reports through an intuitive admin interface.

---

## 🚀 Features

### 👤 Authentication
- Secure Admin Login
- Logout
- Change Password
- Profile Management
- Profile Photo Upload & Remove

### 📖 Book Management
- Add New Books
- Update Book Details
- Delete Books
- Search Books
- Book Categories
- Book Availability Tracking

### 👥 Member Management
- Add Members
- Update Member Details
- Delete Members
- Member Status Management
- Welcome Email Support

### 🔄 Book Issue & Return
- Issue Books
- Return Books
- Due Date Management
- Late Return Tracking
- Fine Calculation
- Borrowing History

### 💰 Fine Management
- Automatic Fine Calculation
- Fine Reports
- Fine History

### 📧 Email Management
- Email Templates
- Welcome Emails
- Email History
- SMTP Email Configuration

### 🔔 Notifications
- System Notifications
- Due Date Alerts
- Notification History

### 📊 Reports
- Book Reports
- Member Reports
- Issue Reports
- Fine Reports
- CSV Export
- PDF Export

### ⚙️ Settings
- Library Settings
- Fine Settings
- Email Settings

---

# 🛠️ Tech Stack

- Python
- Django
- MySQL
- HTML5
- CSS3
- JavaScript
- Bootstrap
- Git
- GitHub

---

# 📂 Project Structure

```
Library Management System
│
├── accounts/
├── books/
├── members/
├── issue/
├── reports/
├── notifications/
├── templates/
├── static/
├── media/
├── library_management/
├── manage.py
└── requirements.txt
```

---

# ⚡ Installation

### Clone Repository

```bash
git clone https://github.com/RohanJagtap431/django-library-management-system.git
```

### Go to Project

```bash
cd django-library-management-system
```

### Create Virtual Environment

```bash
python -m venv env
```

### Activate Environment

#### Windows

```bash
env\Scripts\activate
```

### Install Requirements

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file and add:

```env
SECRET_KEY=your_secret_key

DEBUG=True

DB_NAME=your_database_name
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### Run Migrations

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Run Server

```bash
python manage.py runserver
```

---

# 📷 Screenshots

> Add screenshots here.

- Login Page
- Dashboard
- Book Management
- Member Management
- Issue Book
- Return Book
- Reports
- Profile

---

# 📌 Future Improvements

- REST API
- QR Code Based Book Issue
- Barcode Scanner
- Student Portal
- Mobile Responsive UI
- Dashboard Analytics
- Docker Support
- Cloud Deployment

---

# 👨‍💻 Author

**Rohan Jagtap**

Backend Developer (Python | Django)

GitHub:
https://github.com/RohanJagtap431

---

# ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub.
