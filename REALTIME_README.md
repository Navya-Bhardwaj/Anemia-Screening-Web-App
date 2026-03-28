# Real-Time Anemia Screening System

## 🚀 Overview

The Real-Time Anemia Screening system provides instant AI-powered anemia detection using your device's camera. No more uploading images - get live analysis in real-time!

## ✨ Features

### 🎥 Real-Time Camera Analysis
- **Live Video Stream**: Uses device camera for continuous monitoring
- **Instant Results**: AI analysis every 2 seconds
- **Visual Detection**: Shows detection boxes on identified areas
- **Quality Assessment**: Evaluates frame quality for accurate results

### 🤖 Advanced AI Features
- **Machine Learning**: Real-time image processing with OpenCV
- **Feature Extraction**: Analyzes skin tone, contrast, and texture
- **Risk Assessment**: Low/Medium/High risk levels with confidence scores
- **WebSocket Communication**: Real-time data streaming

### 🎨 Modern UI/UX
- **Glassmorphism Design**: Modern, professional interface
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Elements**: Smooth animations and transitions
- **Live Indicators**: Real-time status updates

## 🛠️ Technical Architecture

### Backend Components
```
├── app.py                 # Main Flask application
├── realtime_routes.py     # WebSocket and API routes
├── ml_realtime.py         # Real-time ML processing
└── run_realtime.py        # Startup script
```

### Frontend Components
```
├── screening_realtime.html  # Real-time screening interface
├── modern-style.css         # Modern UI styling
└── Socket.IO client         # Real-time communication
```

### ML Processing Pipeline
1. **Frame Capture**: Video stream → Canvas → Base64
2. **Preprocessing**: Resize, normalize, extract features
3. **Analysis**: Skin tone, contrast, texture detection
4. **Prediction**: Risk level calculation
5. **Results**: Real-time UI updates via WebSocket

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Modern web browser with camera support
- Flask and Socket.IO dependencies

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the real-time server
python run_realtime.py
```

### Access Points
- **Real-Time Screening**: `http://127.0.0.1:5000/screening/realtime`
- **Traditional Screening**: `http://127.0.0.1:5000/screening`
- **Home Page**: `http://127.0.0.1:5000/`

## 📱 How to Use

### 1. Start Real-Time Screening
1. Navigate to `/screening/realtime`
2. Click "Start Screening" button
3. Grant camera permissions when prompted
4. Position yourself in good lighting

### 2. Live Analysis
- **Automatic Detection**: AI analyzes frames every 2 seconds
- **Visual Feedback**: Detection boxes appear on identified areas
- **Live Results**: Risk level and confidence update in real-time
- **Quality Monitoring**: Frame quality assessed continuously

### 3. Capture & Save
- **Capture Frame**: Click "Capture Frame" to save current analysis
- **Save Results**: Save analysis results to your profile
- **New Screening**: Start a new session anytime

## 🔧 Technical Details

### WebSocket Events
```javascript
// Client → Server
socket.emit('start_analysis')     // Start real-time analysis
socket.emit('stop_analysis')      // Stop analysis
socket.emit('frame_data', frame)  // Send frame for analysis

// Server → Client
socket.on('analysis_result', data)  // Receive analysis results
socket.on('error', error)           // Handle errors
```

### ML Features
- **Skin Tone Analysis**: Detects pallor (pale skin)
- **Contrast Measurement**: Evaluates image clarity
- **Texture Analysis**: Assesses skin texture patterns
- **Color Distribution**: RGB channel analysis

### Risk Assessment Algorithm
```python
# Simplified risk calculation
risk_score = 0
if skin_tone < 100: risk_score += 0.3    # Pallor detection
if contrast < 30: risk_score += 0.2      # Low contrast
if texture < 0.3: risk_score += 0.1      # Texture analysis

# Risk levels
if risk_score < 0.2: return "Low"
elif risk_score < 0.5: return "Medium"
else: return "High"
```

## 🎯 Use Cases

### Medical Screening
- **Quick Assessment**: Rapid anemia risk evaluation
- **Remote Monitoring**: Telemedicine applications
- **Health Tracking**: Regular monitoring over time

### Educational Purposes
- **Medical Training**: Demonstration of AI in healthcare
- **Research**: Anemia detection algorithm development
- **Public Health**: Community screening programs

## 🔒 Privacy & Security

- **Local Processing**: Images processed locally, not stored
- **Temporary Storage**: Frames discarded after analysis
- **Secure Connection**: WebSocket encryption
- **User Consent**: Camera permission required

## 🐛 Troubleshooting

### Common Issues

**Camera Not Working**
- Check browser camera permissions
- Ensure camera is not used by other applications
- Try refreshing the page

**Analysis Not Starting**
- Check WebSocket connection in browser console
- Ensure server is running with SocketIO
- Verify network connectivity

**Poor Detection Quality**
- Improve lighting conditions
- Ensure camera is focused
- Keep steady position during analysis

### Debug Mode
```bash
# Run with debug logging
python run_realtime.py --debug
```

## 🚀 Future Enhancements

### Planned Features
- **Mobile App**: Native iOS/Android applications
- **Advanced ML**: Deep learning models
- **Multi-Language**: International support
- **Cloud Processing**: Cloud-based ML analysis

### API Integration
- **EHR Integration**: Electronic health records
- **Doctor Consultation**: Direct specialist connection
- **Health Platforms**: Integration with health apps

## 📞 Support

For technical support or questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Verify server logs for issues
4. Contact development team

---

**Note**: This system is for demonstration purposes and should not replace professional medical diagnosis. Always consult healthcare professionals for medical concerns.
