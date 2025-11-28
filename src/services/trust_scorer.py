"""
Trust Scoring System
Calculates dynamic trust scores (0-100) for network devices based on multiple factors
"""
from datetime import datetime, timedelta
from typing import Dict, List
import json


class TrustScorer:
    def __init__(self, es_client=None):
        """Initialize trust scorer with optional Elasticsearch client"""
        self.es = es_client
        self.cache = {}  # Cache scores for performance
        self.cache_duration = timedelta(minutes=5)
        
    def calculate_trust_score(self, device_mac: str) -> Dict:
        """
        Calculate comprehensive trust score for a device
        
        Args:
            device_mac: MAC address of device
            
        Returns:
            dict with score, level, and factors breakdown
        """
        # Check cache
        if device_mac in self.cache:
            cached_data = self.cache[device_mac]
            if datetime.now() - cached_data['calculated_at'] < self.cache_duration:
                return cached_data
        
        score = 50  # Start neutral
        factors = {}
        
        # Positive factors
        if self.is_known_device(device_mac):
            score += 20
            factors['known_device'] = {'impact': +20, 'reason': 'Device seen before'}
        
        if self.has_clean_history(device_mac):
            score += 15
            factors['clean_history'] = {'impact': +15, 'reason': 'No threats detected'}
        
        if self.manufacturer_trusted(device_mac):
            score += 10
            factors['trusted_manufacturer'] = {'impact': +10, 'reason': 'Reputable manufacturer'}
        
        if self.minimal_permissions(device_mac):
            score += 5
            factors['minimal_permissions'] = {'impact': +5, 'reason': 'Limited network access'}
        
        # Negative factors
        threat_count = self.get_threat_count(device_mac)
        if threat_count > 0:
            impact = -5 * threat_count
            score += impact
            factors['threats'] = {'impact': impact, 'reason': f'{threat_count} threats detected'}
        
        anomaly_count = self.get_anomaly_count(device_mac)
        if anomaly_count > 0:
            impact = -10 * min(anomaly_count, 5)  # Cap at -50
            score += impact
            factors['anomalies'] = {'impact': impact, 'reason': f'{anomaly_count} ML anomalies'}
        
        if self.uses_weak_encryption(device_mac):
            score -= 15
            factors['weak_encryption'] = {'impact': -15, 'reason': 'Using outdated encryption'}
        
        if self.excessive_connections(device_mac):
            score -= 10
            factors['excessive_connections'] = {'impact': -10, 'reason': 'Unusually high connection count'}
        
        if self.recently_added(device_mac):
            score -= 10
            factors['new_device'] = {'impact': -10, 'reason': 'Recently added to network'}
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Determine trust level
        level = self.get_trust_level(score)
        
        result = {
            'device_mac': device_mac,
            'score': score,
            'level': level,
            'factors': factors,
            'calculated_at': datetime.now(),
            'recommendation': self.get_recommendation(score, level)
        }
        
        # Cache result
        self.cache[device_mac] = result
        
        return result
    
    def get_trust_level(self, score: int) -> str:
        """Convert score to trust level"""
        if score >= 90:
            return 'highly_trusted'
        elif score >= 70:
            return 'trusted'
        elif score >= 50:
            return 'neutral'
        elif score >= 30:
            return 'low_trust'
        else:
            return 'untrusted'
    
    def get_recommendation(self, score: int, level: str) -> str:
        """Get security recommendation based on trust score"""
        if score >= 90:
            return 'Full network access recommended'
        elif score >= 70:
            return 'Normal access with monitoring'
        elif score >= 50:
            return 'Limited access, monitor closely'
        elif score >= 30:
            return 'Restricted access recommended'
        else:
            return 'Quarantine or block recommended'
    
    # Factor checking methods
    
    def is_known_device(self, mac: str) -> bool:
        """Check if device has been seen before"""
        # For demo/testing, check if in a known devices list
        # In production, check database or Elasticsearch
        return True  # Placeholder
    
    def has_clean_history(self, mac: str) -> bool:
        """Check if device has no threat detections"""
        threat_count = self.get_threat_count(mac)
        return threat_count == 0
    
    def manufacturer_trusted(self, mac: str) -> bool:
        """Check if device manufacturer is trusted"""
        # List of trusted manufacturers (by OUI prefix)
        trusted_ouis = [
            'apple', 'samsung', 'google', 'microsoft', 'dell',
            'hp', 'lenovo', 'asus', 'cisco', 'netgear'
        ]
        
        # Get manufacturer from MAC OUI
        # This is a simplified check
        return True  # Placeholder
    
    def minimal_permissions(self, mac: str) -> bool:
        """Check if device has minimal network permissions"""
        # Check connection patterns
        # Devices connecting to few IPs are less risky
        return False  # Placeholder
    
    def get_threat_count(self, mac: str) -> int:
        """Get number of threats detected for device in last 7 days"""
        if not self.es:
            return 0
        
        try:
            from elasticsearch import Elasticsearch
            
            # Query Elasticsearch for threats
            result = self.es.search(
                index="ip_dns",
                body={
                    "size": 0,
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"mac.keyword": mac}},
                                {"exists": {"field": "tags"}},
                                {"range": {"@timestamp": {"gte": "now-7d"}}}
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
    
    def get_anomaly_count(self, mac: str) -> int:
        """Get number of ML anomalies for device in last 7 days"""
        # Would query anomaly database/tracker
        # For now, return 0
        return 0
    
    def uses_weak_encryption(self, mac: str) -> bool:
        """Check if device uses weak/outdated encryption"""
        # Would analyze TLS versions, cipher suites
        return False
    
    def excessive_connections(self, mac: str) -> bool:
        """Check if device has unusually high connection count"""
        # Compare to baseline
        return False
    
    def recently_added(self, mac: str) -> bool:
        """Check if device was added recently (< 24 hours)"""
        # Check first_seen timestamp
        return False
    
    def recalculate_all_scores(self, device_list: List[str]) -> Dict[str, Dict]:
        """Recalculate trust scores for all devices"""
        results = {}
        for mac in device_list:
            results[mac] = self.calculate_trust_score(mac)
        return results
    
    def get_trust_summary(self, device_list: List[str]) -> Dict:
        """Get summary of trust levels across all devices"""
        scores = self.recalculate_all_scores(device_list)
        
        summary = {
            'highly_trusted': 0,
            'trusted': 0,
            'neutral': 0,
            'low_trust': 0,
            'untrusted': 0,
            'total': len(device_list),
            'average_score': 0
        }
        
        total_score = 0
        for mac, data in scores.items():
            summary[data['level']] += 1
            total_score += data['score']
        
        if device_list:
            summary['average_score'] = total_score / len(device_list)
        
        return summary


if __name__ == "__main__":
    # Test trust scoring
    scorer = TrustScorer()
    
    test_mac = "aa:bb:cc:dd:ee:ff"
    result = scorer.calculate_trust_score(test_mac)
    
    print(json.dumps(result, indent=2, default=str))
