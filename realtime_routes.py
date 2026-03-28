from flask import Blueprint, request, jsonify, render_template
from flask_socketio import emit
import cv2
import numpy as np
import base64
import json
import time
from ml_realtime import detector

# Create blueprint
realtime_bp = Blueprint('realtime', __name__)

# SocketIO will be initialized in the main app

@realtime_bp.route('/api/realtime/start')
def start_realtime():
    """Start real-time analysis session"""
    try:
        # Start the detector
        detector.start_realtime_analysis(callback=send_result_to_client)
        
        return jsonify({
            'success': True,
            'message': 'Real-time analysis started',
            'session_id': str(int(time.time()))
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/api/realtime/stop')
def stop_realtime():
    """Stop real-time analysis session"""
    try:
        detector.stop_realtime_analysis()
        
        return jsonify({
            'success': True,
            'message': 'Real-time analysis stopped'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/api/realtime/analyze', methods=['POST'])
def analyze_frame():
    """Analyze a single frame"""
    try:
        # Get frame data from request
        data = request.get_json()
        
        if not data or 'frame' not in data:
            return jsonify({
                'success': False,
                'error': 'No frame data provided'
            }), 400
        
        # Decode base64 frame
        frame_data = base64.b64decode(data['frame'].split(',')[1])
        
        # Convert to numpy array
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({
                'success': False,
                'error': 'Invalid frame data'
            }), 400
        
        # Analyze frame
        result = detector.analyze_frame(frame)
        
        if result:
            return jsonify({
                'success': True,
                'result': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Analysis failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@realtime_bp.route('/api/realtime/capture', methods=['POST'])
def capture_and_analyze():
    """Capture and analyze frame with detailed results"""
    try:
        # Get frame data from request
        data = request.get_json()
        
        if not data or 'frame' not in data:
            return jsonify({
                'success': False,
                'error': 'No frame data provided'
            }), 400
        
        # Decode base64 frame
        frame_data = base64.b64decode(data['frame'].split(',')[1])
        
        # Convert to numpy array
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({
                'success': False,
                'error': 'Invalid frame data'
            }), 400
        
        # Analyze frame with detailed processing
        result = detector.analyze_frame(frame)
        
        if result:
            # Add frame quality assessment
            quality_score = assess_frame_quality(frame)
            result['frame_quality'] = quality_score
            
            # Add processing time
            result['processing_time'] = time.time()
            
            return jsonify({
                'success': True,
                'result': result,
                'recommendations': get_recommendations(result)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Analysis failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def assess_frame_quality(frame):
    """Assess the quality of the captured frame"""
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate quality metrics
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Quality assessment
        quality = {
            'blur_score': blur_score,
            'brightness': brightness,
            'contrast': contrast,
            'overall': 'Good'
        }
        
        # Determine overall quality
        if blur_score < 100:
            quality['overall'] = 'Poor'
        elif blur_score < 200:
            quality['overall'] = 'Fair'
        elif brightness < 50 or brightness > 200:
            quality['overall'] = 'Fair'
        elif contrast < 30:
            quality['overall'] = 'Fair'
        else:
            quality['overall'] = 'Excellent'
        
        return quality
    except Exception as e:
        print(f"❌ Error assessing frame quality: {e}")
        return {'overall': 'Unknown'}

def get_recommendations(result):
    """Get recommendations based on analysis result"""
    try:
        risk_level = result.get('risk_level', 'Unknown')
        confidence = result.get('confidence', 0.0)
        
        recommendations = []
        
        if risk_level == 'Low':
            recommendations.extend([
                'Continue regular health monitoring',
                'Maintain balanced diet rich in iron',
                'Stay hydrated and get adequate rest'
            ])
        elif risk_level == 'Medium':
            recommendations.extend([
                'Consider consulting with a healthcare provider',
                'Increase iron-rich foods in your diet',
                'Monitor for symptoms like fatigue or pale skin',
                'Schedule a follow-up screening in 1-2 weeks'
            ])
        elif risk_level == 'High':
            recommendations.extend([
                'Immediate consultation with a healthcare provider recommended',
                'Comprehensive blood work may be necessary',
                'Avoid self-diagnosis and seek professional medical advice',
                'Monitor for severe symptoms like dizziness or shortness of breath'
            ])
        
        # Add confidence-based recommendations
        if confidence < 0.8:
            recommendations.append('Consider retaking the screening for better accuracy')
        
        return recommendations
    except Exception as e:
        print(f"❌ Error generating recommendations: {e}")
        return ['Unable to generate recommendations at this time']

def send_result_to_client(result):
    """Send result to connected clients via WebSocket"""
    try:
        # This function will be called from app.py
        # The actual socketio.emit will be handled in the main app
        pass
    except Exception as e:
        print(f"❌ Error sending result to client: {e}")
