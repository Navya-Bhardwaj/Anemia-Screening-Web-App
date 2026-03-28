#!/usr/bin/env python3
"""
Real-Time Anemia Screening Application
Run this script to start the application with real-time screening support
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, socketio

if __name__ == '__main__':
    print("🚀 Starting Real-Time Anemia Screening Application...")
    print("📱 Real-time screening available at: http://127.0.0.1:5000/screening/realtime")
    print("🎯 Regular screening available at: http://127.0.0.1:5000/screening")
    print("🏠 Home page: http://127.0.0.1:5000/")
    print("⚡ WebSocket enabled for real-time analysis")
    print("\n📋 Features:")
    print("   • Real-time camera-based screening")
    print("   • Live AI analysis with WebSocket")
    print("   • Frame capture and analysis")
    print("   • Modern glassmorphism UI")
    print("   • Mobile responsive design")
    print("\n🔧 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        socketio.run(
            app, 
            debug=True, 
            host='0.0.0.0', 
            port=5000,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
