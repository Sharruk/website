from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    course_type = db.Column(db.String(10), nullable=False)  # UG, PG, MBA
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # CAT, ESE, SAT, Practical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'course_type': self.course_type,
            'department': self.department,
            'semester': self.semester,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Subject {self.code}: {self.name}>'

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    custom_filename = db.Column(db.String(255), nullable=False)
    course_type = db.Column(db.String(10), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    subject_name = db.Column(db.String(200), nullable=True)  # For backward compatibility
    file_type = db.Column(db.String(20), nullable=False, default='QP')  # QP or Syllabus
    size = db.Column(db.String(50), nullable=True)
    file_path = db.Column(db.String(500), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    subject = db.relationship('Subject', backref='files')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'custom_filename': self.custom_filename,
            'course_type': self.course_type,
            'department': self.department,
            'semester': self.semester,
            'category': self.category,
            'subject_id': self.subject_id,
            'subject_name': self.subject_name,
            'subject_code': self.subject.code if self.subject else None,
            'file_type': self.file_type,
            'size': self.size,
            'file_path': self.file_path,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }
    
    def __repr__(self):
        return f'<File {self.filename}>'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'