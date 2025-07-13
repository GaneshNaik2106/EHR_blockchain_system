from app import db
from datetime import datetime

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    experience_years = db.Column(db.Integer, default=0)
    years_of_experience = db.Column(db.Integer, default=0)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # Male, Female, Other
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    education = db.Column(db.Text)
    bio = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    medical_records = db.relationship('MedicalRecord', lazy=True)
    consultations = db.relationship('Consultation', backref='doctor', lazy=True)
    
    @property
    def total_patients(self):
        """Get total number of unique patients"""
        from app.models.consultation import Consultation
        unique_patients = db.session.query(Consultation.patient_id).filter_by(doctor_id=self.id).distinct().count()
        return unique_patients
    
    @property
    def total_consultations(self):
        """Get total number of consultations"""
        from app.models.consultation import Consultation
        return Consultation.query.filter_by(doctor_id=self.id).count()
    
    @property
    def first_name(self):
        """Get first name from user"""
        return self.user.name.split()[0] if self.user and self.user.name else ''
    
    @property
    def last_name(self):
        """Get last name from user"""
        name_parts = self.user.name.split() if self.user and self.user.name else []
        return ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
    
    @property
    def email(self):
        """Get email from user"""
        return self.user.email if self.user else ''
    
    def __repr__(self):
        return f'<Doctor {self.user.name}>' 