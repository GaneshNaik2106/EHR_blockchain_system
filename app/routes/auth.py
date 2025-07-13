from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'patient')
        
        # Basic validation
        if not name or not email or not password or not confirm_password or not role:
            flash('All fields are required', 'error')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('auth/register.html')
        
        if role not in ['patient', 'doctor']:
            flash('Invalid role selected', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        try:
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                role=role
            )
            db.session.add(user)
            db.session.flush()  # Get user.id before commit

            # Create patient profile if role is patient
            if role == 'patient':
                patient = Patient(user_id=user.id)
                db.session.add(patient)
            # Create doctor profile if role is doctor
            elif role == 'doctor':
                # For now, create doctor with default values
                # In a real application, you'd want to collect this information during registration
                doctor = Doctor(
                    user_id=user.id, 
                    specialization='General Medicine', 
                    license_number=f'LIC{user.id:06d}'  # Generate a temporary license number
                )
                db.session.add(doctor)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html') 