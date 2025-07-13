#!/usr/bin/env python3
"""
Test script for authentication functionality
"""

from app import create_app, db
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

def test_user_creation():
    """Test creating users with different roles"""
    print("=== Testing User Creation ===")
    
    app = create_app()
    with app.app_context():
        # Clear existing test users
        User.query.filter_by(email='test_patient@example.com').delete()
        User.query.filter_by(email='test_doctor@example.com').delete()
        db.session.commit()
        
        # Test 1: Create a patient
        print("\n1. Creating test patient...")
        try:
            patient_user = User(
                name='Test Patient',
                email='test_patient@example.com',
                password_hash=generate_password_hash('password123'),
                role='patient'
            )
            db.session.add(patient_user)
            db.session.flush()  # Get user.id before commit
            
            patient = Patient(user_id=patient_user.id)
            db.session.add(patient)
            db.session.commit()
            
            print("✅ Patient created successfully!")
            print(f"   User ID: {patient_user.id}")
            print(f"   Patient ID: {patient.id}")
            print(f"   Email: {patient_user.email}")
            print(f"   Role: {patient_user.role}")
            
        except Exception as e:
            print(f"❌ Failed to create patient: {e}")
            db.session.rollback()
            return False
        
        # Test 2: Create a doctor
        print("\n2. Creating test doctor...")
        try:
            doctor_user = User(
                name='Test Doctor',
                email='test_doctor@example.com',
                password_hash=generate_password_hash('password123'),
                role='doctor'
            )
            db.session.add(doctor_user)
            db.session.flush()  # Get user.id before commit
            
            doctor = Doctor(
                user_id=doctor_user.id,
                specialization='General Medicine',
                license_number=f'LIC{doctor_user.id:06d}'
            )
            db.session.add(doctor)
            db.session.commit()
            
            print("✅ Doctor created successfully!")
            print(f"   User ID: {doctor_user.id}")
            print(f"   Doctor ID: {doctor.id}")
            print(f"   Email: {doctor_user.email}")
            print(f"   Role: {doctor_user.role}")
            print(f"   Specialization: {doctor.specialization}")
            print(f"   License: {doctor.license_number}")
            
        except Exception as e:
            print(f"❌ Failed to create doctor: {e}")
            db.session.rollback()
            return False
        
        return True

def test_password_verification():
    """Test password hashing and verification"""
    print("\n=== Testing Password Verification ===")
    
    app = create_app()
    with app.app_context():
        # Test password hashing
        password = 'testpassword123'
        password_hash = generate_password_hash(password)
        
        print(f"Original password: {password}")
        print(f"Generated hash: {password_hash[:50]}...")
        
        # Test password verification
        is_valid = check_password_hash(password_hash, password)
        print(f"Password verification: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Test wrong password
        is_invalid = check_password_hash(password_hash, 'wrongpassword')
        print(f"Wrong password verification: {'❌ Should be invalid' if not is_invalid else '⚠️ Unexpectedly valid'}")
        
        return is_valid and not is_invalid

def test_user_queries():
    """Test querying users by email and role"""
    print("\n=== Testing User Queries ===")
    
    app = create_app()
    with app.app_context():
        # Test finding patient by email
        patient_user = User.query.filter_by(email='test_patient@example.com').first()
        if patient_user:
            print(f"✅ Found patient: {patient_user.name} ({patient_user.email})")
            print(f"   Role: {patient_user.role}")
            print(f"   Has patient profile: {'Yes' if hasattr(patient_user, 'patient_profile') and patient_user.patient_profile else 'No'}")
        else:
            print("❌ Patient not found")
            return False
        
        # Test finding doctor by email
        doctor_user = User.query.filter_by(email='test_doctor@example.com').first()
        if doctor_user:
            print(f"✅ Found doctor: {doctor_user.name} ({doctor_user.email})")
            print(f"   Role: {doctor_user.role}")
            print(f"   Has doctor profile: {'Yes' if hasattr(doctor_user, 'doctor_profile') and doctor_user.doctor_profile else 'No'}")
        else:
            print("❌ Doctor not found")
            return False
        
        # Test role-based queries
        patients = User.query.filter_by(role='patient').all()
        doctors = User.query.filter_by(role='doctor').all()
        
        print(f"\n📊 User Statistics:")
        print(f"   Total patients: {len(patients)}")
        print(f"   Total doctors: {len(doctors)}")
        
        return True

def test_relationships():
    """Test model relationships"""
    print("\n=== Testing Model Relationships ===")
    
    app = create_app()
    with app.app_context():
        # Test patient relationship
        patient_user = User.query.filter_by(email='test_patient@example.com').first()
        if patient_user and patient_user.patient_profile:
            print(f"✅ Patient relationship works:")
            print(f"   User: {patient_user.name}")
            print(f"   Patient ID: {patient_user.patient_profile.id}")
            print(f"   User ID from patient: {patient_user.patient_profile.user_id}")
        else:
            print("❌ Patient relationship failed")
            return False
        
        # Test doctor relationship
        doctor_user = User.query.filter_by(email='test_doctor@example.com').first()
        if doctor_user and doctor_user.doctor_profile:
            print(f"✅ Doctor relationship works:")
            print(f"   User: {doctor_user.name}")
            print(f"   Doctor ID: {doctor_user.doctor_profile.id}")
            print(f"   User ID from doctor: {doctor_user.doctor_profile.user_id}")
            print(f"   Specialization: {doctor_user.doctor_profile.specialization}")
        else:
            print("❌ Doctor relationship failed")
            return False
        
        return True

if __name__ == '__main__':
    print("🧪 Testing Authentication System")
    print("=" * 50)
    
    # Run all tests
    tests = [
        test_user_creation,
        test_password_verification,
        test_user_queries,
        test_relationships
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Authentication system is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the errors above.") 