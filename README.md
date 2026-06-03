# 🗳️ asictsvotes - Secure Online Voting System

A full-featured, production-ready online voting platform designed for universities. Supports multiple elections, faculty restrictions, and two-factor authentication.

## ✨ Features

- **🔐 Secure Authentication** – Matric number + password with 30-second OTP via email
- **🗳️ Multiple Elections** – Run university-wide or faculty-restricted elections simultaneously
- **📊 Real-time Results** – Interactive bar charts using Chart.js
- **👨‍💼 Admin Dashboard** – Create elections, add candidates, bulk import students via CSV
- **🌓 Dark Mode** – Toggle between light and dark themes
- **📱 Fully Responsive** – Works on desktop, tablet, and mobile devices
- **🛡️ One Vote Per Election** – Enforced at database level

## 🚀 Tech Stack

- **Backend:** Django 6.0
- **Frontend:** Bootstrap 5, Chart.js
- **Database:** SQLite (development) / PostgreSQL (production ready)
- **Authentication:** Custom user model with OTP via email

## 📋 Prerequisites

- Python 3.13+
- pip
- Git

## 🔧 Installation

 **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/asictsvotes.git
   cd asictsvotes

python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

python manage.py makemigrations voting
python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

Access the application

Student portal: http://127.0.0.1:8000

Admin panel: http://127.0.0.1:8000/admin-panel

Django admin: http://127.0.0.1:8000/admin
   
