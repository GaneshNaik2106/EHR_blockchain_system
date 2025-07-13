from app import create_app, db
from app.models.user import User
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.record import MedicalRecord
from datetime import datetime

app = create_app()

with app.app_context():
    print("=== Testing Medical Record Creation ===")
    
    # Get a doctor
    doctor = Doctor.query.first()
    if doctor:
        print(f"Found doctor: {doctor.user.name}")
        
        # Get a patient
        patient = Patient.query.first()
        if patient:
            print(f"Found patient: {patient.user.name}")
            
            # Create a test medical record
            record = MedicalRecord(
                patient_id=patient.id,
                doctor_id=doctor.id,
                diagnosis="Test diagnosis",
                treatment="Test treatment",
                prescription="Test prescription",
                notes="Test notes",
                date=datetime.now().date()
            )
            
            try:
                db.session.add(record)
                db.session.commit()
                print(f"✅ Medical record created successfully! ID: {record.id}")
                
                # Test retrieving the record
                retrieved_record = MedicalRecord.query.get(record.id)
                if retrieved_record:
                    print(f"✅ Record retrieved successfully!")
                    print(f"   Patient: {retrieved_record.patient.user.name}")
                    print(f"   Doctor: {retrieved_record.doctor.user.name}")
                    print(f"   Diagnosis: {retrieved_record.diagnosis}")
                    print(f"   Date: {retrieved_record.date}")
                else:
                    print("❌ Failed to retrieve record")
                    
            except Exception as e:
                print(f"❌ Error creating record: {e}")
                db.session.rollback()
        else:
            print("❌ No patients found")
    else:
        print("❌ No doctors found")
    
    print("\n=== Current Medical Records ===")
    records = MedicalRecord.query.all()
    print(f"Total records: {len(records)}")
    
    for record in records:
        print(f"Record ID: {record.id}")
        print(f"  Patient: {record.patient.user.name if record.patient else 'Unknown'}")
        print(f"  Doctor: {record.doctor.user.name if record.doctor else 'Unknown'}")
        print(f"  Diagnosis: {record.diagnosis}")
        print(f"  Date: {record.date}")
        print("---") 