from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

from services.ids_manager import IDSManager
from services.policy_database import PolicyDatabase

router = APIRouter()

# Dependencies
def get_db():
    return PolicyDatabase()

def get_ids_manager():
    return IDSManager()

# Models
class IDSRuleUpdate(BaseModel):
    enabled: bool

class IDSAlert(BaseModel):
    id: int
    timestamp: str
    event_type: str
    src_ip: Optional[str]
    dest_ip: Optional[str]
    alert_signature: Optional[str]
    alert_severity: Optional[int]
    action: Optional[str]
    raw_json: str

# Routes

@router.get("/alerts", response_model=Dict)
async def get_alerts(
    limit: int = 50, 
    severity: Optional[int] = None,
    db: PolicyDatabase = Depends(get_db)
):
    """Get recent IDS alerts"""
    alerts = db.get_recent_alerts(limit=limit)
    
    # Filter by severity if requested (in memory for now, DB filter better later)
    if severity:
        alerts = [a for a in alerts if a['alert_severity'] <= severity]
        
    return {"alerts": alerts, "count": len(alerts)}

@router.get("/rules", response_model=Dict)
async def get_rules(
    manager: IDSManager = Depends(get_ids_manager),
    db: PolicyDatabase = Depends(get_db)
):
    """Get all IDS rules"""
    # Ensure rules are loaded
    if not db.get_ids_rules():
        manager.parse_rules_file()
        
    rules = db.get_ids_rules()
    return {"rules": rules, "count": len(rules)}

@router.post("/rules/{sid}/toggle")
async def toggle_rule(
    sid: int, 
    update: IDSRuleUpdate,
    manager: IDSManager = Depends(get_ids_manager)
):
    """Enable or disable a rule"""
    success = manager.toggle_rule(sid, update.enabled)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle rule")
        
    return {"status": "success", "sid": sid, "enabled": update.enabled}

@router.get("/stats")
async def get_stats(db: PolicyDatabase = Depends(get_db)):
    """Get IDS statistics"""
    alerts = db.get_recent_alerts(limit=1000)
    
    stats = {
        "total_alerts_24h": len(alerts),
        "high_severity": len([a for a in alerts if a['alert_severity'] == 1]),
        "medium_severity": len([a for a in alerts if a['alert_severity'] == 2]),
        "blocked": len([a for a in alerts if a['action'] == 'blocked']),
        "top_attackers": {},
        "top_signatures": {}
    }
    
    # Calculate top attackers
    attackers = {}
    signatures = {}
    
    for alert in alerts:
        src = alert['src_ip']
        sig = alert['alert_signature']
        
        attackers[src] = attackers.get(src, 0) + 1
        signatures[sig] = signatures.get(sig, 0) + 1
        
    stats["top_attackers"] = dict(sorted(attackers.items(), key=lambda x: x[1], reverse=True)[:5])
    stats["top_signatures"] = dict(sorted(signatures.items(), key=lambda x: x[1], reverse=True)[:5])
    
    return stats

@router.post("/control/{action}")
async def control_ids(
    action: str,
    manager: IDSManager = Depends(get_ids_manager)
):
    """Start/Stop/Reload IDS"""
    if action == "start":
        success = manager.start_ids()
    elif action == "stop":
        success = manager.stop_ids()
    elif action == "reload":
        manager.parse_rules_file()
        success = True
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    return {"status": "success" if success else "failed", "action": action}
