from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from database import db, User, QRCode, init_db
import random
import string
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Configuration
# Read secret and database URL from environment (falls back to local sqlite)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'Gyan956958')
db_uri = os.getenv('DATABASE_URL', '')
if db_uri and db_uri.startswith('postgres://'):
    db_uri = db_uri.replace('postgres://', 'postgresql+psycopg2://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or 'sqlite:///referral_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Generate unique User ID
def generate_user_id():
    return 'USER' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))

# JWT Token verification decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token required'}), 403
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except:
            return jsonify({'message': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Admin verification decorator
def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated

# Create admin user
def create_admin():
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin_id = generate_user_id()
        hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
        
        admin = User(
            name='Admin',
            email='admin@example.com',
            password=hashed_password,
            user_id=admin_id,
            is_admin=True
        )
        
        db.session.add(admin)
        db.session.commit()
        
        print('✅ Admin created successfully')
        print(f'📧 Email: admin@example.com')
        print(f'🔑 Password: admin123')
        print(f'🆔 Admin ID: {admin_id}')

# Routes

# Serve static files
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Signup API
@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        referral_id = data.get('referralId', '').strip().upper()
        referrer_name = data.get('referrerName', '').strip()
        
        # Validation
        if not all([name, email, password, referral_id, referrer_name]):
            return jsonify({'message': 'Sabhi fields zaroori hain'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Password kam se kam 6 characters ka hona chahiye'}), 400
        
        # Check if email exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'message': 'Email pehle se registered hai'}), 400
        
        # Verify referral ID
        referrer = User.query.filter_by(user_id=referral_id).first()
        if not referrer:
            return jsonify({'message': 'Invalid Referral ID'}), 400
        
        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Create new user
        new_user_id = generate_user_id()
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            user_id=new_user_id,
            referred_by=referral_id,
            referrer_name=referrer_name,
            is_admin=False
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'Signup successful',
            'userId': new_user_id
        }), 201
        
    except Exception as e:
        print(f'Signup error: {e}')
        return jsonify({'message': 'Server error'}), 500

# Login API
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'Email ya password galat hai'}), 401
        
        # Verify password
        if not check_password_hash(user.password, password):
            return jsonify({'message': 'Email ya password galat hai'}), 401
        
        # Generate token (PyJWT 2.0+ returns string directly)
        try:
            token = jwt.encode({
                'user_id': user.user_id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
            }, app.config['SECRET_KEY'], algorithm="HS256")
            # Ensure token is string (in case of old PyJWT returning bytes)
            if isinstance(token, bytes):
                token = token.decode('utf-8')
        except Exception as e:
            print(f'Token generation error: {e}')
            return jsonify({'message': 'Server error'}), 500
        
        return jsonify({
            'token': token,
            'user': {
                'name': user.name,
                'email': user.email,
                'userId': user.user_id,
                'isAdmin': user.is_admin
            }
        }), 200
        
    except Exception as e:
        print(f'Login error: {e}')
        return jsonify({'message': 'Server error'}), 500

# Verify Token API
@app.route('/api/verify', methods=['GET'])
@token_required
def verify_token(current_user):
    return jsonify({
        'user': {
            'name': current_user.name,
            'email': current_user.email,
            'userId': current_user.user_id,
            'isAdmin': current_user.is_admin
        }
    }), 200

# Get All Users (Admin only)
@app.route('/api/users', methods=['GET'])
@token_required
@admin_required
def get_users(current_user):
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        
        users_list = []
        for user in users:
            # Count referrals
            referral_count = User.query.filter_by(referred_by=user.user_id).count()
            
            users_list.append({
                'name': user.name,
                'email': user.email,
                'userId': user.user_id,
                'referredBy': user.referred_by,
                'referrerName': user.referrer_name,
                'isAdmin': user.is_admin,
                'createdAt': user.created_at.isoformat(),
                'referralCount': referral_count
            })
        
        # Get today's users
        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_users = User.query.filter(User.created_at >= today).count()
        
        return jsonify({
            'users': users_list,
            'totalUsers': len(users_list),
            'todayUsers': today_users
        }), 200
        
    except Exception as e:
        print(f'Get users error: {e}')
        return jsonify({'message': 'Server error'}), 500

# Get Referrals by User ID (Admin only)
@app.route('/api/referrals/<user_id>', methods=['GET'])
@token_required
@admin_required
def get_referrals(current_user, user_id):
    try:
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        referrals = User.query.filter_by(referred_by=user_id).order_by(User.created_at.desc()).all()
        
        referrals_list = []
        for ref in referrals:
            referrals_list.append({
                'name': ref.name,
                'email': ref.email,
                'userId': ref.user_id,
                'createdAt': ref.created_at.isoformat()
            })
        
        return jsonify({
            'user': {
                'name': user.name,
                'userId': user.user_id
            },
            'referrals': referrals_list
        }), 200
        
    except Exception as e:
        print(f'Get referrals error: {e}')
        return jsonify({'message': 'Server error'}), 500

# Get QR Code
@app.route('/api/qrcode', methods=['GET'])
def get_qrcode():
    try:
        qr = QRCode.query.first()
        return jsonify({'qrCode': qr.qr_code if qr else None}), 200
    except Exception as e:
        print(f'Get QR error: {e}')
        return jsonify({'message': 'Server error'}), 500

# Upload QR Code (Admin only)
@app.route('/api/qrcode', methods=['POST'])
@token_required
@admin_required
def upload_qrcode(current_user):
    try:
        data = request.get_json()
        qr_code = data.get('qrCode')
        
        qr = QRCode.query.first()
        if qr:
            qr.qr_code = qr_code
            qr.updated_at = datetime.datetime.utcnow()
        else:
            qr = QRCode(qr_code=qr_code)
            db.session.add(qr)
        
        db.session.commit()
        
        return jsonify({'message': 'QR code uploaded successfully'}), 200
        
    except Exception as e:
        print(f'Upload QR error: {e}')
        return jsonify({'message': 'Server error'}), 500

# Delete QR Code (Admin only)
@app.route('/api/qrcode', methods=['DELETE'])
@token_required
@admin_required
def delete_qrcode(current_user):
    try:
        QRCode.query.delete()
        db.session.commit()
        
        return jsonify({'message': 'QR code removed successfully'}), 200
        
    except Exception as e:
        print(f'Delete QR error: {e}')
        return jsonify({'message': 'Server error'}), 500

# Initialize database and create admin
with app.app_context():
    init_db()
    create_admin()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

    # print("DB:",os.getenv("DATABASE_URL"))
    # print("SECRET:",os.getenv("SECRET_KEY"))