from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import cv2
import numpy as np
from PIL import Image
import os
import base64
import time
from datetime import datetime
import firebase_admin
from firebase_config import get_firestore_db, verify_user_token
from auth_routes import auth_bp, require_auth
from ml_screening import ml_screening
from realtime_routes import realtime_bp
from ml_realtime import detector
from flask_socketio import SocketIO
import jwt

app = Flask(__name__, template_folder='templates')
app.secret_key = 'anemia-screening-secret-key-2024'  # Required for session management
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(realtime_bp, url_prefix='/realtime')

# JWT Secret for session tokens
JWT_SECRET = 'anemia-screening-jwt-secret-2024'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def analyze_image(image_path, user_uid=None):
    """
    Analyze the image for potential anemia indicators using ML.
    Returns a dictionary with risk level, message, color, confidence, and features.
    """
    try:
        # Use ML screening for analysis
        result = ml_screening.predict_anemia_risk(image_path)
        
        # Store result in Firestore if user is authenticated
        if user_uid:
            db = get_firestore_db()
            if db:
                screening_data = {
                    'date': datetime.datetime.utcnow(),
                    'result': result,
                    'imagePath': image_path,
                    'userId': user_uid
                }
                
                # Add to user's screening history
                user_ref = db.collection('users').document(user_uid)
                user_doc = user_ref.get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    if 'screeningHistory' not in user_data:
                        user_data['screeningHistory'] = []
                    
                    user_data['screeningHistory'].append(screening_data)
                    user_ref.update({'screeningHistory': user_data['screeningHistory']})
        
        return result
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return {
            "risk_level": "Error",
            "message": "Error: Unable to process image.",
            "color": "gray",
            "confidence": 0.0
        }

@app.route('/')
def home():
    return render_template('home_modern.html')

@app.route('/screening')
def index():
    return render_template('screening_modern.html')

@app.route('/screening/realtime')
def realtime_screening():
    return render_template('screening_realtime.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if file:
        # Extract just the filename from the file object
        filename = os.path.basename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get user UID if authenticated
        user_uid = session.get('user_uid')
        
        result = analyze_image(filepath, user_uid)
        
        # Clean up uploaded file
        os.remove(filepath)

        # Store result in session for progress tracking (fallback)
        if 'results' not in session:
            session['results'] = []
        session['results'].append({
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'risk_level': result['risk_level'],
            'confidence': result.get('confidence', 0.0),
            'color': result['color']
        })
        session.modified = True

        # Return JSON response for AJAX
        return jsonify({
            'success': True,
            'result': result,
            'redirect': '/result'
        })

@app.route('/doctor')
def doctor():
    return render_template('doctor_modern.html')

@app.route('/result')
def result():
    # Try to get result from session storage (passed from upload)
    # For now, we'll use a default result if none is provided
    default_result = {
        'risk_level': 'Medium',
        'message': 'AI analysis completed. Please consult with a healthcare professional for accurate diagnosis.',
        'color': 'yellow',
        'confidence': 0.85
    }
    
    # Check if we have a result in the session (fallback)
    if 'results' in session and session['results']:
        last_result = session['results'][-1]
        result = {
            'risk_level': last_result['risk_level'],
            'message': 'AI analysis completed. Please consult with a healthcare professional for accurate diagnosis.',
            'color': last_result['color'],
            'confidence': last_result['confidence']
        }
    else:
        result = default_result
    
    return render_template('result_modern.html', result=result)

@app.route('/login')
def login():
    return render_template('login_modern.html')

@app.route('/register')
def register():
    return render_template('register_modern.html')

@app.route('/profile')
@require_auth
def profile():
    return render_template('profile_modern.html')

@app.route('/progress')
@require_auth
def progress():
    # Get user data from Firestore
    user_uid = session.get('user_uid')
    db = get_firestore_db()
    
    if db and user_uid:
        user_doc = db.collection('users').document(user_uid).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            results = user_data.get('screeningHistory', [])
            # Convert datetime objects to strings for template
            for result in results:
                if 'date' in result and hasattr(result['date'], 'strftime'):
                    result['date'] = result['date'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            results = []
    else:
        # Fallback to session data
        results = session.get('results', [])
    
    return render_template('progress.html', results=results)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').lower()
    responses = {
        'precautions': 'Precautions for anemia: Rest when tired, avoid heavy lifting, stay hydrated, avoid caffeine and alcohol, eat iron-rich foods, take supplements as prescribed.',
        'home remedies': 'Home remedies for anemia: Eat iron-rich foods like spinach, lentils, red meat. Include vitamin C foods (citrus, tomatoes) to aid absorption. Drink beetroot juice, pomegranate juice. Avoid tea/coffee with meals.',
        'diet': 'Recommended diet for anemia: Iron-rich foods (spinach, beans, nuts), vitamin C sources (oranges, strawberries), vitamin B12 (eggs, dairy), folate (leafy greens, broccoli). Avoid calcium-rich foods with iron intake.',
        'symptoms': 'Common anemia symptoms: Fatigue, weakness, pale skin, shortness of breath, dizziness, cold hands/feet, irregular heartbeat.',
        'causes': 'Anemia causes: Iron deficiency, vitamin deficiency, chronic diseases, blood loss, bone marrow problems.',
        'treatment': 'Treatment: Depends on cause. May include iron supplements, vitamin B12 injections, blood transfusions, treating underlying conditions.',
        'prevention': 'Prevention: Balanced diet with iron/vitamins, regular check-ups, treat underlying conditions, avoid blood loss.',
        'iron rich foods': 'Iron-rich foods: Red meat, poultry, fish, lentils, beans, tofu, fortified cereals, spinach, raisins.',
        'vitamin c': 'Vitamin C helps iron absorption. Sources: Citrus fruits, bell peppers, strawberries, tomatoes, broccoli.',
        'supplements': 'Supplements: Iron tablets, vitamin B12, folate. Take as prescribed by doctor. May cause constipation or nausea.',
        'exercise': 'Exercise: Light activities like walking are good. Avoid strenuous exercise until anemia improves.',
        'pregnancy': 'During pregnancy: Higher iron needs. Prenatal vitamins, iron-rich diet, regular blood tests.',
        'children': 'In children: Ensure iron-fortified formula, iron-rich foods, vitamin C. Monitor growth and development.',
        'elderly': 'In elderly: May need B12 supplements, check for malabsorption, regular screenings.',
        'default': 'I can help with information about anemia precautions, home remedies, diet recommendations, symptoms, causes, and treatment. What would you like to know?'
    }

    response = responses.get('default')
    for key, value in responses.items():
        if key in user_message:
            response = value
            break

    return {'response': response}

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected to real-time analysis')
    emit('connected', {'message': 'Connected to real-time analysis server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected from real-time analysis')

@socketio.on('start_analysis')
def handle_start_analysis():
    """Handle start analysis request"""
    try:
        detector.start_realtime_analysis(callback=send_result_to_client)
        emit('analysis_started', {'message': 'Real-time analysis started'})
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('stop_analysis')
def handle_stop_analysis():
    """Handle stop analysis request"""
    try:
        detector.stop_realtime_analysis()
        emit('analysis_stopped', {'message': 'Real-time analysis stopped'})
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('frame_data')
def handle_frame_data(data):
    """Handle incoming frame data"""
    try:
        if 'frame' not in data:
            emit('error', {'message': 'No frame data provided'})
            return
        
        # Decode base64 frame
        frame_data = base64.b64decode(data['frame'].split(',')[1])
        
        # Convert to numpy array
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            emit('error', {'message': 'Invalid frame data'})
            return
        
        # Add frame to analysis queue
        detector.add_frame_for_analysis(frame)
        
    except Exception as e:
        emit('error', {'message': str(e)})

def send_result_to_client(result):
    """Send result to connected clients via WebSocket"""
    try:
        socketio.emit('analysis_result', {
            'timestamp': time.time(),
            'result': result
        })
    except Exception as e:
        print(f"❌ Error sending result to client: {e}")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
