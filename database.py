from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from database import db, User,QRCode, init_db

db = SQLAlchemy()

class User(db.Model):
    """User Model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    referred_by = db.Column(db.String(20), nullable=True)
    referrer_name = db.Column(db.String(100), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.name} ({self.user_id})>'
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'userId': self.user_id,
            'referredBy': self.referred_by,
            'referrerName': self.referrer_name,
            'isAdmin': self.is_admin,
            'createdAt': self.created_at.isoformat()
        }
    
    def get_referrals(self):
        """Get all users referred by this user"""
        return User.query.filter_by(referred_by=self.user_id).all()
    
    def get_referral_count(self):
        """Get count of referrals"""
        return User.query.filter_by(referred_by=self.user_id).count()


class QRCode(db.Model):
    """QR Code Model"""
    __tablename__ = 'qrcodes'
    
    id = db.Column(db.Integer, primary_key=True)
    qr_code = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<QRCode {self.id}>'
    
    def to_dict(self):
        """Convert QR code object to dictionary"""
        return {
            'id': self.id,
            'qrCode': self.qr_code,
            'updatedAt': self.updated_at.isoformat()
        }


def init_db():
    """Initialize database - create all tables"""
    db.create_all()
    print('✅ Database tables created successfully')