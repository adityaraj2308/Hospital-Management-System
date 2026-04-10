from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, cache
from models.models import User, Doctor, Patient, Department, Appointment, Treatment, DoctorAvailability
import bcrypt
import json
from datetime import date, datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        identity = json.loads(get_jwt_identity())
        if identity['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


# ─── Dashboard ────────────────────────────────────────────────
@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def dashboard():
    total_doctors = Doctor.query.filter_by(is_active=True).count()
    total_patients = Patient.query.filter_by(is_active=True).count()
    total_appointments = Appointment.query.count()
    booked = Appointment.query.filter_by(status='Booked').count()
    completed = Appointment.query.filter_by(status='Completed').count()
    cancelled = Appointment.query.filter_by(status='Cancelled').count()
    today_appts = Appointment.query.filter_by(date=date.today(), status='Booked').count()

    return jsonify({
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'booked': booked,
        'completed': completed,
        'cancelled': cancelled,
        'today_appointments': today_appts
    }), 200


# ─── Departments ──────────────────────────────────────────────
@admin_bp.route('/departments', methods=['GET'])
@admin_required
def get_departments():
    depts = Department.query.all()
    return jsonify([d.to_dict() for d in depts]), 200


@admin_bp.route('/departments', methods=['POST'])
@admin_required
def add_department():
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Department name required'}), 400
    if Department.query.filter_by(name=name).first():
        return jsonify({'error': 'Department already exists'}), 409
    dept = Department(name=name, description=data.get('description', ''))
    db.session.add(dept)
    db.session.commit()
    cache.delete('departments')
    return jsonify(dept.to_dict()), 201


@admin_bp.route('/departments/<int:dept_id>', methods=['PUT'])
@admin_required
def update_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    data = request.get_json()
    dept.name = data.get('name', dept.name)
    dept.description = data.get('description', dept.description)
    db.session.commit()
    cache.delete('departments')
    return jsonify(dept.to_dict()), 200


@admin_bp.route('/departments/<int:dept_id>', methods=['DELETE'])
@admin_required
def delete_department(dept_id):
    dept = Department.query.get_or_404(dept_id)
    db.session.delete(dept)
    db.session.commit()
    return jsonify({'message': 'Department deleted'}), 200


# ─── Doctors ──────────────────────────────────────────────────
@admin_bp.route('/doctors', methods=['GET'])
@admin_required
def get_doctors():
    doctors = Doctor.query.all()
    return jsonify([d.to_dict() for d in doctors]), 200


@admin_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    data = request.get_json()
    required = ['username', 'email', 'password', 'name', 'specialization']
    if not all(data.get(f) for f in required):
        return jsonify({'error': 'username, email, password, name, specialization required'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409

    password_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
    user = User(username=data['username'], email=data['email'],
                password_hash=password_hash, role='doctor')
    db.session.add(user)
    db.session.flush()

    doctor = Doctor(
        user_id=user.id,
        name=data['name'],
        specialization=data['specialization'],
        department_id=data.get('department_id'),
        phone=data.get('phone', ''),
        experience_years=data.get('experience_years', 0),
        qualification=data.get('qualification', ''),
        bio=data.get('bio', '')
    )
    db.session.add(doctor)
    db.session.commit()
    cache.delete('doctors')
    return jsonify(doctor.to_dict()), 201


@admin_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json()
    doctor.name = data.get('name', doctor.name)
    doctor.specialization = data.get('specialization', doctor.specialization)
    doctor.department_id = data.get('department_id', doctor.department_id)
    doctor.phone = data.get('phone', doctor.phone)
    doctor.experience_years = data.get('experience_years', doctor.experience_years)
    doctor.qualification = data.get('qualification', doctor.qualification)
    doctor.bio = data.get('bio', doctor.bio)

    if data.get('email'):
        doctor.user.email = data['email']
    if data.get('password'):
        doctor.user.password_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()

    db.session.commit()
    cache.delete('doctors')
    return jsonify(doctor.to_dict()), 200


@admin_bp.route('/doctors/<int:doctor_id>/toggle', methods=['PUT'])
@admin_required
def toggle_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_active = not doctor.is_active
    doctor.user.is_active = doctor.is_active
    db.session.commit()
    status = 'activated' if doctor.is_active else 'deactivated'
    return jsonify({'message': f'Doctor {status}', 'is_active': doctor.is_active}), 200


@admin_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.user.is_active = False
    doctor.is_active = False
    db.session.commit()
    return jsonify({'message': 'Doctor blacklisted'}), 200


# ─── Patients ─────────────────────────────────────────────────
@admin_bp.route('/patients', methods=['GET'])
@admin_required
def get_patients():
    patients = Patient.query.all()
    return jsonify([p.to_dict() for p in patients]), 200


@admin_bp.route('/patients/<int:patient_id>', methods=['GET'])
@admin_required
def get_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = patient.to_dict()
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc()).all()
    data['appointments'] = [a.to_dict() for a in appointments]
    return jsonify(data), 200


@admin_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@admin_required
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    data = request.get_json()
    patient.name = data.get('name', patient.name)
    patient.age = data.get('age', patient.age)
    patient.gender = data.get('gender', patient.gender)
    patient.phone = data.get('phone', patient.phone)
    patient.address = data.get('address', patient.address)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    patient.emergency_contact = data.get('emergency_contact', patient.emergency_contact)
    db.session.commit()
    return jsonify(patient.to_dict()), 200


@admin_bp.route('/patients/<int:patient_id>/toggle', methods=['PUT'])
@admin_required
def toggle_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.is_active = not patient.is_active
    patient.user.is_active = patient.is_active
    db.session.commit()
    status = 'activated' if patient.is_active else 'deactivated'
    return jsonify({'message': f'Patient {status}', 'is_active': patient.is_active}), 200


# ─── Appointments ─────────────────────────────────────────────
@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def get_appointments():
    status = request.args.get('status')
    query = Appointment.query
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.date.desc(), Appointment.time.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200


@admin_bp.route('/appointments/<int:appt_id>', methods=['PUT'])
@admin_required
def update_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    data = request.get_json()
    if 'status' in data:
        appt.status = data['status']
    if 'notes' in data:
        appt.notes = data['notes']
    db.session.commit()
    return jsonify(appt.to_dict()), 200


# ─── Search ───────────────────────────────────────────────────
@admin_bp.route('/search', methods=['GET'])
@admin_required
def search():
    q = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    results = {}

    if not q:
        return jsonify(results), 200

    if search_type in ('all', 'doctor'):
        doctors = Doctor.query.join(User).filter(
            db.or_(
                Doctor.name.ilike(f'%{q}%'),
                Doctor.specialization.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%')
            )
        ).all()
        results['doctors'] = [d.to_dict() for d in doctors]

    if search_type in ('all', 'patient'):
        patients = Patient.query.join(User).filter(
            db.or_(
                Patient.name.ilike(f'%{q}%'),
                Patient.phone.ilike(f'%{q}%'),
                User.email.ilike(f'%{q}%'),
                Patient.id == (int(q) if q.isdigit() else -1)
            )
        ).all()
        results['patients'] = [p.to_dict() for p in patients]

    return jsonify(results), 200


# ─── Stats for charts ─────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    from sqlalchemy import func

    # Cache for 60 seconds to boost performance
    cached = cache.get('admin_stats')
    if cached:
        return jsonify(cached), 200

    dept_stats = db.session.query(
        Department.name,
        func.count(Doctor.id).label('count')
    ).outerjoin(Doctor, Doctor.department_id == Department.id).group_by(Department.name).all()

    monthly = db.session.query(
        func.strftime('%Y-%m', Appointment.date).label('month'),
        func.count(Appointment.id).label('count')
    ).group_by('month').order_by('month').limit(12).all()

    doctor_activity = db.session.query(
        Doctor.name,
        func.count(Appointment.id).label('count')
    ).outerjoin(Appointment, db.and_(
        Appointment.doctor_id == Doctor.id,
        Appointment.status.in_(['Completed', 'Booked'])
    )).filter(Doctor.is_active == True).group_by(Doctor.name).order_by(
        func.count(Appointment.id).desc()
    ).limit(8).all()

    result = {
        'department_stats': [{'name': r[0], 'count': r[1]} for r in dept_stats],
        'monthly_appointments': [{'month': r[0], 'count': r[1]} for r in monthly],
        'doctor_activity': [{'name': r[0], 'count': r[1]} for r in doctor_activity]
    }
    cache.set('admin_stats', result, timeout=60)
    return jsonify(result), 200
