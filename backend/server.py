import os
import sys
import bcrypt
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Add backend dir to path for module resolution
sys.path.insert(0, str(ROOT_DIR))

from flask import Flask, jsonify
from flask_cors import CORS
from extensions import db, jwt, mail, cache
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # DEBUG (check env loaded)
    print("MAIL USER:", app.config['MAIL_USERNAME'])

    # Try Redis cache, fallback to SimpleCache
    try:
        import redis as redis_lib
        r = redis_lib.from_url(app.config['REDIS_URL'])
        r.ping()
    except Exception:
        app.config['CACHE_TYPE'] = 'SimpleCache'
        app.config['CACHE_DEFAULT_TIMEOUT'] = 300

    # Init extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cache.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.doctor import doctor_bp
    from routes.patient import patient_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(doctor_bp, url_prefix='/api/doctor')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')

    # ---------------- ROUTES ---------------- #

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'app': 'HMS - Hospital Management System'})

    @app.route('/api/test-email')
    def test_email():
        from flask_mail import Message

        msg = Message(
            subject="Test Email from HMS",
            recipients=["hms.project.demo@gmail.com"],  # send to yourself
            body="✅ Email system is working!"
        )
        mail.send(msg)

        return "Email sent successfully!"

    @app.route('/api/download-zip')
    def download_zip():
        from flask import send_file
        zip_path = Path(__file__).parent.parent / 'HMS_23f2000961.zip'
        return send_file(str(zip_path), as_attachment=True, download_name='HMS_23f2000961.zip', mimetype='application/zip')

    @app.route('/api/departments', methods=['GET'])
    def get_departments():
        from models.models import Department
        depts = Department.query.all()
        return jsonify([d.to_dict() for d in depts]), 200

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        _seed_data(app)

    return app


def _seed_data(app):
    from models.models import User, Doctor, Patient, Department, DoctorAvailability
    from datetime import date, timedelta

    # Create admin
    if not User.query.filter_by(role='admin').first():
        pw = bcrypt.hashpw('Admin@123'.encode(), bcrypt.gensalt()).decode()
        admin = User(username='admin', email='admin@hms.local', password_hash=pw, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("[HMS] Admin created: username=admin password=Admin@123")

    # Seed departments
    dept_names = [
        ('Cardiology', 'Heart and cardiovascular diseases'),
        ('Neurology', 'Brain and nervous system disorders'),
        ('Orthopedics', 'Bone and joint diseases'),
        ('Pediatrics', 'Children medical care'),
        ('Dermatology', 'Skin and hair disorders'),
        ('General Medicine', 'General health and routine checkups'),
        ('Gynecology', 'Women health and reproductive system'),
        ('ENT', 'Ear, Nose and Throat disorders'),
    ]
    for name, desc in dept_names:
        if not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name, description=desc))
    db.session.commit()

    # Seed demo doctor
    if not User.query.filter_by(username='dr.sharma').first():
        dept = Department.query.filter_by(name='Cardiology').first()
        pw = bcrypt.hashpw('Doctor@123'.encode(), bcrypt.gensalt()).decode()
        user = User(username='dr.sharma', email='dr.sharma@hms.local', password_hash=pw, role='doctor')
        db.session.add(user)
        db.session.flush()
        doctor = Doctor(
            user_id=user.id, name='Dr. Rajesh Sharma',
            specialization='Cardiology', department_id=dept.id if dept else None,
            phone='9876543210', experience_years=10,
            qualification='MBBS, MD (Cardiology)', bio='Senior Cardiologist with 10 years experience'
        )
        db.session.add(doctor)
        db.session.flush()

        today = date.today()
        for i in range(7):
            avail_date = today + timedelta(days=i)
            if avail_date.weekday() < 6:
                db.session.add(DoctorAvailability(
                    doctor_id=doctor.id,
                    date=avail_date,
                    start_time='09:00',
                    end_time='17:00',
                    is_available=True,
                    max_appointments=10
                ))
        db.session.commit()

    # ❗ IMPORTANT: FIX PATIENT EMAIL
    if not User.query.filter_by(username='patient1').first():
        pw = bcrypt.hashpw('Patient@123'.encode(), bcrypt.gensalt()).decode()
        user = User(
            username='patient1',
            email='hms.project.demo@gmail.com',  # ✅ CHANGE HERE
            password_hash=pw,
            role='patient'
        )
        db.session.add(user)
        db.session.flush()
        patient = Patient(
            user_id=user.id,
            name='Rahul Kumar',
            age=30,
            gender='Male',
            phone='9123456789',
            blood_group='B+',
            address='123 Main Street, Delhi'
        )
        db.session.add(patient)
        db.session.commit()


# Create Flask app instance
flask_app = create_app()

from asgiref.wsgi import WsgiToAsgi
app = WsgiToAsgi(flask_app)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=5000, debug=True)