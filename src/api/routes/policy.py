"""
Policy Management API Routes
Provides CRUD operations and testing for network policies.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

from services.policy_engine import PolicyEngine
from services.policy_database import PolicyDatabase
from models.policy import NetworkPolicy, PolicyCondition, POLICY_TEMPLATES


router = APIRouter(prefix="/api/v1/policies", tags=["policies"])

# Initialize services
engine = PolicyEngine()


# Pydantic models for API
class PolicyConditionCreate(BaseModel):
    """Schema for creating a policy condition."""
    type: str
    operator: str
    value: any


class PolicyCreate(BaseModel):
    """Schema for creating a new policy."""
    name: str
    description: str
    source: str
    destination: str
    conditions: List[PolicyConditionCreate]
    action: str
    priority: int = 50
    enabled: bool = True


class PolicyUpdate(BaseModel):
    """Schema for updating an existing policy."""
    name: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None
    action: Optional[str] = None
    priority: Optional[int] = None
    enabled: Optional[bool] = None


@router.get("")
async def list_policies(enabled_only: bool = False):
    """
    List all network policies.
    
    Args:
        enabled_only: If True, only return enabled policies
    
    Returns:
        Dictionary with policies list and total count
    
    Example:
        GET /api/v1/policies?enabled_only=true
    """
    try:
        if enabled_only:
            policies = engine.db.get_enabled_policies()
        else:
            policies = engine.db.get_all_policies()
        
        return {
            "policies": [p.to_dict() for p in policies],
            "total": len(policies)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("")
async def create_policy(policy: PolicyCreate):
    """
    Create a new network policy.
    
    Validates the policy and checks for conflicts before creation.
    
    Args:
        policy: Policy creation data
    
    Returns:
        Created policy with ID and conflict warnings
    
    Example:
        POST /api/v1/policies
        {
            "name": "Block IoT at Night",
            "description": "Block IoT devices after 10 PM",
            "source": "category:iot",
            "destination": "!192.168.0.0/16",
            "conditions": [
                {"type": "time_range", "operator": "in", "value": ["22:00", "06:00"]}
            ],
            "action": "block",
            "priority": 60
        }
    """
    try:
        # Convert to NetworkPolicy
        conditions = [
            PolicyCondition(
                type=c.type,
                operator=c.operator,
                value=c.value
            )
            for c in policy.conditions
        ]
        
        new_policy = NetworkPolicy(
            id=None,
            name=policy.name,
            description=policy.description,
            source=policy.source,
            destination=policy.destination,
            conditions=conditions,
            action=policy.action,
            priority=policy.priority,
            enabled=policy.enabled
        )
        
        # Check for conflicts
        conflicts = engine.detect_conflicts(new_policy)
        
        # Create policy
        policy_id = engine.db.create_policy(new_policy)
        
        # Reload policies
        engine.load_policies()
        
        return {
            "status": "success",
            "policy_id": policy_id,
            "conflicts": conflicts,
            "warning": "Policy has conflicts" if conflicts else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{policy_id}")
async def get_policy(policy_id: int):
    """
    Get a specific policy by ID.
    
    Args:
        policy_id: Policy ID
    
    Returns:
        Policy details
    
    Example:
        GET /api/v1/policies/1
    """
    policy = engine.db.get_policy(policy_id)
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return policy.to_dict()


@router.put("/{policy_id}")
async def update_policy(policy_id: int, updates: PolicyUpdate):
    """
    Update an existing policy.
    
    Args:
        policy_id: Policy ID to update
        updates: Fields to update
    
    Returns:
        Success status
    
    Example:
        PUT /api/v1/policies/1
        {"enabled": false}
    """
    try:
        # Convert to dict, removing None values
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        success = engine.db.update_policy(policy_id, update_dict)
        
        if not success:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Reload policies
        engine.load_policies()
        
        return {"status": "success", "updated": True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{policy_id}")
async def delete_policy(policy_id: int):
    """
    Delete a policy.
    
    Args:
        policy_id: Policy ID to delete
    
    Returns:
        Success status
    
    Example:
        DELETE /api/v1/policies/1
    """
    try:
        success = engine.db.delete_policy(policy_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Reload policies
        engine.load_policies()
        
        return {"status": "success", "deleted": True}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest/{mac}")
async def suggest_policies(mac: str):
    """
    Get ML-powered policy suggestions for a device.
    
    Analyzes device behavior and suggests appropriate policies.
    
    Args:
        mac: Device MAC address
    
    Returns:
        List of suggested policies with confidence scores
    
    Example:
        POST /api/v1/policies/suggest/aa:bb:cc:dd:ee:ff
    """
    try:
        suggestions = engine.suggest_policies_for_device(mac)
        
        return {
            "device_mac": mac,
            "suggestions": suggestions,
            "total": len(suggestions)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{policy_id}/test")
async def test_policy(policy_id: int, test_cases: List[Dict]):
    """
    Test a policy against sample scenarios.
    
    Args:
        policy_id: Policy to test
        test_cases: List of test scenarios (contexts)
    
    Returns:
        Test results showing which scenarios would match
    
    Example:
        POST /api/v1/policies/1/test
        [
            {"trust_score": 25, "time": "14:00"},
            {"trust_score": 85, "time": "22:00"}
        ]
    """
    try:
        policy = engine.db.get_policy(policy_id)
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        results = engine.test_policy(policy, test_cases)
        
        return {
            "policy_id": policy_id,
            "policy_name": policy.name,
            "test_results": results,
            "matched_count": sum(1 for r in results if r['would_apply'])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply")
async def apply_all_policies():
    """
    Apply all enabled policies to iptables.
    
    This will:
    1. Clear existing policy rules
    2. Apply all enabled policies in priority order
    3. Return application results
    
    Returns:
        Application statistics (applied, failed, skipped)
    
    Example:
        POST /api/v1/policies/apply
    """
    try:
        results = engine.apply_policies()
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{policy_id}/logs")
async def get_policy_logs(policy_id: int, limit: int = 100):
    """
    Get execution logs for a policy.
    
    Args:
        policy_id: Policy ID
        limit: Maximum number of logs to return
    
    Returns:
        List of policy execution logs
    
    Example:
        GET /api/v1/policies/1/logs?limit=50
    """
    try:
        logs = engine.db.get_policy_logs(policy_id, limit)
        
        return {
            "policy_id": policy_id,
            "logs": logs,
            "total": len(logs)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/list")
async def list_templates():
    """
    Get list of pre-built policy templates.
    
    Returns:
        List of available policy templates
    
    Example:
        GET /api/v1/policies/templates/list
    """
    return {
        "templates": POLICY_TEMPLATES,
        "total": len(POLICY_TEMPLATES)
    }
