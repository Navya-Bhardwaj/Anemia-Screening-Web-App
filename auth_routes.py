from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template
from firebase_config import create_user, verify_user_token, get_user_by_uid, get_firestore_db
import jwt
import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# JWT Secret for session tokens
JWT_SECRET = 'anemia-screening-jwt-secret-2024'

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration endpoint"""
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    display_name = data.get('displayName', '')
    firstName = data.get('firstName', '')
    lastName = data.get('lastName', '')
    phone = data.get('phone', '')
    dateOfBirth = data.get('dateOfBirth', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    try:
        from firebase_config import get_firestore_db, firebase_initialized, auth
        
        if firebase_initialized:
            # Firebase mode - try to find user or create session fallback
            try:
                # Try to find existing user in Firebase Auth
                user = auth.get_user_by_email(email)
                user_uid = user.uid
                
                # Store user data in Firestore
                db = get_firestore_db()
                if db:
                    user_data = {
                        'uid': user_uid,
                        'email': email,
                        'displayName': display_name,
                        'firstName': firstName,
                        'lastName': lastName,
                        'phone': phone,
                        'dateOfBirth': dateOfBirth,
                        'createdAt': datetime.datetime.utcnow(),
                        'screeningHistory': [],
                        'profile': {
                            'age': '',
                            'gender': '',
                            'medicalHistory': '',
                            'riskFactors': []
                        }
                    }
                    db.collection('users').document(user_uid).set(user_data, merge=True)
                
                return jsonify({
                    'message': 'User profile created successfully',
                    'uid': user_uid,
                    'email': email,
                    'mode': 'firebase'
                }), 201
                
            except Exception as e:
                print(f"❌ User not found in Firebase Auth, creating session: {e}")
                # Fall back to session mode
                pass
        
        # Session mode (fallback)
        session_user_id = f"session_{email.replace('@', '_').replace('.', '_')}"
        session['user_uid'] = session_user_id
        session['user_email'] = email
        session['user_display_name'] = display_name
        session['user_first_name'] = firstName
        session['user_last_name'] = lastName
        
        return jsonify({
            'message': 'User created successfully (session mode)',
            'uid': session_user_id,
            'email': email,
            'mode': 'session'
        }), 201
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    id_token = data.get('idToken')
    email = data.get('email')
    password = data.get('password')
    
    # Firebase login with ID token
    if id_token:
        # Verify Firebase ID token
        decoded_token = verify_user_token(id_token)
        if decoded_token:
            # Create session token
            session_token = jwt.encode({
                'uid': decoded_token['uid'],
                'email': decoded_token['email'],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
            }, JWT_SECRET, algorithm='HS256')
            
            session['user_token'] = session_token
            session['user_uid'] = decoded_token['uid']
            session['user_email'] = decoded_token['email']
            session['user_display_name'] = decoded_token.get('displayName', '')
            
            return jsonify({
                'message': 'Login successful',
                'token': session_token,
                'user': {
                    'uid': decoded_token['uid'],
                    'email': decoded_token['email'],
                    'displayName': decoded_token.get('displayName', '')
                },
                'mode': 'firebase'
            }), 200
        else:
            return jsonify({'error': 'Invalid Firebase token'}), 401
    
    # Session-based login with email/password
    elif email and password:
        # Simple session-based authentication (for demo purposes)
        session_user_id = f"session_{email.replace('@', '_').replace('.', '_')}"
        
        # Create session token
        session_token = jwt.encode({
            'uid': session_user_id,
            'email': email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        session['user_token'] = session_token
        session['user_uid'] = session_user_id
        session['user_email'] = email
        session['user_display_name'] = email.split('@')[0]  # Simple display name
        
        return jsonify({
            'message': 'Login successful',
            'token': session_token,
            'user': {
                'uid': session_user_id,
                'email': email,
                'displayName': email.split('@')[0]
            },
            'mode': 'session'
        }), 200
    
    else:
        return jsonify({'error': 'ID token or email/password required'}), 400

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """User logout endpoint"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/profile', methods=['GET', 'PUT'])
def profile():
    """User profile management"""
    if 'user_uid' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    uid = session['user_uid']
    db = get_firestore_db()
    
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    if request.method == 'GET':
        # Get user profile
        user_doc = db.collection('users').document(uid).get()
        if user_doc.exists:
            return jsonify(user_doc.to_dict()), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    
    elif request.method == 'PUT':
        # Update user profile
        data = request.get_json()
        db.collection('users').document(uid).update(data)
        return jsonify({'message': 'Profile updated successfully'}), 200

def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_uid' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
