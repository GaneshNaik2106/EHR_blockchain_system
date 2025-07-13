from app import db
from datetime import datetime

class MedicalRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    vital_signs = db.Column(db.Text)  # JSON string for blood pressure, temperature, etc.
    lab_results = db.Column(db.Text)  # JSON string for lab test results
    blockchain_hash = db.Column(db.String(255))  # Hash of the record for blockchain
    ipfs_hash = db.Column(db.String(255))  # IPFS hash for file storage
    date = db.Column(db.Date, default=datetime.utcnow().date)  # Date of the medical record
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor = db.relationship('Doctor', backref='records')
    
    def __repr__(self):
        return f'<MedicalRecord {self.id} - Patient {self.patient_id}>'
    
    def to_dict(self):
        """Convert record to dictionary for blockchain storage"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'prescription': self.prescription,
            'notes': self.notes,
            'symptoms': self.symptoms,
            'vital_signs': self.vital_signs,
            'lab_results': self.lab_results,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 