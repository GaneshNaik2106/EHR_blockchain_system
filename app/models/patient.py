from app import db
from datetime import datetime

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))  # Male, Female, Other
    blood_type = db.Column(db.String(5))  # A+, B+, O+, AB+, etc.
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    consultations = db.relationship('Consultation', backref='patient', lazy=True)
    
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
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def __repr__(self):
        return f'<Patient {self.user.name}>' 