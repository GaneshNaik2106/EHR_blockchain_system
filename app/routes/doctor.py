from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.record import MedicalRecord
from app.models.consultation import Consultation
from app import db
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.before_request
def require_doctor():
    if not current_user.is_authenticated or current_user.role != 'doctor':
        flash('Access denied. Doctor privileges required.', 'error')
        return redirect(url_for('main.home'))

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    # Get today's consultations
    today = datetime.now().date()
    today_consultations = Consultation.query.filter_by(
        doctor_id=doctor.id, 
        date=today
    ).all()
    
    # Get pending consultations
    pending_consultations = Consultation.query.filter_by(
        doctor_id=doctor.id, 
        status='scheduled'
    ).order_by(Consultation.date).limit(10).all()
    
    # Get recent medical records created by this doctor
    recent_records = MedicalRecord.query.filter_by(
        doctor_id=doctor.id
    ).order_by(MedicalRecord.created_at.desc()).limit(5).all()
    
    return render_template('doctor/dashboard.html', 
                         doctor=doctor,
                         today_consultations=today_consultations,
                         pending_consultations=pending_consultations,
                         recent_records=recent_records)

@doctor_bp.route('/patients')
@login_required
def patients():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    # Get all patients in the system
    all_patients = Patient.query.all()
    
    # Get patients who have consulted with this doctor
    consultations = Consultation.query.filter_by(doctor_id=doctor.id).all()
    consulted_patient_ids = list(set([c.patient_id for c in consultations]))
    
    # Add consultation info to each patient
    for patient in all_patients:
        patient.has_consulted = patient.id in consulted_patient_ids
        patient.consultation_count = len([c for c in consultations if c.patient_id == patient.id])
    
    return render_template('doctor/patients.html', patients=all_patients)

@doctor_bp.route('/patient/<int:patient_id>')
@login_required
def view_patient(patient_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.created_at.desc()).all()
    consultations = Consultation.query.filter_by(patient_id=patient_id, doctor_id=doctor.id).order_by(Consultation.date.desc()).all()
    
    return render_template('doctor/view_patient.html', 
                         patient=patient, 
                         records=records, 
                         consultations=consultations)

@doctor_bp.route('/patient/<int:patient_id>/record/new', methods=['GET', 'POST'])
@login_required
def create_record(patient_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        
        record = MedicalRecord(
            patient_id=patient_id,
            doctor_id=doctor.id,
            diagnosis=diagnosis,
            treatment=treatment,
            prescription=prescription,
            notes=notes,
            date=datetime.now().date()
        )
        
        db.session.add(record)
        db.session.commit()
        
        flash('Medical record created successfully!', 'success')
        return redirect(url_for('doctor.view_patient', patient_id=patient_id))
    
    return render_template('doctor/create_record.html', patient=patient)

@doctor_bp.route('/record/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    record = MedicalRecord.query.filter_by(id=record_id, doctor_id=doctor.id).first_or_404()
    
    if request.method == 'POST':
        record.diagnosis = request.form.get('diagnosis')
        record.treatment = request.form.get('treatment')
        record.prescription = request.form.get('prescription')
        record.notes = request.form.get('notes')
        record.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Medical record updated successfully!', 'success')
        return redirect(url_for('doctor.view_patient', patient_id=record.patient_id))
    
    return render_template('doctor/edit_record.html', record=record)

@doctor_bp.route('/consultations')
@login_required
def consultations():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    consultations = Consultation.query.filter_by(doctor_id=doctor.id).order_by(Consultation.date.desc()).all()
    return render_template('doctor/consultations.html', consultations=consultations)

@doctor_bp.route('/consultations/<int:consultation_id>/start', methods=['POST'])
@login_required
def start_consultation(consultation_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'})
    
    consultation = Consultation.query.filter_by(id=consultation_id, doctor_id=doctor.id).first()
    if not consultation:
        return jsonify({'success': False, 'message': 'Consultation not found'})
    
    consultation.status = 'in_progress'
    consultation.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Consultation started successfully'})

@doctor_bp.route('/consultations/<int:consultation_id>/complete', methods=['POST'])
@login_required
def complete_consultation(consultation_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'})
    
    consultation = Consultation.query.filter_by(id=consultation_id, doctor_id=doctor.id).first()
    if not consultation:
        return jsonify({'success': False, 'message': 'Consultation not found'})
    
    consultation.status = 'completed'
    consultation.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Consultation completed successfully'})

@doctor_bp.route('/consultation/<int:consultation_id>')
@login_required
def view_consultation(consultation_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    consultation = Consultation.query.filter_by(id=consultation_id, doctor_id=doctor.id).first_or_404()
    return render_template('doctor/view_consultation.html', consultation=consultation)

@doctor_bp.route('/consultation/<int:consultation_id>/update', methods=['POST'])
@login_required
def update_consultation(consultation_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    consultation = Consultation.query.filter_by(id=consultation_id, doctor_id=doctor.id).first_or_404()
    
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    consultation.status = status
    consultation.notes = notes
    consultation.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Consultation updated successfully!', 'success')
    return redirect(url_for('doctor.view_consultation', consultation_id=consultation_id))

@doctor_bp.route('/schedule')
@login_required
def schedule():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    # Get today's appointments
    today = datetime.now().date()
    today_appointments = Consultation.query.filter_by(
        doctor_id=doctor.id, 
        date=today
    ).order_by(Consultation.date).all()
    
    # Get week appointments (next 7 days)
    from datetime import timedelta
    week_end = today + timedelta(days=7)
    week_appointments = Consultation.query.filter(
        Consultation.doctor_id == doctor.id,
        Consultation.date >= today,
        Consultation.date <= week_end
    ).order_by(Consultation.date).all()
    
    # Group by date for weekly view
    week_data = []
    for i in range(7):
        date = today + timedelta(days=i)
        day_appointments = [c for c in week_appointments if c.date == date]
        week_data.append({
            'date': date,
            'count': len(day_appointments)
        })
    
    # Mock data for available slots and pending requests
    available_slots = 15  # Mock data
    pending_requests = []  # Mock data - would come from appointment requests
    
    schedule_data = {
        'today_appointments': today_appointments,
        'week_appointments': week_data,
        'available_slots': available_slots,
        'pending_requests': pending_requests
    }
    
    return render_template('doctor/schedule.html', schedule_data=schedule_data)

@doctor_bp.route('/schedule/availability', methods=['POST'])
@login_required
def set_availability():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'})
    
    data = request.get_json()
    # Here you would save the availability settings
    # For now, just return success
    return jsonify({'success': True, 'message': 'Availability updated successfully'})

@doctor_bp.route('/schedule/requests/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_request(request_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'})
    
    # Here you would approve the appointment request
    # For now, just return success
    return jsonify({'success': True, 'message': 'Request approved successfully'})

@doctor_bp.route('/schedule/requests/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_request(request_id):
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'})
    
    # Here you would reject the appointment request
    # For now, just return success
    return jsonify({'success': True, 'message': 'Request rejected successfully'})

@doctor_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found. Please contact support.', 'error')
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        doctor.specialization = request.form.get('specialization')
        doctor.license_number = request.form.get('license_number')
        doctor.phone = request.form.get('phone')
        doctor.address = request.form.get('address')
        doctor.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('doctor.profile'))
    
    return render_template('doctor/profile.html', doctor=doctor)

@doctor_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'})
    
    data = request.get_json()
    
    # Update doctor profile fields
    if 'first_name' in data:
        doctor.first_name = data['first_name']
    if 'last_name' in data:
        doctor.last_name = data['last_name']
    if 'email' in data:
        doctor.email = data['email']
    if 'phone' in data:
        doctor.phone = data['phone']
    if 'specialization' in data:
        doctor.specialization = data['specialization']
    if 'license_number' in data:
        doctor.license_number = data['license_number']
    if 'years_of_experience' in data:
        doctor.years_of_experience = data['years_of_experience']
    if 'education' in data:
        doctor.education = data['education']
    if 'bio' in data:
        doctor.bio = data['bio']
    if 'address' in data:
        doctor.address = data['address']
    if 'city' in data:
        doctor.city = data['city']
    if 'state' in data:
        doctor.state = data['state']
    if 'zip_code' in data:
        doctor.zip_code = data['zip_code']
    if 'date_of_birth' in data and data['date_of_birth']:
        try:
            doctor.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format for date of birth'})
    if 'gender' in data:
        doctor.gender = data['gender']
    
    doctor.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

@doctor_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        return jsonify({'success': False, 'message': 'Doctor profile not found'})
    
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    # Here you would verify the current password and update it
    # For now, just return success
    return jsonify({'success': True, 'message': 'Password changed successfully'}) 