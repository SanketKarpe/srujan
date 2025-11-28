"""
Demo Mode API - Returns mock data for testing without Raspberry Pi
Set environment variable DEMO_MODE=true to enable
"""
from fastapi import APIRouter, Query
from typing import Optional
import os
import json
from pathlib import Path
from datetime import datetime
import random

router = APIRouter(prefix="/api/v1/demo", tags=["demo"])

# Load mock data
mock_data_path = Path(__file__).parent.parent.parent / "demo" / "mock_data.json"

def load_mock_data():
    """Load mock data from JSON file"""
    if mock_data_path.exists():
        with open(mock_data_path, 'r') as f:
            return json.load(f)
    return generate_inline_mock_data()

def generate_inline_mock_data():
    """Generate mock data inline if file doesn't exist"""
    return {
        "devices": [
            {
                "mac": "aa:bb:cc:dd:ee:01",
                "ip": f"192.168.1.{10+i}",
                "hostname": f"device-{i+1}",
                "manufacturer": random.choice(["Samsung", "Apple", "Google", "Amazon", "TP-Link"]),
                "device_type": "Smart Device",
                "category": random.choice(["iot", "non_iot"]),
                "status": "active",
                "last_seen": datetime.now().isoformat()
            }
            for i in range(15)
        ],
        "threats": [],
        "ml_alerts": [],
        "network_stats": {
            "timestamp": datetime.now().isoformat(),
            "devices": {"total": 15, "active": 14, "blocked": 1, "new_today": 2},
            "security": {"threats_today": 3, "threats_blocked": 3, "gsb_enabled": True}
        }
    }

# Load data once at startup
MOCK_DATA = load_mock_data()

@router.get("/devices")
async def get_demo_devices():
    """Get mock device list"""
    return {
        "devices": MOCK_DATA.get("devices", []),
        "total": len(MOCK_DATA.get("devices", []))
    }

@router.get("/devices/{mac}")
async def get_demo_device(mac: str):
    """Get specific mock device"""
    devices = MOCK_DATA.get("devices", [])
    device = next((d for d in devices if d["mac"] == mac), None)
    if device:
        return device
    return {"error": "Device not found"}

@router.get("/network/stats")
async def get_demo_stats():
    """Get mock network statistics"""
    return MOCK_DATA.get("network_stats", {})

@router.get("/threats/recent")
async def get_demo_threats():
    """Get mock threats"""
    return {
        "threats": MOCK_DATA.get("threats", []),
        "total": len(MOCK_DATA.get("threats", []))
    }

@router.get("/ml/alerts")
async def get_demo_ml_alerts():
    """Get mock ML alerts"""
    alerts = MOCK_DATA.get("ml_alerts", [])
    
    by_risk = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for alert in alerts:
        by_risk[alert.get("risk_level", "low")] += 1
    
    return {
        "alerts": alerts,
        "total": len(alerts),
        "by_risk_level": by_risk,
        "false_positives": sum(1 for a in alerts if a.get("false_positive", False))
    }

@router.get("/ml/insights/{mac}")
async def get_demo_ml_insights(mac: str):
    """Get mock ML insights for device"""
    # Generate random but realistic insights
    is_anomaly = random.choice([True, False, False])
    
    return {
        "mac": mac,
        "current_behavior": {
            "dns_query_count": random.randint(50, 500),
            "unique_domains": random.randint(10, 100),
            "dns_diversity": random.uniform(0.1, 0.9),
            "threat_count": random.randint(0, 3),
            "threat_ratio": random.uniform(0, 0.1),
            "domain_entropy": random.uniform(3.0, 5.0),
            "connection_count": random.randint(20, 300),
            "unique_ips": random.randint(5, 50),
            "ip_diversity": random.uniform(0.2, 0.8),
            "external_connections": random.randint(10, 200),
            "external_ratio": random.uniform(0.3, 0.9)
        },
        "anomaly_detection": {
            "success": True,
            "is_anomaly": is_anomaly,
            "anomaly_score": random.uniform(-0.5, 0.3),
            "confidence": random.randint(60, 95),
            "risk_level": "high" if is_anomaly else "low"
        },
        "risk_score": random.randint(70, 90) if is_anomaly else random.randint(10, 40),
        "risk_level": "high" if is_anomaly else "low",
        "recent_anomalies_count": random.randint(0, 10),
        "recommendations": [
            {
                "severity": "high" if is_anomaly else "info",
                "title": "Unusual Behavior Detected" if is_anomaly else "Normal Behavior",
                "description": "Device is exhibiting abnormal patterns" if is_anomaly else "Device is operating normally",
                "action": "Consider quarantining" if is_anomaly else "No action required"
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.post("/generate")
async def generate_new_mock_data(num_devices: int = 20):
    """Generate new mock data"""
    # This would call the mock_data_generator script
    return {
        "status": "success",
        "message": f"Generated new mock data with {num_devices} devices"
    }
