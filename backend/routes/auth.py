from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from extensions import db
from models.models import User, Patient, Doctor
import bcrypt
import json

auth_bp = Blueprint('auth', __name__)


# ---------------- LOGIN ---------------- #
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account is deactivated. Contact admin.'}), 403

    # Get profile info
    name = user.username
    profile_id = None

    if user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if doctor:
            name = doctor.name
            profile_id = doctor.id

    elif user.role == 'patient':
        patient = Patient.query.filter_by(user_id=user.id).first()
        if patient:
            name = patient.name
            profile_id = patient.id

    identity = json.dumps({
        'user_id': user.id,
        'role': user.role,
        'profile_id': profile_id
    })

    token = create_access_token(identity=identity)

    return jsonify({
        'token': token,
        'role': user.role,
        'username': user.username,
        'name': name,
        'user_id': user.id,
        'profile_id': profile_id
    }), 200


# ---------------- REGISTER ---------------- #
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    age = data.get('age')
    gender = data.get('gender', '').strip()
    blood_group = data.get('blood_group', '').strip()

    # ✅ Required fields
    if not username or not email or not password or not name:
        return jsonify({'error': 'Username, email, password and name are required'}), 400

    # ✅ Basic email validation
    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400

    # ✅ Duplicate checks
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already taken'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # ✅ Password hashing
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # ✅ Create user
    user = User(
        username=username,
        email=email,   # 🔥 IMPORTANT for reminders
        password_hash=password_hash,
        role='patient'
    )
    db.session.add(user)
    db.session.flush()

    # ✅ Create patient profile
    patient = Patient(
        user_id=user.id,
        name=name,
        phone=phone,
        age=age,
        gender=gender,
        blood_group=blood_group
    )
    db.session.add(patient)
    db.session.commit()

    return jsonify({'message': 'Registration successful! Please login.'}), 201


# ---------------- GET CURRENT USER ---------------- #
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    identity = json.loads(get_jwt_identity())
    user = User.query.get(identity['user_id'])

    if not user:
        return jsonify({'error': 'User not found'}), 404

    result = user.to_dict()

    if user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user.id).first()
        if doctor:
            result['profile'] = doctor.to_dict()

    elif user.role == 'patient':
        patient = Patient.query.filter_by(user_id=user.id).first()
        if patient:
            result['profile'] = patient.to_dict()

    return jsonify(result), 200


# ---------------- CHANGE PASSWORD ---------------- #
@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    identity = json.loads(get_jwt_identity())
    data = request.get_json() or {}

    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    user = User.query.get(identity['user_id'])

    if not user or not bcrypt.checkpw(old_password.encode(), user.password_hash.encode()):
        return jsonify({'error': 'Current password incorrect'}), 400

    user.password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    db.session.commit()

    return jsonify({'message': 'Password changed successfully'}), 200