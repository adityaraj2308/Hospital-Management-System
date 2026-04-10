# 🏥 Hospital Management System

A full-stack web application to manage hospital operations including patients, doctors, appointments, and treatments.

---

## 🚀 Features

### 🔐 Authentication & Roles

* JWT-based authentication
* Role-based dashboards (Admin, Doctor, Patient)

### 👨‍⚕️ Admin

* Manage doctors and patients
* View system statistics
* Control appointments

### 🩺 Doctor

* View appointments
* Add diagnosis and prescriptions
* Manage availability

### 👤 Patient

* Register and login
* Book / reschedule / cancel appointments
* View treatment history
* Export treatment history as CSV

### ⚙️ Background Jobs

* Daily reminder emails (Celery + Redis)
* Monthly doctor reports
* Async task processing

### 📊 Other Features

* Redis caching
* API-based architecture
* Responsive UI (Vue + Bootstrap)

---

## 🛠️ Tech Stack

| Layer      | Technology              |
| ---------- | ----------------------- |
| Frontend   | Vue.js, Vite, Bootstrap |
| Backend    | Flask, SQLAlchemy       |
| Auth       | JWT                     |
| Database   | SQLite                  |
| Async Jobs | Celery + Redis          |
| Email      | Flask-Mail              |

---

## ⚙️ Setup Instructions

### Backend

```bash
cd backend
pip install -r requirements.txt
python server.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Environment Variables

Create `.env` file:

```
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_app_password
SECRET_KEY=your_secret
JWT_SECRET_KEY=your_jwt_secret
REDIS_URL=redis://localhost:6379/0
```

---

## 📌 API Documentation

Available in `api.yaml`

---

## 🎥 Demo

https://drive.google.com/file/d/1bNFn7JyRwicAwb0_yPCMMgWpp0O6fX7-/view?usp=drive_link

---

## 👨‍💻 Author

Aditya Raj

---