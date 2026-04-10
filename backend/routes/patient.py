from flask import send_file, Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, cache
from models.models import User, Doctor, Patient, Appointment, Treatment, DoctorAvailability, Department
import json
import csv
import io
from datetime import date, datetime, timedelta
from functools import wraps
from celery.result import AsyncResult

patient_bp = Blueprint('patient', __name__)


def patient_required(f):
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        identity = json.loads(get_jwt_identity())
        if identity['role'] != 'patient':
            return jsonify({'error': 'Patient access required'}), 403
        kwargs['patient_identity'] = identity
        return f(*args, **kwargs)
    return decorated


def get_patient(identity):
    return Patient.query.filter_by(user_id=identity['user_id']).first()


# ─── Dashboard ────────────────────────────────────────────────
@patient_bp.route('/dashboard', methods=['GET'])
@patient_required
def dashboard(patient_identity):
    patient = get_patient(patient_identity)
    if not patient:
        return jsonify({'error': 'Patient profile not found'}), 404

    today = date.today()
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.date, Appointment.time).all()

    past = Appointment.query.filter(
        Appointment.patient_id == patient.id,
        Appointment.status.in_(['Completed', 'Cancelled'])
    ).order_by(Appointment.date.desc()).limit(5).all()

    return jsonify({
        'patient': patient.to_dict(),
        'upcoming_appointments': [a.to_dict() for a in upcoming],
        'recent_history': [a.to_dict() for a in past],
        'stats': {
            'upcoming_count': len(upcoming),
            'total_visits': Appointment.query.filter_by(patient_id=patient.id, status='Completed').count()
        }
    }), 200


# ─── Profile ──────────────────────────────────────────────────
@patient_bp.route('/profile', methods=['GET'])
@patient_required
def get_profile(patient_identity):
    patient = get_patient(patient_identity)
    return jsonify(patient.to_dict()), 200


@patient_bp.route('/profile', methods=['PUT'])
@patient_required
def update_profile(patient_identity):
    patient = get_patient(patient_identity)
    data = request.get_json()
    patient.name = data.get('name', patient.name)
    patient.age = data.get('age', patient.age)
    patient.gender = data.get('gender', patient.gender)
    patient.phone = data.get('phone', patient.phone)
    patient.address = data.get('address', patient.address)
    patient.blood_group = data.get('blood_group', patient.blood_group)
    patient.emergency_contact = data.get('emergency_contact', patient.emergency_contact)
    if data.get('email'):
        patient.user.email = data['email']
    db.session.commit()
    return jsonify(patient.to_dict()), 200


# ─── Departments ──────────────────────────────────────────────
@patient_bp.route('/departments', methods=['GET'])
@patient_required
def get_departments(patient_identity):
    cached = cache.get('departments')
    if cached:
        return jsonify(cached), 200
    depts = Department.query.all()
    result = [d.to_dict() for d in depts]
    cache.set('departments', result, timeout=300)
    return jsonify(result), 200


# ─── Doctors ──────────────────────────────────────────────────
@patient_bp.route('/doctors', methods=['GET'])
@patient_required
def get_doctors(patient_identity):
    specialization = request.args.get('specialization', '')
    name = request.args.get('name', '')

    # Cache per search combination for 60 seconds
    cache_key = f'doctors_list_{specialization}_{name}'
    cached = cache.get(cache_key)
    if cached:
        return jsonify(cached), 200

    query = Doctor.query.filter_by(is_active=True)
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    if name:
        query = query.filter(Doctor.name.ilike(f'%{name}%'))
    doctors = query.all()

    result = []
    today = date.today()
    for doc in doctors:
        d = doc.to_dict(include_user=False)
        avails = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doc.id,
            DoctorAvailability.date >= today,
            DoctorAvailability.is_available == True
        ).order_by(DoctorAvailability.date).limit(7).all()
        d['availability'] = [a.to_dict() for a in avails]
        result.append(d)

    cache.set(cache_key, result, timeout=60)
    return jsonify(result), 200


@patient_bp.route('/doctors/<int:doctor_id>/availability', methods=['GET'])
@patient_required
def get_doctor_availability(patient_identity, doctor_id):
    today = date.today()
    week_end = today + timedelta(days=7)
    avails = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_end,
        DoctorAvailability.is_available == True
    ).order_by(DoctorAvailability.date).all()

    result = []
    for avail in avails:
        d = avail.to_dict()
        booked_count = Appointment.query.filter_by(
            doctor_id=doctor_id, date=avail.date, status='Booked'
        ).count()
        d['booked_count'] = booked_count
        d['slots_remaining'] = max(0, avail.max_appointments - booked_count)
        result.append(d)

    return jsonify(result), 200


# ─── Appointments ─────────────────────────────────────────────
@patient_bp.route('/appointments', methods=['GET'])
@patient_required
def get_appointments(patient_identity):
    patient = get_patient(patient_identity)
    status = request.args.get('status')
    query = Appointment.query.filter_by(patient_id=patient.id)
    if status:
        query = query.filter_by(status=status)
    appointments = query.order_by(Appointment.date.desc(), Appointment.time).all()
    return jsonify([a.to_dict() for a in appointments]), 200


@patient_bp.route('/appointments', methods=['POST'])
@patient_required
def book_appointment(patient_identity):
    patient = get_patient(patient_identity)
    if not patient.is_active:
        return jsonify({'error': 'Account deactivated'}), 403

    data = request.get_json()
    doctor_id = data.get('doctor_id')
    appt_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    appt_time = data.get('time', '09:00')
    reason = data.get('reason', '')

    if appt_date < date.today():
        return jsonify({'error': 'Cannot book appointment in the past'}), 400

    # Check doctor availability
    avail = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id, date=appt_date, is_available=True
    ).first()
    if not avail:
        return jsonify({'error': 'Doctor not available on this date'}), 400

    # Check slot capacity
    booked_count = Appointment.query.filter_by(
        doctor_id=doctor_id, date=appt_date, status='Booked'
    ).count()
    if booked_count >= avail.max_appointments:
        return jsonify({'error': 'All slots filled for this date'}), 400

    # Check double booking (same doctor, same date+time)
    existing = Appointment.query.filter_by(
        doctor_id=doctor_id, date=appt_date, time=appt_time, status='Booked'
    ).first()
    if existing:
        return jsonify({'error': 'This time slot is already booked'}), 409

    # Check patient not double booking same doctor same date
    patient_existing = Appointment.query.filter_by(
        patient_id=patient.id, doctor_id=doctor_id, date=appt_date, status='Booked'
    ).first()
    if patient_existing:
        return jsonify({'error': 'You already have an appointment with this doctor on this date'}), 409

    appt = Appointment(
        patient_id=patient.id,
        doctor_id=doctor_id,
        date=appt_date,
        time=appt_time,
        status='Booked',
        reason=reason
    )
    db.session.add(appt)
    db.session.commit()
    return jsonify(appt.to_dict()), 201


@patient_bp.route('/appointments/<int:appt_id>', methods=['PUT'])
@patient_required
def update_appointment(patient_identity, appt_id):
    patient = get_patient(patient_identity)
    appt = Appointment.query.filter_by(id=appt_id, patient_id=patient.id).first_or_404()

    if appt.status != 'Booked':
        return jsonify({'error': 'Only booked appointments can be modified'}), 400

    data = request.get_json()
    action = data.get('action', 'reschedule')

    if action == 'cancel':
        appt.status = 'Cancelled'
        db.session.commit()
        return jsonify({'message': 'Appointment cancelled', 'appointment': appt.to_dict()}), 200

    # Reschedule
    new_date = datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else appt.date
    new_time = data.get('time', appt.time)

    if new_date < date.today():
        return jsonify({'error': 'Cannot reschedule to past date'}), 400

    avail = DoctorAvailability.query.filter_by(
        doctor_id=appt.doctor_id, date=new_date, is_available=True
    ).first()
    if not avail:
        return jsonify({'error': 'Doctor not available on this date'}), 400

    conflict = Appointment.query.filter_by(
        doctor_id=appt.doctor_id, date=new_date, time=new_time, status='Booked'
    ).filter(Appointment.id != appt_id).first()
    if conflict:
        return jsonify({'error': 'This time slot is already booked'}), 409

    appt.date = new_date
    appt.time = new_time
    db.session.commit()
    return jsonify(appt.to_dict()), 200


@patient_bp.route('/appointments/<int:appt_id>', methods=['DELETE'])
@patient_required
def cancel_appointment(patient_identity, appt_id):
    patient = get_patient(patient_identity)
    appt = Appointment.query.filter_by(id=appt_id, patient_id=patient.id).first_or_404()
    if appt.status != 'Booked':
        return jsonify({'error': 'Only booked appointments can be cancelled'}), 400
    appt.status = 'Cancelled'
    db.session.commit()
    return jsonify({'message': 'Appointment cancelled'}), 200


# ─── History ──────────────────────────────────────────────────
@patient_bp.route('/history', methods=['GET'])
@patient_required
def get_history(patient_identity):
    patient = get_patient(patient_identity)
    appointments = Appointment.query.filter_by(
        patient_id=patient.id, status='Completed'
    ).order_by(Appointment.date.desc()).all()
    return jsonify([a.to_dict() for a in appointments]), 200

# ─── CSV Export ───────────────────────────────────────────────
@patient_bp.route('/export-csv', methods=['POST'])
@patient_required
def trigger_export(patient_identity):
    patient = get_patient(patient_identity)

    appointments = Appointment.query.filter_by(
        patient_id=patient.id, status='Completed'
    ).order_by(Appointment.date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        'Patient ID', 'Patient Name', 'Doctor', 'Specialization',
        'Date', 'Time', 'Diagnosis', 'Prescription', 'Notes', 'Next Visit'
    ])

    for appt in appointments:
        t = appt.treatment
        writer.writerow([
            patient.id,
            patient.name,
            appt.doctor.name,
            appt.doctor.specialization,
            appt.date.strftime('%Y-%m-%d'),
            appt.time,
            t.diagnosis if t else '',
            t.prescription if t else '',
            t.notes if t else '',
            t.next_visit.strftime('%Y-%m-%d') if t and t.next_visit else ''
        ])

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='patient_history.csv'
    )