from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, cache
from models.models import User, Doctor, Patient, Appointment, Treatment, DoctorAvailability
import json
from datetime import date, datetime, timedelta
from functools import wraps

doctor_bp = Blueprint('doctor', __name__)


def doctor_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        identity = json.loads(get_jwt_identity())
        if identity['role'] != 'doctor':
            return jsonify({'error': 'Doctor access required'}), 403
        kwargs['doctor_identity'] = identity
        return f(*args, **kwargs)
    return decorated


def get_doctor(identity):
    return Doctor.query.filter_by(user_id=identity['user_id']).first()


# ─── Dashboard ────────────────────────────────────────────────
@doctor_bp.route('/dashboard', methods=['GET'])
@doctor_required
def dashboard(doctor_identity):
    doctor = get_doctor(doctor_identity)
    if not doctor:
        return jsonify({'error': 'Doctor profile not found'}), 404

    today = date.today()
    week_end = today + timedelta(days=7)

    today_appts = Appointment.query.filter_by(
        doctor_id=doctor.id, date=today
    ).filter(Appointment.status != 'Cancelled').all()

    week_appts = Appointment.query.filter(
        Appointment.doctor_id == doctor.id,
        Appointment.date >= today,
        Appointment.date <= week_end,
        Appointment.status != 'Cancelled'
    ).order_by(Appointment.date, Appointment.time).all()

    total_patients = db.session.query(Patient.id).join(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().count()

    completed = Appointment.query.filter_by(doctor_id=doctor.id, status='Completed').count()

    return jsonify({
        'doctor': doctor.to_dict(),
        'today_appointments': [a.to_dict() for a in today_appts],
        'week_appointments': [a.to_dict() for a in week_appts],
        'stats': {
            'total_patients': total_patients,
            'today_count': len(today_appts),
            'week_count': len(week_appts),
            'completed_total': completed
        }
    }), 200


# ─── Appointments ─────────────────────────────────────────────
@doctor_bp.route('/appointments', methods=['GET'])
@doctor_required
def get_appointments(doctor_identity):
    doctor = get_doctor(doctor_identity)
    status = request.args.get('status')
    query = Appointment.query.filter_by(doctor_id=doctor.id)
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.date.desc(), Appointment.time).all()
    return jsonify([a.to_dict() for a in appointments]), 200


@doctor_bp.route('/appointments/<int:appt_id>/status', methods=['PUT'])
@doctor_required
def update_status(doctor_identity, appt_id):
    doctor = get_doctor(doctor_identity)
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first_or_404()
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ('Completed', 'Cancelled', 'Booked'):
        return jsonify({'error': 'Invalid status'}), 400
    appt.status = new_status
    if data.get('notes'):
        appt.notes = data['notes']
    db.session.commit()
    return jsonify(appt.to_dict()), 200


# ─── Treatment ────────────────────────────────────────────────
@doctor_bp.route('/appointments/<int:appt_id>/treatment', methods=['POST', 'PUT'])
@doctor_required
def add_treatment(doctor_identity, appt_id):
    doctor = get_doctor(doctor_identity)
    appt = Appointment.query.filter_by(id=appt_id, doctor_id=doctor.id).first_or_404()
    data = request.get_json()

    treatment = appt.treatment
    if treatment:
        treatment.diagnosis = data.get('diagnosis', treatment.diagnosis)
        treatment.prescription = data.get('prescription', treatment.prescription)
        treatment.notes = data.get('notes', treatment.notes)
        if data.get('next_visit'):
            treatment.next_visit = datetime.strptime(data['next_visit'], '%Y-%m-%d').date()
    else:
        next_visit = None
        if data.get('next_visit'):
            next_visit = datetime.strptime(data['next_visit'], '%Y-%m-%d').date()
        treatment = Treatment(
            appointment_id=appt_id,
            diagnosis=data.get('diagnosis', ''),
            prescription=data.get('prescription', ''),
            notes=data.get('notes', ''),
            next_visit=next_visit
        )
        db.session.add(treatment)

    # Auto-complete appointment when treatment is added
    if appt.status == 'Booked':
        appt.status = 'Completed'

    db.session.commit()
    return jsonify(treatment.to_dict()), 200


# ─── Patients ─────────────────────────────────────────────────
@doctor_bp.route('/patients', methods=['GET'])
@doctor_required
def get_patients(doctor_identity):
    doctor = get_doctor(doctor_identity)
    patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor.id
    ).distinct().all()
    return jsonify([p.to_dict() for p in patients]), 200


@doctor_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@doctor_required
def get_patient_history(doctor_identity, patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.date.desc()
    ).all()
    return jsonify({
        'patient': patient.to_dict(),
        'history': [a.to_dict() for a in appointments]
    }), 200


# ─── Availability ─────────────────────────────────────────────
@doctor_bp.route('/availability', methods=['GET'])
@doctor_required
def get_availability(doctor_identity):
    doctor = get_doctor(doctor_identity)
    today = date.today()
    week_end = today + timedelta(days=7)
    avails = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor.id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end
    ).order_by(DoctorAvailability.date).all()
    return jsonify([a.to_dict() for a in avails]), 200


@doctor_bp.route('/availability', methods=['POST'])
@doctor_required
def set_availability(doctor_identity):
    doctor = get_doctor(doctor_identity)
    data = request.get_json()
    avail_list = data.get('availability', [])

    for item in avail_list:
        avail_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
        existing = DoctorAvailability.query.filter_by(
            doctor_id=doctor.id, date=avail_date
        ).first()
        if existing:
            existing.start_time = item.get('start_time', existing.start_time)
            existing.end_time = item.get('end_time', existing.end_time)
            existing.is_available = item.get('is_available', existing.is_available)
            existing.max_appointments = item.get('max_appointments', existing.max_appointments)
        else:
            avail = DoctorAvailability(
                doctor_id=doctor.id,
                date=avail_date,
                start_time=item.get('start_time', '09:00'),
                end_time=item.get('end_time', '17:00'),
                is_available=item.get('is_available', True),
                max_appointments=item.get('max_appointments', 10)
            )
            db.session.add(avail)

    db.session.commit()
    cache.delete(f'availability_{doctor.id}')
    return jsonify({'message': 'Availability updated'}), 200


@doctor_bp.route('/profile', methods=['PUT'])
@doctor_required
def update_profile(doctor_identity):
    doctor = get_doctor(doctor_identity)
    data = request.get_json()
    doctor.phone = data.get('phone', doctor.phone)
    doctor.bio = data.get('bio', doctor.bio)
    doctor.qualification = data.get('qualification', doctor.qualification)
    db.session.commit()
    return jsonify(doctor.to_dict()), 200
