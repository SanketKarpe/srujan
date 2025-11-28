"""
ML API Routes for Srujan
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add ml directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'ml'))

from feature_extractor import FeatureExtractor
from anomaly_detector import AnomalyDetector, AnomalyTracker

router = APIRouter(prefix="/api/v1/ml", tags=["ml"])

# Initialize ML components
feature_extractor = FeatureExtractor()
anomaly_detector = AnomalyDetector(model_dir='ml_models')
anomaly_tracker = AnomalyTracker(db_path='data/anomalies.json')

@router.get("/insights/{mac}")
async def get_ml_insights(mac: str):
    """Get ML insights for a specific device"""
    try:
        # Get current features
        current_features = feature_extractor.extract_device_features(mac, hours=1)
        feature_vector = feature_extractor.get_feature_vector(current_features)
        
        # Get baseline
        baseline = feature_extractor.build_baseline(mac, days=7)
        
        # Check for anomaly
        detection = anomaly_detector.detect_anomaly(mac, feature_vector)
        
        # Calculate risk score (0-100)
        risk_score = 0
        if detection.get('success'):
            if detection['is_anomaly']:
                risk_score = detection['confidence']
            else:
                risk_score = max(0, 100 - detection['confidence'])
        
        # Get recent anomalies for this device
        recent_anomalies = anomaly_tracker.get_recent_anomalies(mac=mac, hours=168)  # 1 week
        
        # Generate recommendations
        recommendations = _generate_recommendations(current_features, detection, recent_anomalies)
        
        return {
            'mac': mac,
            'current_behavior': current_features,
            'baseline': baseline,
            'anomaly_detection': detection,
            'risk_score': risk_score,
            'risk_level': detection.get('risk_level', 'unknown') if detection.get('success') else 'unknown',
            'recent_anomalies_count': len(recent_anomalies),
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_ml_alerts(hours: int = 24, limit: int = 100):
    """Get ML-detected anomalies"""
    try:
        anomalies = anomaly_tracker.get_recent_anomalies(hours=hours, limit=limit)
        
        # Group by risk level
        by_risk = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for anomaly in anomalies:
            risk_level = anomaly.get('risk_level', 'low')
            by_risk[risk_level] = by_risk.get(risk_level, 0) + 1
        
        return {
            'alerts': anomalies,
            'total': len(anomalies),
            'by_risk_level': by_risk,
            'false_positives': sum(1 for a in anomalies if a.get('false_positive', False))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/train")
async def train_models(background_tasks: BackgroundTasks):
    """Trigger ML model training for all devices"""
    background_tasks.add_task(_train_all_models)
    return {
        'status': 'started',
        'message': 'Model training started in background'
    }

@router.get("/models")
async def list_trained_models():
    """List all trained models"""
    try:
        models = anomaly_detector.get_trained_models()
        return {
            'models': models,
            'total': len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback/{anomaly_id}")
async def mark_false_positive(anomaly_id: int):
    """Mark an anomaly as false positive"""
    try:
        success = anomaly_tracker.mark_false_positive(anomaly_id)
        if success:
            return {'status': 'success', 'message': 'Marked as false positive'}
        else:
            raise HTTPException(status_code=404, detail='Anomaly not found')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _train_all_models():
    """Background task to train models for all devices"""
    print("Starting model training for all devices...")
    
    # Get all devices from API
    # For now, we'll use a placeholder
    # In production, this would query the devices endpoint
    
    # TODO: Implement full training loop
    # 1. Get list of all devices
    # 2. For each device:
    #    - Collect historical features (7 days)
    #    - Train model
    #    - Save model
    
    print("Model training complete")

def _generate_recommendations(features, detection, recent_anomalies):
    """Generate security recommendations based on ML analysis"""
    recommendations = []
    
    if detection.get('success') and detection.get('is_anomaly'):
        recommendations.append({
            'severity': 'high',
            'title': 'Unusual Behavior Detected',
            'description': f"Device is exhibiting abnormal patterns with {detection['confidence']}% confidence",
            'action': 'Consider quarantining this device temporarily'
        })
    
    if features.get('threat_count', 0) > 0:
        recommendations.append({
            'severity': 'critical',
            'title': 'Malicious Connections Detected',
            'description': f"{features['threat_count']} connections to known malicious domains",
            'action': 'Block this device immediately'
        })
    
    if features.get('domain_entropy', 0) > 4.5:
        recommendations.append({
            'severity': 'medium',
            'title': 'Possible DGA Activity',
            'description': 'High domain name entropy may indicate Domain Generation Algorithm usage',
            'action': 'Monitor DNS queries closely'
        })
    
    if features.get('external_ratio', 0) > 0.8:
        recommendations.append({
            'severity': 'low',
            'title': 'High External Traffic',
            'description': 'Most connections are to external IPs',
            'action': 'Verify this is expected behavior for this device type'
        })
    
    if len(recent_anomalies) > 10:
        recommendations.append({
            'severity': 'high',
            'title': 'Frequent Anomalies',
            'description': f'{len(recent_anomalies)} anomalies in the past week',
            'action': 'Device may be compromised - investigate thoroughly'
        })
    
    if not recommendations:
        recommendations.append({
            'severity': 'info',
            'title': 'Normal Behavior',
            'description': 'Device is operating within normal parameters',
            'action': 'No action required'
        })
    
    return recommendations
