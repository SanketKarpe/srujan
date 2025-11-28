"""
Anomaly Detection using Machine Learning
Detects unusual device behavior patterns
"""
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib
import os
from pathlib import Path
from datetime import datetime
import json


class AnomalyDetector:
    def __init__(self, model_dir='models'):
        """
        Initialize anomaly detector
        
        Args:
            model_dir: Directory to store trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.models = {}  # MAC -> model mapping
        self.scalers = {}  # MAC -> scaler mapping
        
        # Model hyperparameters
        self.contamination = 0.1  # Expected proportion of anomalies
        self.random_state = 42
        
    def train_model(self, mac, feature_history):
        """
        Train anomaly detection model for a device
        
        Args:
            mac: Device MAC address
            feature_history: List of feature vectors (numpy arrays)
            
        Returns:
            dict: Training results
        """
        if len(feature_history) < 10:
            return {
                'success': False,
                'error': 'Insufficient data for training (need at least 10 samples)'
            }
        
        # Convert to numpy array
        X = np.array(feature_history)
        
        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train Isolation Forest
        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples='auto',
            bootstrap=False
        )
        
        model.fit(X_scaled)
        
        # Store model and scaler
        self.models[mac] = model
        self.scalers[mac] = scaler
        
        # Save to disk
        self._save_model(mac, model, scaler)
        
        # Validate on training data
        predictions = model.predict(X_scaled)
        scores = model.score_samples(X_scaled)
        
        normal_count = np.sum(predictions == 1)
        anomaly_count = np.sum(predictions == -1)
        
        return {
            'success': True,
            'mac': mac,
            'samples_trained': len(X),
            'normal_count': int(normal_count),
            'anomaly_count': int(anomaly_count),
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores)),
            'trained_at': datetime.now().isoformat()
        }
    
    def detect_anomaly(self, mac, current_features):
        """
        Detect if current behavior is anomalous
        
        Args:
            mac: Device MAC address
            current_features: Current feature vector (numpy array)
            
        Returns:
            dict: Detection results
        """
        # Load model if not in memory
        if mac not in self.models:
            loaded = self._load_model(mac)
            if not loaded:
                return {
                    'success': False,
                    'error': 'No trained model found for device'
                }
        
        model = self.models[mac]
        scaler = self.scalers[mac]
        
        # Scale features
        X = current_features.reshape(1, -1)
        X_scaled = scaler.transform(X)
        
        # Predict
        prediction = model.predict(X_scaled)[0]
        score = model.score_samples(X_scaled)[0]
        
        # Calculate confidence
        # Score ranges from ~-0.5 (anomaly) to ~0.5 (normal)
        # Convert to 0-100 confidence scale
        confidence = self._calculate_confidence(score)
        
        is_anomaly = prediction == -1
        
        return {
            'success': True,
            'is_anomaly': bool(is_anomaly),
            'anomaly_score': float(score),
            'confidence': confidence,
            'risk_level': self._get_risk_level(score, is_anomaly),
            'detected_at': datetime.now().isoformat()
        }
    
    def _calculate_confidence(self, score):
        """
        Convert anomaly score to confidence percentage
        
        Args:
            score: Anomaly score from model
            
        Returns:
            int: Confidence (0-100)
        """
        # Isolation Forest scores typically range from -0.5 to 0.5
        # More negative = more anomalous
        # Map to 0-100 where 100 = very confident it's anomalous
        
        # Normalize score to 0-1 range
        normalized = (score + 0.5) / 1.0
        
        # Convert to confidence (inverse for anomalies)
        confidence = int((1 - normalized) * 100)
        
        return max(0, min(100, confidence))
    
    def _get_risk_level(self, score, is_anomaly):
        """
        Determine risk level based on anomaly score
        
        Args:
            score: Anomaly score
            is_anomaly: Whether flagged as anomaly
            
        Returns:
            str: Risk level (low, medium, high, critical)
        """
        if not is_anomaly:
            return 'low'
        
        # More negative = higher risk
        if score < -0.4:
            return 'critical'
        elif score < -0.3:
            return 'high'
        elif score < -0.2:
            return 'medium'
        else:
            return 'low'
    
    def _save_model(self, mac, model, scaler):
        """Save model and scaler to disk"""
        model_path = self.model_dir / f"{mac.replace(':', '_')}_model.pkl"
        scaler_path = self.model_dir / f"{mac.replace(':', '_')}_scaler.pkl"
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        # Save metadata
        metadata = {
            'mac': mac,
            'saved_at': datetime.now().isoformat(),
            'contamination': self.contamination
        }
        
        metadata_path = self.model_dir / f"{mac.replace(':', '_')}_meta.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def _load_model(self, mac):
        """Load model and scaler from disk"""
        model_path = self.model_dir / f"{mac.replace(':', '_')}_model.pkl"
        scaler_path = self.model_dir / f"{mac.replace(':', '_')}_scaler.pkl"
        
        if not model_path.exists() or not scaler_path.exists():
            return False
        
        try:
            self.models[mac] = joblib.load(model_path)
            self.scalers[mac] = joblib.load(scaler_path)
            return True
        except Exception as e:
            print(f"Error loading model for {mac}: {e}")
            return False
    
    def get_trained_models(self):
        """Get list of devices with trained models"""
        models = []
        
        for metadata_file in self.model_dir.glob("*_meta.json"):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    models.append(metadata)
            except:
                continue
        
        return models


class AnomalyTracker:
    """Track anomalies over time for reporting"""
    
    def __init__(self, db_path='anomalies.json'):
        self.db_path = Path(db_path)
        self.anomalies = self._load_anomalies()
    
    def _load_anomalies(self):
        """Load anomalies from disk"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_anomalies(self):
        """Save anomalies to disk"""
        with open(self.db_path, 'w') as f:
            json.dump(self.anomalies, f, indent=2)
    
    def record_anomaly(self, mac, detection_result, features):
        """Record an anomaly detection"""
        anomaly = {
            'mac': mac,
            'detected_at': detection_result['detected_at'],
            'anomaly_score': detection_result['anomaly_score'],
            'confidence': detection_result['confidence'],
            'risk_level': detection_result['risk_level'],
            'features': features.tolist() if isinstance(features, np.ndarray) else features,
            'false_positive': False  # Can be updated by user
        }
        
        self.anomalies.append(anomaly)
        self._save_anomalies()
    
    def get_recent_anomalies(self, mac=None, hours=24, limit=100):
        """Get recent anomalies"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        filtered = [
            a for a in self.anomalies
            if (mac is None or a['mac'] == mac) and
               datetime.fromisoformat(a['detected_at']) > cutoff
        ]
        
        # Sort by time (most recent first)
        filtered.sort(key=lambda x: x['detected_at'], reverse=True)
        
        return filtered[:limit]
    
    def mark_false_positive(self, anomaly_id):
        """Mark an anomaly as false positive"""
        if 0 <= anomaly_id < len(self.anomalies):
            self.anomalies[anomaly_id]['false_positive'] = True
            self._save_anomalies()
            return True
        return False


if __name__ == "__main__":
    from datetime import timedelta
    
    # Test anomaly detection
    detector = AnomalyDetector()
    
    # Generate synthetic training data (normal behavior)
    np.random.seed(42)
    normal_data = np.random.randn(50, 11) * 0.5 + 5  # 50 samples, 11 features
    
    # Train model
    print("Training model...")
    result = detector.train_model("test:mac:address", normal_data)
    print(json.dumps(result, indent=2))
    
    # Test with normal data
    print("\nTesting with normal data...")
    test_normal = np.random.randn(11) * 0.5 + 5
    detection = detector.detect_anomaly("test:mac:address", test_normal)
    print(json.dumps(detection, indent=2))
    
    # Test with anomalous data
    print("\nTesting with anomalous data...")
    test_anomaly = np.random.randn(11) * 2 + 15  # Very different pattern
    detection = detector.detect_anomaly("test:mac:address", test_anomaly)
    print(json.dumps(detection, indent=2))
