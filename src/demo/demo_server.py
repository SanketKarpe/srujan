"""
Standalone Demo Server - No dependencies on Srujan lib
Run this to test the dashboard without Raspberry Pi or Elasticsearch
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
from datetime import datetime
import random
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.routes import ids

app = FastAPI(title="Srujan Demo Server", version="1.0.0-demo")

# Register IDS router
app.include_router(ids.router, prefix="/api/v1/ids", tags=["ids"])

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load mock data
mock_data_path = Path(__file__).parent / "mock_data.json"

try:
    with open(mock_data_path, 'r') as f:
        MOCK_DATA = json.load(f)
    print(f"✅ Loaded mock data: {len(MOCK_DATA.get('devices', []))} devices")
except FileNotFoundError:
    print("⚠️  mock_data.json not found, using minimal data")
    MOCK_DATA = {
        "devices": [],
        "threats": [],
        "ml_alerts": [],
        "network_stats": {}
    }

@app.get("/")
async def root():
    return {
        "name": "Srujan Demo Server",
        "version": "1.0.0-demo",
        "mode": "DEMO",
        "endpoints": [
            "/api/v1/devices",
            "/api/v1/network/stats",
            "/api/v1/threats/recent",
            "/api/v1/ml/alerts",
            "/api/v1/ml/insights/{mac}",
            "/docs"
        ]
    }

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "mode": "DEMO"}

@app.get("/api/v1/devices")
async def get_devices():
    devices = MOCK_DATA.get("devices", [])
    return {"devices": devices, "total": len(devices)}

@app.get("/api/v1/devices/{mac}")
async def get_device(mac: str):
    devices = MOCK_DATA.get("devices", [])
    device = next((d for d in devices if d["mac"] == mac), None)
    if device:
        return device
    return {"error": "Device not found"}

@app.post("/api/v1/devices/{mac}/block")
async def block_device(mac: str):
    return {"status": "success", "message": f"Device {mac} blocked (demo mode)"}

@app.post("/api/v1/devices/{mac}/allow")
async def allow_device(mac: str):
    return {"status": "success", "message": f"Device {mac} allowed (demo mode)"}

@app.get("/api/v1/network/stats")
async def get_stats():
    stats = MOCK_DATA.get("network_stats", {})
    if not stats:
        # Generate minimal stats
        devices = MOCK_DATA.get("devices", [])
        stats = {
            "timestamp": datetime.now().isoformat(),
            "devices": {
                "total": len(devices),
                "active": len(devices),
                "blocked": 0,
                "new_today": 0
            },
            "security": {
                "threats_today": len(MOCK_DATA.get("threats", [])),
                "threats_blocked": len(MOCK_DATA.get("threats", [])),
                "gsb_enabled": True
            }
        }
    return stats

@app.get("/api/v1/threats/recent")
async def get_threats():
    threats = MOCK_DATA.get("threats", [])
    return {"threats": threats, "total": len(threats)}

@app.get("/api/v1/ml/alerts")
async def get_ml_alerts():
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

@app.get("/api/v1/ml/insights/{mac}")
async def get_ml_insights(mac: str):
    # Generate random but realistic insights
    is_anomaly = random.choice([True, False, False])
    
    if is_anomaly:
        risk_level = random.choice(["critical", "high", "medium"])
        risk_score = random.randint(70, 95)
        anomaly_score = random.uniform(-0.5, -0.2)
        confidence = random.randint(75, 95)
    else:
        risk_level = "low"
        risk_score = random.randint(10, 40)
        anomaly_score = random.uniform(-0.1, 0.3)
        confidence = random.randint(60, 85)
    
    return {
        "mac": mac,
        "current_behavior": {
            "dns_query_count": random.randint(50, 500),
            "unique_domains": random.randint(10, 100),
            "dns_diversity": round(random.uniform(0.1, 0.9), 2),
            "threat_count": random.randint(0, 3),
            "threat_ratio": round(random.uniform(0, 0.1), 3),
            "domain_entropy": round(random.uniform(3.0, 5.0), 2),
            "connection_count": random.randint(20, 300),
            "unique_ips": random.randint(5, 50),
            "ip_diversity": round(random.uniform(0.2, 0.8), 2),
            "external_connections": random.randint(10, 200),
            "external_ratio": round(random.uniform(0.3, 0.9), 2)
        },
        "anomaly_detection": {
            "success": True,
            "is_anomaly": is_anomaly,
            "anomaly_score": round(anomaly_score, 4),
            "confidence": confidence,
            "risk_level": risk_level
        },
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recent_anomalies_count": random.randint(0, 10),
        "recommendations": [
            {
                "severity": "high" if is_anomaly else "info",
                "title": "Unusual Behavior Detected" if is_anomaly else "Normal Behavior",
                "description": "Device is exhibiting abnormal patterns" if is_anomaly else "Device is operating normally",
                "action": "Consider quarantining temporarily" if is_anomaly else "No action required"
            }
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/ml/models")
async def get_ml_models():
    return {"models": [], "total": 0}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🎭 SRUJAN DEMO SERVER")
    print("="*60)
    print(f"📊 Loaded {len(MOCK_DATA.get('devices', []))} devices")
    print(f"⚠️  {len(MOCK_DATA.get('threats', []))} threats")
    print(f"🤖 {len(MOCK_DATA.get('ml_alerts', []))} ML alerts")
    print("\n🌐 Starting server...")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("\n💡 Frontend: Start with 'cd web && npm run dev'")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
