"""
Trust Score Management API Routes
Provides endpoints for device trust scoring and management.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional

from services.trust_scorer import TrustScorer
from services.policy_database import PolicyDatabase


router = APIRouter(prefix="/api/v1/trust", tags=["trust"])

# Initialize services
trust_scorer = TrustScorer()
db = PolicyDatabase()


class TrustOverride(BaseModel):
    """Schema for manual trust score override."""
    score: int
    reason: str


@router.get("/{mac}")
async def get_trust_score(mac: str, recalculate: bool = False):
    """
    Get trust score for a specific device.
    
    Args:
        mac: Device MAC address
        recalculate: If True, force recalculation instead of using cache
    
    Returns:
        Trust score data with factors breakdown
    
    Example:
        GET /api/v1/trust/aa:bb:cc:dd:ee:ff?recalculate=true
    """
    try:
        # Get from database first
        if not recalculate:
            cached_score = db.get_trust_score(mac)
            if cached_score:
                return cached_score
        
        # Calculate fresh score
        score_data = trust_scorer.calculate_trust_score(mac)
        
        # Save to database
        db.save_trust_score(mac, score_data)
        
        return score_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def get_all_trust_scores():
    """
    Get trust scores for all devices.
    
    Returns:
        List of trust scores sorted by score (highest first)
    
    Example:
        GET /api/v1/trust
    """
    try:
        scores = db.get_all_trust_scores()
        
        # Group by trust level
        by_level = {
            'highly_trusted': [],
            'trusted': [],
            'neutral': [],
            'low_trust': [],
            'untrusted': []
        }
        
        for score in scores:
            by_level[score['level']].append(score)
        
        return {
            "scores": scores,
            "total": len(scores),
            "by_level": {
                level: len(devices)
                for level, devices in by_level.items()
            },
            "average_score": sum(s['score'] for s in scores) / len(scores) if scores else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{mac}")
async def override_trust_score(mac: str, override: TrustOverride):
    """
    Manually override trust score for a device.
    
    Useful for correcting ML mistakes or enforcing manual policies.
    
    Args:
        mac: Device MAC address
        override: Trust score override data
    
    Returns:
        Updated trust score
    
    Example:
        PUT /api/v1/trust/aa:bb:cc:dd:ee:ff
        {
            "score": 90,
            "reason": "Company device, verified secure"
        }
    """
    try:
        if not (0 <= override.score <= 100):
            raise HTTPException(
                status_code=400,
                detail="Trust score must be between 0 and 100"
            )
        
        # Get current score for factors
        current = trust_scorer.calculate_trust_score(mac)
        
        # Create override data
        override_data = {
            'device_mac': mac,
            'score': override.score,
            'level': trust_scorer.get_trust_level(override.score),
            'factors': {
                'manual_override': {
                    'impact': 0,
                    'reason': override.reason
                },
                **current.get('factors', {})
            },
            'calculated_at': current['calculated_at'],
            'manual_override': True,
            'manual_score': override.score
        }
        
        # Save to database
        db.save_trust_score(mac, override_data)
        
        return override_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recalculate")
async def recalculate_all_scores(device_list: Optional[List[str]] = None):
    """
    Recalculate trust scores for all or specific devices.
    
    Args:
        device_list: Optional list of MAC addresses to recalculate
                    If None, recalculates all devices
    
    Returns:
        Recalculation results with summary statistics
    
    Example:
        POST /api/v1/trust/recalculate
        ["aa:bb:cc:dd:ee:ff", "11:22:33:44:55:66"]
    """
    try:
        if device_list is None:
            # Get all devices from database
            all_scores = db.get_all_trust_scores()
            device_list = [s['device_mac'] for s in all_scores]
        
        # Recalculate scores
        results = trust_scorer.recalculate_all_scores(device_list)
        
        # Save to database
        for mac, score_data in results.items():
            db.save_trust_score(mac, score_data)
        
        # Get summary
        summary = trust_scorer.get_trust_summary(device_list)
        
        return {
            "status": "success",
            "recalculated": len(results),
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary/statistics")
async def get_trust_statistics():
    """
    Get aggregate trust score statistics.
    
    Returns:
        Statistical summary of trust scores across all devices
    
    Example:
        GET /api/v1/trust/summary/statistics
    """
    try:
        all_scores = db.get_all_trust_scores()
        
        if not all_scores:
            return {
                "total_devices": 0,
                "average_score": 0,
                "by_level": {},
                "score_distribution": {}
            }
        
        # Calculate statistics
        scores = [s['score'] for s in all_scores]
        
        # Group by trust level
        by_level = {}
        for score_data in all_scores:
            level = score_data['level']
            by_level[level] = by_level.get(level, 0) + 1
        
        # Score distribution (buckets of 20)
        distribution = {
            "0-20": 0,
            "21-40": 0,
            "41-60": 0,
            "61-80": 0,
            "81-100": 0
        }
        
        for score in scores:
            if score <= 20:
                distribution["0-20"] += 1
            elif score <= 40:
                distribution["21-40"] += 1
            elif score <= 60:
                distribution["41-60"] += 1
            elif score <= 80:
                distribution["61-80"] += 1
            else:
                distribution["81-100"] += 1
        
        return {
            "total_devices": len(all_scores),
            "average_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "by_level": by_level,
            "score_distribution": distribution
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
