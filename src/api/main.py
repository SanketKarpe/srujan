"""
Srujan API - FastAPI backend for web dashboard
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.config import *
from lib.utils import mac_to_vendor

# Import ML router
try:
    from api.routes import ml
    ML_ENABLED = True
except ImportError:
    print("Warning: ML module not available")
    ML_ENABLED = False

# Import demo router
try:
    from api.routes import demo
    DEMO_ENABLED = True
    print("✅ Demo mode available at /api/v1/demo")
except ImportError:
    print("Warning: Demo module not available")
    DEMO_ENABLED = False

# Import policy router
try:
    from api.routes import policy
    POLICY_ENABLED = True
    print("✅ Policy engine available at /api/v1/policies")
except ImportError:
    print("Warning: Policy module not available")
    POLICY_ENABLED = False

# Import trust router
try:
    from api.routes import trust
    TRUST_ENABLED = True
    print("✅ Trust scoring available at /api/v1/trust")
except ImportError:
    print("Warning: Trust module not available")
    TRUST_ENABLED = False

# Import IDS router
try:
    from api.routes import ids
    IDS_ENABLED = True
    print("✅ IDS module available at /api/v1/ids")
except ImportError:
    print("Warning: IDS module not available")
    IDS_ENABLED = False

app = FastAPI(
    title="Srujan API",
    description="Network security gateway for smart homes",
    version="1.0.0"
)

# Register ML router if available
if ML_ENABLED:
    app.include_router(ml.router)

# Register demo router if available  
if DEMO_ENABLED:
    app.include_router(demo.router)

# Register policy router if available
if POLICY_ENABLED:
    app.include_router(policy.router)

# Register trust router if available
if TRUST_ENABLED:
    app.include_router(trust.router)
    
# Register IDS router if available
if IDS_ENABLED:
    app.include_router(ids.router, prefix="/api/v1/ids", tags=["ids"])

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

# ==================== Helper Functions ====================

def read_dnsmasq_leases():
    """Read DHCP leases from dnsmasq"""
    devices = []
    lease_file = Path("/var/lib/misc/dnsmasq.leases")
    
    if not lease_file.exists():
        return devices
    
    try:
        with open(lease_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 4:
                    timestamp, mac, ip, hostname = parts[0], parts[1], parts[2], parts[3]
                    
                    devices.append({
                        "mac": mac,
                        "ip": ip,
                        "hostname": hostname if hostname != "*" else None,
                        "manufacturer": mac_to_vendor(mac),
                        "last_seen": datetime.fromtimestamp(int(timestamp)).isoformat(),
                        "status": "active"
                    })
    except Exception as e:
        print(f"Error reading leases: {e}")
    
    return devices

def get_elasticsearch_devices():
    """Get devices from Elasticsearch (mac_ip index)"""
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch([{'host': HOST_ADDR, 'port': ES_PORT}])
        
        # Get recent device data
        result = es.search(
            index="mac_ip",
            body={
                "size": 100,
                "sort": [{"@timestamp": {"order": "desc"}}],
                "query": {"match_all": {}}
            }
        )
        
        devices_map = {}
        for hit in result['hits']['hits']:
            source = hit['_source']
            mac = source.get('mac')
            
            if mac and mac not in devices_map:
                devices_map[mac] = {
                    "mac": mac,
                    "ip": source.get('ip'),
                    "manufacturer": source.get('manufacturer'),
                    "last_seen": source.get('@timestamp'),
                    "status": "active"
                }
        
        return list(devices_map.values())
    except Exception as e:
        print(f"Error getting Elasticsearch devices: {e}")
        return []

def get_threat_count():
    """Get threat count from Google Safe Browsing checks"""
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch([{'host': HOST_ADDR, 'port': ES_PORT}])
        
        result = es.search(
            index="ip_dns",
            body={
                "size": 0,
                "query": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "tags"}},
                            {"range": {"@timestamp": {"gte": "now-24h"}}}
                        ]
                    }
                },
                "aggs": {
                    "threat_count": {"value_count": {"field": "tags"}}
                }
            }
        )
        
        return result['aggregations']['threat_count']['value']
    except Exception as e:
        print(f"Error getting threat count: {e}")
        return 0

# ==================== API Routes ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Srujan API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/devices")
async def list_devices():
    """List all discovered devices"""
    # Try to get devices from multiple sources
    dhcp_devices = read_dnsmasq_leases()
    es_devices = get_elasticsearch_devices()
    
    # Merge devices by MAC address
    devices_map = {}
    
    for device in dhcp_devices + es_devices:
        mac = device['mac']
        if mac in devices_map:
            # Merge data, preferring non-null values
            for key, value in device.items():
                if value and not devices_map[mac].get(key):
                    devices_map[mac][key] = value
        else:
            devices_map[mac] = device
    
    # Add device type based on manufacturer
    for device in devices_map.values():
        manufacturer = device.get('manufacturer', '').lower() if device.get('manufacturer') else ''
        
        # Simple heuristic device type detection
        if any(x in manufacturer for x in ['amazon', 'google', 'apple', 'samsung', 'lg', 'sony']):
            device['device_type'] = 'IoT Device'
            device['category'] = 'iot'
        else:
            device['device_type'] = 'Unknown'
            device['category'] = 'non_iot'
    
    return {
        "devices": list(devices_map.values()),
        "total": len(devices_map)
    }

@app.get("/api/v1/devices/{mac}")
async def get_device(mac: str):
    """Get specific device details"""
    devices = await list_devices()
    
    for device in devices['devices']:
        if device['mac'].lower() == mac.lower():
            return device
    
    raise HTTPException(status_code=404, detail="Device not found")

@app.post("/api/v1/devices/{mac}/block")
async def block_device(mac: str):
    """Block a device"""
    import subprocess
    
    try:
        # Add iptables rule to block device
        result = subprocess.run(
            ["iptables", "-A", "FORWARD", "-m", "mac", "--mac-source", mac, "-j", "DROP"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Broadcast update to all connected clients
            await manager.broadcast({
                "type": "device_blocked",
                "mac": mac,
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "success", "message": f"Device {mac} blocked"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to block device: {result.stderr}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/devices/{mac}/allow")
async def allow_device(mac: str):
    """Allow a blocked device"""
    import subprocess
    
    try:
        # Remove iptables block rule
        result = subprocess.run(
            ["iptables", "-D", "FORWARD", "-m", "mac", "--mac-source", mac, "-j", "DROP"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Broadcast update
            await manager.broadcast({
                "type": "device_allowed",
                "mac": mac,
                "timestamp": datetime.now().isoformat()
            })
            
            return {"status": "success", "message": f"Device {mac} allowed"}
        else:
            # Device might not have been blocked, that's ok
            return {"status": "success", "message": f"Device {mac} already allowed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/network/stats")
async def get_network_stats():
    """Get network statistics"""
    devices = await list_devices()
    total_devices = devices['total']
    
    # Count active vs inactive
    active_count = sum(1 for d in devices['devices'] if d.get('status') == 'active')
    
    # Get threat count
    threats_today = get_threat_count()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "devices": {
            "total": total_devices,
            "active": active_count,
            "blocked": 0,  # TODO: Track blocked devices
            "new_today": 0  # TODO: Track new devices
        },
        "security": {
            "threats_today": threats_today,
            "threats_blocked": threats_today,  # Assuming all detected are blocked
            "gsb_enabled": GSB_ENABLE
        }
    }

@app.get("/api/v1/threats/recent")
async def get_recent_threats():
    """Get recent threat detections"""
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch([{'host': HOST_ADDR, 'port': ES_PORT}])
        
        result = es.search(
            index="ip_dns",
            body={
                "size": 50,
                "sort": [{"@timestamp": {"order": "desc"}}],
                "query": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "tags"}},
                            {"range": {"@timestamp": {"gte": "now-7d"}}}
                        ]
                    }
                }
            }
        )
        
        threats = []
        for hit in result['hits']['hits']:
            source = hit['_source']
            threats.append({
                "timestamp": source.get('@timestamp'),
                "device_ip": source.get('ip'),
                "dns_query": source.get('dns'),
                "tags": source.get('tags', []),
                "severity": "high" if "GSB" in source.get('tags', []) else "medium"
            })
        
        return {"threats": threats, "total": len(threats)}
    except Exception as e:
        print(f"Error getting threats: {e}")
        return {"threats": [], "total": 0}

@app.websocket("/api/v1/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to Srujan API",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            # Send periodic updates every 5 seconds
            await asyncio.sleep(5)
            
            # Send network stats update
            stats = await get_network_stats()
            await websocket.send_json({
                "type": "stats_update",
                "data": stats
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
