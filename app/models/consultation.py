from app import db
from datetime import datetime

class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    
    # Relationships - backrefs are defined in Patient and Doctor models
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    reason = db.Column(db.Text)
    consultation_type = db.Column(db.String(50), default='General')  # General, Specialist, Emergency, etc.
    duration = db.Column(db.Integer, default=30)  # Duration in minutes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Consultation {self.id} - Patient {self.patient_id} with Doctor {self.doctor_id}>' 