from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.patient import Patient
from app.models.record import MedicalRecord
from app.models.consultation import Consultation
from app import db
from datetime import datetime, date, time
from app.services.blockchain_service import BlockchainService

patient_bp = Blueprint('patient', __name__)

@patient_bp.before_request
def require_patient():
    if not current_user.is_authenticated or current_user.role != 'patient':
        flash('Access denied. Patient privileges required.', 'error')
        return redirect(url_for('main.home'))

blockchain_service = BlockchainService()

@patient_bp.route('/dashboard')
@login_required
def dashboard():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    records = MedicalRecord.query.filter_by(patient_id=patient.id).all()
    consultations = Consultation.query.filter_by(patient_id=patient.id).all()
    # Fetch blockchain hashes for each record
    record_hashes = {}
    for record in records:
        record_hash = blockchain_service.hash_record(record.to_dict())
        # Optionally, fetch from blockchain if you store hashes there
        record_hashes[record.id] = record_hash
    return render_template(
        'patient/dashboard.html',
        patient=patient,
        records=records,
        consultations=consultations,
        record_hashes=record_hashes
    )

@patient_bp.route('/records')
@login_required
def records():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    records = MedicalRecord.query.filter_by(patient_id=patient.id).all()
    return render_template('patient/records.html', records=records)

@patient_bp.route('/record/<int:record_id>')
@login_required
def view_record(record_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    record = MedicalRecord.query.filter_by(id=record_id, patient_id=patient.id).first_or_404()
    # Get blockchain hash for this record
    record_hash = blockchain_service.hash_record(record.to_dict())
    return render_template(
        'patient/view_record.html',
        record=record,
        record_hash=record_hash
    )

@patient_bp.route('/consultations')
@login_required
def consultations():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    consultations = Consultation.query.filter_by(patient_id=patient.id).all()
    return render_template('patient/consultations.html', consultations=consultations)

@patient_bp.route('/consultation/<int:consultation_id>')
@login_required
def view_consultation(consultation_id):
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    consultation = Consultation.query.filter_by(id=consultation_id, patient_id=patient.id).first_or_404()
    return render_template('patient/view_consultation.html', consultation=consultation)

@patient_bp.route('/book-consultation', methods=['GET', 'POST'])
@login_required
def book_consultation():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        reason = request.form.get('reason')
        
        # Validate required fields
        if not date_str or not time_str or not reason:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('patient.book_consultation'))
        
        # Convert date string to Python date object
        try:
            consultation_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
            return redirect(url_for('patient.book_consultation'))
        
        # Convert time string to Python time object
        try:
            consultation_time = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            flash('Invalid time format. Please use HH:MM format.', 'error')
            return redirect(url_for('patient.book_consultation'))
        
        consultation = Consultation(
            patient_id=patient.id,
            doctor_id=doctor_id,
            date=consultation_date,
            time=consultation_time,
            reason=reason,
            status='scheduled'
        )
        
        db.session.add(consultation)
        db.session.commit()
        
        flash('Consultation booked successfully!', 'success')
        return redirect(url_for('patient.consultations'))
    
    # Get available doctors
    from app.models.doctor import Doctor
    doctors = Doctor.query.all()
    return render_template('patient/book_consultation.html', doctors=doctors)

@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        date_of_birth_str = request.form.get('date_of_birth')
        if date_of_birth_str:
            try:
                patient.date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for date of birth. Please use YYYY-MM-DD format.', 'error')
                return redirect(url_for('patient.profile'))
        else:
            patient.date_of_birth = None
            
        patient.gender = request.form.get('gender')
        patient.blood_type = request.form.get('blood_type')
        patient.phone = request.form.get('phone')
        patient.address = request.form.get('address')
        patient.emergency_contact = request.form.get('emergency_contact')
        patient.emergency_phone = request.form.get('emergency_phone')
        patient.medical_history = request.form.get('medical_history')
        patient.allergies = request.form.get('allergies')
        patient.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/profile.html', patient=patient)