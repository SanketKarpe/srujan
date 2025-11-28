"""
Policy Models
Data models for network policies and conditions
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import time as dt_time
from dataclasses import dataclass, asdict
import json


class PolicyAction(Enum):
    """Actions that can be taken when a policy matches"""
    ALLOW = "allow"
    BLOCK = "block"
    RATE_LIMIT = "rate_limit"
    LOG_ONLY = "log_only"
    QUARANTINE = "quarantine"
    ALLOW_PRIORITY = "allow_priority"


class ConditionType(Enum):
    """Types of conditions that can be evaluated"""
    TIME_RANGE = "time_range"
    DAY_OF_WEEK = "day_of_week"
    TRUST_SCORE = "trust_score"
    DEVICE_CATEGORY = "device_category"
    ML_RISK_LEVEL = "ml_risk_level"
    NETWORK_ZONE = "network_zone"
    DESTINATION_IP = "destination_ip"
    DESTINATION_PORT = "destination_port"
    SOURCE_MAC = "source_mac"


@dataclass
class PolicyCondition:
    """A single condition for policy evaluation"""
    type: str  # ConditionType value
    operator: str  # >=, <=, ==, in, not_in, between
    value: Any  # Value to compare against
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate if condition is met given context
        
        Args:
            context: Dictionary of current context values
            
        Returns:
            True if condition is met, False otherwise
        """
        actual_value = context.get(self.type)
        
        if actual_value is None:
            return False
        
        if self.operator == ">=":
            return actual_value >= self.value
        elif self.operator == "<=":
            return actual_value <= self.value
        elif self.operator == "==":
            return actual_value == self.value
        elif self.operator == "!=":
            return actual_value != self.value
        elif self.operator == "in":
            return actual_value in self.value
        elif self.operator == "not_in":
            return actual_value not in self.value
        elif self.operator == "between":
            return self.value[0] <= actual_value <= self.value[1]
        
        return False
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'type': self.type,
            'operator': self.operator,
            'value': self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PolicyCondition':
        """Create from dictionary"""
        return cls(
            type=data['type'],
            operator=data['operator'],
            value=data['value']
        )


@dataclass
class NetworkPolicy:
    """A complete network policy with conditions and action"""
    id: Optional[int]
    name: str
    description: str
    source: str  # MAC, IP, zone, category, or "any"
    destination: str  # IP, CIDR, zone, or "any"
    conditions: List[PolicyCondition]
    action: str  # PolicyAction value
    priority: int = 50  # Higher = evaluated first
    enabled: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def should_apply(self, context: Dict[str, Any]) -> bool:
        """
        Check if all conditions are met for this policy
        
        Args:
            context: Current context with all relevant values
            
        Returns:
            True if policy should be applied, False otherwise
        """
        if not self.enabled:
            return False
        
        # Check source match
        if self.source != "any":
            if not self._matches_source(context):
                return False
        
        # Check destination match
        if self.destination != "any":
            if not self._matches_destination(context):
                return False
        
        # Evaluate all conditions (AND logic)
        return all(condition.evaluate(context) for condition in self.conditions)
    
    def _matches_source(self, context: Dict[str, Any]) -> bool:
        """Check if source matches"""
        source_value = context.get('source_mac') or context.get('source_ip')
        
        if self.source.startswith('category:'):
            category = self.source.split(':')[1]
            return context.get('device_category') == category
        elif self.source.startswith('zone:'):
            zone = self.source.split(':')[1]
            return context.get('network_zone') == zone
        else:
            return source_value == self.source
    
    def _matches_destination(self, context: Dict[str, Any]) -> bool:
        """Check if destination matches"""
        dest_ip = context.get('destination_ip', '')
        
        # Simple IP or CIDR check (simplified)
        if '/' in self.destination:
            # CIDR check would go here
            return True  # Placeholder
        else:
            return dest_ip == self.destination
    
    def to_iptables_rule(self) -> str:
        """
        Convert policy to iptables command
        
        Returns:
            iptables command string
        """
        if self.action == PolicyAction.BLOCK.value:
            if self.source != "any" and not self.source.startswith(('category:', 'zone:')):
                return f"iptables -A FORWARD -m mac --mac-source {self.source} -j DROP"
            else:
                return f"iptables -A FORWARD -j DROP  # Policy: {self.name}"
        
        elif self.action == PolicyAction.ALLOW.value:
            if self.source != "any" and not self.source.startswith(('category:', 'zone:')):
                return f"iptables -A FORWARD -m mac --mac-source {self.source} -j ACCEPT"
            else:
                return f"iptables -A FORWARD -j ACCEPT  # Policy: {self.name}"
        
        elif self.action == PolicyAction.QUARANTINE.value:
            # Quarantine = block all except DNS
            return f"iptables -A FORWARD -p udp --dport 53 -j ACCEPT && iptables -A FORWARD -j DROP  # Quarantine: {self.name}"
        
        elif self.action == PolicyAction.LOG_ONLY.value:
            return f"iptables -A FORWARD -j LOG --log-prefix='Policy:{self.name}'"
        
        return f"# Policy: {self.name} (action: {self.action})"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'source': self.source,
            'destination': self.destination,
            'conditions': [c.to_dict() for c in self.conditions],
            'action': self.action,
            'priority': self.priority,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'NetworkPolicy':
        """Create from dictionary"""
        conditions = [PolicyCondition.from_dict(c) for c in data.get('conditions', [])]
        
        return cls(
            id=data.get('id'),
            name=data['name'],
            description=data.get('description', ''),
            source=data['source'],
            destination=data['destination'],
            conditions=conditions,
            action=data['action'],
            priority=data.get('priority', 50),
            enabled=data.get('enabled', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )


# Pre-built policy templates
POLICY_TEMPLATES = [
    {
        "name": "Bedtime Internet Block",
        "description": "Block all IoT devices from internet access after 10 PM",
        "source": "category:iot",
        "destination": "!192.168.0.0/16",
        "conditions": [
            {"type": "time_range", "operator": "in", "value": ["22:00", "06:00"]}
        ],
        "action": "block",
        "priority": 60
    },
    {
        "name": "Low Trust Quarantine",
        "description": "Quarantine devices with trust score below 30",
        "source": "any",
        "destination": "any",
        "conditions": [
            {"type": "trust_score", "operator": "<=", "value": 30}
        ],
        "action": "quarantine",
        "priority": 90
    },
    {
        "name": "Work From Home Priority",
        "description": "Prioritize work devices during business hours",
        "source": "category:work",
        "destination": "any",
        "conditions": [
            {"type": "time_range", "operator": "in", "value": ["09:00", "17:00"]},
            {"type": "day_of_week", "operator": "in", "value": ["Mon", "Tue", "Wed", "Thu", "Fri"]}
        ],
        "action": "allow_priority",
        "priority": 70
    },
    {
        "name": "ML Anomaly Block",
        "description": "Block devices with critical ML risk level",
        "source": "any",
        "destination": "any",
        "conditions": [
            {"type": "ml_risk_level", "operator": "==", "value": "critical"}
        ],
        "action": "block",
        "priority": 95
    },
    {
        "name": "Guest Network Isolation",
        "description": "Restrict guest devices to internet only (no local network)",
        "source": "zone:guest",
        "destination": "192.168.0.0/16",
        "conditions": [],
        "action": "block",
        "priority": 80
    }
]


if __name__ == "__main__":
    # Test policy evaluation
    policy = NetworkPolicy(
        id=1,
        name="Test Policy",
        description="Test trust-based blocking",
        source="any",
        destination="any",
        conditions=[
            PolicyCondition(type="trust_score", operator="<=", value=30)
        ],
        action="block",
        priority=50
    )
    
    # Test context
    context = {
        "trust_score": 25,
        "source_mac": "aa:bb:cc:dd:ee:ff"
    }
    
    print(f"Should apply: {policy.should_apply(context)}")
    print(f"iptables rule: {policy.to_iptables_rule()}")
    print(f"Policy dict: {json.dumps(policy.to_dict(), indent=2)}")
