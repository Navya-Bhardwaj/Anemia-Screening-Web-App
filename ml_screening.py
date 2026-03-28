import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import os
import pickle

class AnemiaScreeningML:
    def __init__(self):
        """Initialize the ML screening model"""
        self.model = None
        self.scaler = StandardScaler()
        self.feature_extractor = None
        self.load_model()
    
    def load_model(self):
        """Load or create the ML model"""
        try:
            # Try to load existing model
            if os.path.exists('models/anemia_model.h5'):
                self.model = tf.keras.models.load_model('models/anemia_model.h5')
                print("✅ Loaded existing ML model")
            else:
                # Create a new model if none exists
                self.create_model()
                print("🆕 Created new ML model")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.create_model()
    
    def create_model(self):
        """Create a CNN model for anemia detection"""
        # Create models directory if it doesn't exist
        os.makedirs('models', exist_ok=True)
        
        # Build a simple CNN model
        self.model = tf.keras.Sequential([
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(128, 128, 3)),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(3, activation='softmax')  # 3 classes: Low, Medium, High risk
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # Save the model
        self.model.save('models/anemia_model.h5')
        print("✅ Created and saved new ML model")
    
    def extract_features(self, image_path):
        """Extract features from image for analysis"""
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Convert to different color spaces
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            features = {}
            
            # Color features
            features['mean_bgr'] = np.mean(image, axis=(0, 1))
            features['std_bgr'] = np.std(image, axis=(0, 1))
            features['mean_hsv'] = np.mean(hsv, axis=(0, 1))
            features['std_hsv'] = np.std(hsv, axis=(0, 1))
            features['mean_lab'] = np.mean(lab, axis=(0, 1))
            features['std_lab'] = np.std(lab, axis=(0, 1))
            
            # Texture features
            features['mean_gray'] = np.mean(gray)
            features['std_gray'] = np.std(gray)
            features['brightness'] = features['mean_gray']
            
            # Pallor detection features
            features['pallor_ratio'] = self.calculate_pallor_ratio(image)
            features['conjunctival_pallor'] = self.detect_conjunctival_pallor(image)
            features['nail_pallor'] = self.detect_nail_pallor(image)
            
            # Statistical features
            features['skewness'] = self.calculate_skewness(gray)
            features['kurtosis'] = self.calculate_kurtosis(gray)
            
            return features
            
        except Exception as e:
            print(f"❌ Feature extraction error: {e}")
            return None
    
    def calculate_pallor_ratio(self, image):
        """Calculate pallor ratio based on color intensity"""
        # Convert to HSV and extract value channel
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        value_channel = hsv[:, :, 2]
        
        # Calculate ratio of low intensity pixels
        low_intensity = np.sum(value_channel < 100)
        total_pixels = value_channel.size
        pallor_ratio = low_intensity / total_pixels
        
        return pallor_ratio
    
    def detect_conjunctival_pallor(self, image):
        """Detect conjunctival pallor (eye pallor)"""
        # This is a simplified detection
        # In practice, you'd need more sophisticated eye detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for pale regions in the image
        pale_regions = gray < 120
        pallor_percentage = np.sum(pale_regions) / pale_regions.size
        
        return pallor_percentage
    
    def detect_nail_pallor(self, image):
        """Detect nail bed pallor"""
        # Simplified nail pallor detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Extract saturation and value
        saturation = hsv[:, :, 1]
        value = hsv[:, :, 2]
        
        # Low saturation and high value indicates pallor
        pallor_mask = (saturation < 30) & (value > 150)
        pallor_percentage = np.sum(pallor_mask) / pallor_mask.size
        
        return pallor_percentage
    
    def calculate_skewness(self, gray_image):
        """Calculate skewness of the image histogram"""
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        # Calculate skewness
        mean = np.mean(gray_image)
        std = np.std(gray_image)
        skewness = np.mean(((gray_image - mean) / std) ** 3)
        
        return skewness
    
    def calculate_kurtosis(self, gray_image):
        """Calculate kurtosis of the image histogram"""
        mean = np.mean(gray_image)
        std = np.std(gray_image)
        kurtosis = np.mean(((gray_image - mean) / std) ** 4) - 3
        
        return kurtosis
    
    def predict_anemia_risk(self, image_path):
        """Predict anemia risk using ML model"""
        try:
            # Extract features
            features = self.extract_features(image_path)
            if features is None:
                return self.fallback_analysis(image_path)
            
            # Prepare features for model input
            feature_vector = np.array([
                features['brightness'],
                features['pallor_ratio'],
                features['conjunctival_pallor'],
                features['nail_pallor'],
                features['skewness'],
                features['kurtosis']
            ]).reshape(1, -1)
            
            # Since we don't have a trained model, use rule-based classification
            risk_level = self.rule_based_classification(features)
            
            return risk_level
            
        except Exception as e:
            print(f"❌ ML prediction error: {e}")
            return self.fallback_analysis(image_path)
    
    def rule_based_classification(self, features):
        """Rule-based classification as fallback"""
        brightness = features['brightness']
        pallor_ratio = features['pallor_ratio']
        conjunctival_pallor = features['conjunctival_pallor']
        nail_pallor = features['nail_pallor']
        
        # Calculate risk score
        risk_score = 0
        
        # Brightness factor (lower = more pale)
        if brightness < 100:
            risk_score += 3
        elif brightness < 150:
            risk_score += 2
        else:
            risk_score += 1
        
        # Pallor ratio factor
        if pallor_ratio > 0.4:
            risk_score += 3
        elif pallor_ratio > 0.25:
            risk_score += 2
        else:
            risk_score += 1
        
        # Conjunctival pallor factor
        if conjunctival_pallor > 0.3:
            risk_score += 2
        else:
            risk_score += 1
        
        # Nail pallor factor
        if nail_pallor > 0.3:
            risk_score += 2
        else:
            risk_score += 1
        
        # Determine risk level
        if risk_score >= 8:
            return {
                "risk_level": "High Risk",
                "message": "High likelihood of anemia detected. Please consult a healthcare professional immediately.",
                "color": "red",
                "confidence": min(0.95, 0.6 + (risk_score - 8) * 0.1),
                "risk_score": risk_score,
                "features": features
            }
        elif risk_score >= 5:
            return {
                "risk_level": "Moderate Risk",
                "message": "Moderate likelihood of anemia. Consider further testing and consultation with a healthcare provider.",
                "color": "orange",
                "confidence": 0.7 + (risk_score - 5) * 0.05,
                "risk_score": risk_score,
                "features": features
            }
        else:
            return {
                "risk_level": "Low Risk",
                "message": "Low likelihood of anemia. Image appears normal, but regular check-ups are recommended.",
                "color": "green",
                "confidence": 0.6 + (4 - risk_score) * 0.05,
                "risk_score": risk_score,
                "features": features
            }
    
    def fallback_analysis(self, image_path):
        """Fallback analysis using basic brightness method"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {
                    "risk_level": "Error",
                    "message": "Error: Unable to process image.",
                    "color": "gray",
                    "confidence": 0.0
                }
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)
            
            if avg_brightness < 100:
                risk_level = "High Risk"
                message = "High likelihood of anemia detected. Please consult a healthcare professional."
                color = "red"
            elif avg_brightness < 150:
                risk_level = "Moderate Risk"
                message = "Moderate likelihood of anemia. Consider further testing."
                color = "orange"
            else:
                risk_level = "Low Risk"
                message = "Low likelihood of anemia. Image appears normal."
                color = "green"
            
            return {
                "risk_level": risk_level,
                "message": message,
                "color": color,
                "confidence": 0.6,
                "brightness": float(avg_brightness)
            }
            
        except Exception as e:
            print(f"❌ Fallback analysis error: {e}")
            return {
                "risk_level": "Error",
                "message": "Error: Unable to process image.",
                "color": "gray",
                "confidence": 0.0
            }

# Global ML instance
ml_screening = AnemiaScreeningML()
