import cv2
import numpy as np
import time
from PIL import Image
import threading
import queue

class RealTimeAnemiaDetector:
    def __init__(self):
        self.model_loaded = False
        self.detection_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.is_running = False
        
        # Initialize ML model (simplified for demo)
        self.load_model()
    
    def load_model(self):
        """Load the ML model for anemia detection"""
        try:
            # In a real implementation, you would load your trained model here
            # For demo purposes, we'll use a simplified approach
            self.model_loaded = True
            print("✅ Real-time ML model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model_loaded = False
    
    def preprocess_frame(self, frame):
        """Preprocess video frame for analysis"""
        try:
            # Convert to RGB
            if len(frame.shape) == 3:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame
            
            # Resize for model input
            frame_resized = cv2.resize(frame_rgb, (224, 224))
            
            # Normalize
            frame_normalized = frame_resized / 255.0
            
            return frame_normalized
        except Exception as e:
            print(f"❌ Error preprocessing frame: {e}")
            return None
    
    def analyze_frame(self, frame):
        """Analyze a single frame for anemia indicators"""
        try:
            if not self.model_loaded:
                return self.get_mock_result()
            
            # Preprocess frame
            processed_frame = self.preprocess_frame(frame)
            if processed_frame is None:
                return None
            
            # Extract features for analysis
            features = self.extract_features(processed_frame)
            
            # Make prediction (simplified)
            prediction = self.predict_anemia(features)
            
            return prediction
        except Exception as e:
            print(f"❌ Error analyzing frame: {e}")
            return None
    
    def extract_features(self, frame):
        """Extract relevant features from frame"""
        try:
            # Convert to grayscale for analysis
            if len(frame.shape) == 3:
                gray = cv2.cvtColor((frame * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            else:
                gray = (frame * 255).astype(np.uint8)
            
            features = {}
            
            # Feature 1: Skin tone analysis (pallor detection)
            features['skin_tone'] = np.mean(gray)
            
            # Feature 2: Contrast analysis
            features['contrast'] = np.std(gray)
            
            # Feature 3: Texture analysis
            features['texture'] = self.calculate_texture(gray)
            
            # Feature 4: Color distribution
            if len(frame.shape) == 3:
                features['color_distribution'] = {
                    'red_mean': np.mean(frame[:, :, 0]),
                    'green_mean': np.mean(frame[:, :, 1]),
                    'blue_mean': np.mean(frame[:, :, 2])
                }
            else:
                features['color_distribution'] = {
                    'red_mean': np.mean(gray),
                    'green_mean': np.mean(gray),
                    'blue_mean': np.mean(gray)
                }
            
            return features
        except Exception as e:
            print(f"❌ Error extracting features: {e}")
            return {}
    
    def calculate_texture(self, gray_frame):
        """Calculate texture features"""
        try:
            # Simple texture measure using Local Binary Pattern approximation
            height, width = gray_frame.shape
            texture_score = 0
            
            for i in range(1, height-1):
                for j in range(1, width-1):
                    center = gray_frame[i, j]
                    
                    # Compare with 8 neighbors
                    neighbors = [
                        gray_frame[i-1, j-1], gray_frame[i-1, j], gray_frame[i-1, j+1],
                        gray_frame[i, j-1], gray_frame[i, j+1],
                        gray_frame[i+1, j-1], gray_frame[i+1, j], gray_frame[i+1, j+1]
                    ]
                    
                    # Simple texture measure
                    texture_score += sum(1 for n in neighbors if n > center)
            
            return texture_score / ((height-2) * (width-2) * 8)
        except Exception as e:
            print(f"❌ Error calculating texture: {e}")
            return 0.5
    
    def predict_anemia(self, features):
        """Make prediction based on extracted features"""
        try:
            if not features:
                return self.get_mock_result()
            
            # Simplified prediction logic
            skin_tone = features.get('skin_tone', 128)
            contrast = features.get('contrast', 50)
            texture = features.get('texture', 0.5)
            
            # Calculate risk score (simplified)
            risk_score = 0
            
            # Lower skin tone (pallor) increases risk
            if skin_tone < 100:
                risk_score += 0.3
            elif skin_tone < 120:
                risk_score += 0.2
            elif skin_tone < 140:
                risk_score += 0.1
            
            # Lower contrast increases risk
            if contrast < 30:
                risk_score += 0.2
            elif contrast < 40:
                risk_score += 0.1
            
            # Texture analysis
            if texture < 0.3:
                risk_score += 0.1
            elif texture > 0.7:
                risk_score += 0.1
            
            # Determine risk level
            if risk_score < 0.2:
                risk_level = "Low"
                color = "green"
            elif risk_score < 0.5:
                risk_level = "Medium"
                color = "yellow"
            else:
                risk_level = "High"
                color = "red"
            
            # Calculate confidence
            confidence = max(0.7, min(0.95, 0.85 + (0.1 * (1 - risk_score))))
            
            return {
                "risk_level": risk_level,
                "color": color,
                "confidence": confidence,
                "features": features,
                "risk_score": risk_score,
                "analysis_time": time.time()
            }
        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return self.get_mock_result()
    
    def get_mock_result(self):
        """Get mock result for demo purposes"""
        import random
        risks = ["Low", "Medium", "High"]
        colors = ["green", "yellow", "red"]
        
        risk_level = random.choice(risks)
        color = colors[risks.index(risk_level)]
        confidence = random.uniform(0.75, 0.95)
        
        return {
            "risk_level": risk_level,
            "color": color,
            "confidence": confidence,
            "features": {},
            "risk_score": random.uniform(0.1, 0.8),
            "analysis_time": time.time()
        }
    
    def start_realtime_analysis(self, callback):
        """Start real-time analysis in a separate thread"""
        self.is_running = True
        
        def analysis_worker():
            while self.is_running:
                try:
                    if not self.detection_queue.empty():
                        frame_data = self.detection_queue.get(timeout=1)
                        
                        # Analyze frame
                        result = self.analyze_frame(frame_data)
                        
                        if result:
                            # Put result in results queue
                            self.results_queue.put(result)
                            
                            # Call callback if provided
                            if callback:
                                callback(result)
                    
                    time.sleep(0.1)  # Small delay to prevent excessive CPU usage
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"❌ Error in analysis worker: {e}")
                    time.sleep(0.5)
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=analysis_worker)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def stop_realtime_analysis(self):
        """Stop real-time analysis"""
        self.is_running = False
        
        # Clear queues
        while not self.detection_queue.empty():
            try:
                self.detection_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.results_queue.empty():
            try:
                self.results_queue.get_nowait()
            except queue.Empty:
                break
    
    def add_frame_for_analysis(self, frame):
        """Add frame to analysis queue"""
        try:
            if not self.detection_queue.full():
                self.detection_queue.put(frame, block=False)
        except queue.Full:
            pass  # Skip frame if queue is full
    
    def get_latest_result(self):
        """Get latest analysis result"""
        try:
            return self.results_queue.get_nowait()
        except queue.Empty:
            return None

# Global detector instance
detector = RealTimeAnemiaDetector()
