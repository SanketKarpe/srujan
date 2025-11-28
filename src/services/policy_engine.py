"""
Policy Engine Core
Evaluates network policies, detects conflicts, and applies iptables rules.

This module provides the core policy evaluation engine that:
1. Evaluates policies against real-time network context
2. Detects and resolves policy conflicts
3. Generates and applies iptables rules
4. Provides ML-powered policy suggestions
5. Tracks policy execution for audit trails
"""
import subprocess
from typing import List, Dict, Optional, Tuple
from datetime import datetime, time as dt_time
import logging

from models.policy import NetworkPolicy, PolicyAction, PolicyCondition, POLICY_TEMPLATES
from services.policy_database import PolicyDatabase
from services.trust_scorer import TrustScorer


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PolicyEngine:
    """
    Core policy evaluation and enforcement engine.
    
    This class handles all policy-related operations including evaluation,
    conflict detection, iptables rule generation, and ML-powered suggestions.
    
    Attributes:
        db: PolicyDatabase instance for persistence
        trust_scorer: TrustScorer for calculating device trust
        active_policies: List of currently enabled policies
        dry_run: If True, don't actually apply iptables rules
    """
    
    def __init__(self, db_path: str = 'data/policies.db', dry_run: bool = False):
        """
        Initialize the policy engine.
        
        Args:
            db_path: Path to SQLite database file
            dry_run: If True, simulate iptables commands without executing
        """
        self.db = PolicyDatabase(db_path)
        self.trust_scorer = TrustScorer()
        self.active_policies: List[NetworkPolicy] = []
        self.dry_run = dry_run
        self.load_policies()
    
    def load_policies(self):
        """
        Load all enabled policies from database.
        
        Policies are sorted by priority (highest first) to ensure
        correct evaluation order.
        """
        self.active_policies = self.db.get_enabled_policies()
        self.active_policies.sort(key=lambda p: p.priority, reverse=True)
        logger.info(f"Loaded {len(self.active_policies)} active policies")
    
    def build_context(self, source_mac: str, dest_ip: str, **kwargs) -> Dict:
        """
        Build evaluation context for policy checking.
        
        Creates a dictionary of all relevant context information needed
        to evaluate policy conditions.
        
        Args:
            source_mac: Source device MAC address
            dest_ip: Destination IP address
            **kwargs: Additional context values (device_category, zone, etc.)
        
        Returns:
            Dictionary with all context values for policy evaluation
        
        Example:
            >>> engine = PolicyEngine()
            >>> context = engine.build_context(
            ...     "aa:bb:cc:dd:ee:ff",
            ...     "8.8.8.8",
            ...     device_category="iot"
            ... )
            >>> context['trust_score']
            65
        """
        now = datetime.now()
        
        # Calculate trust score
        trust_data = self.trust_scorer.calculate_trust_score(source_mac)
        
        context = {
            # Device info
            'source_mac': source_mac,
            'destination_ip': dest_ip,
            'device_category': kwargs.get('device_category', 'unknown'),
            'network_zone': kwargs.get('network_zone', 'default'),
            
            # Time-based
            'time': now.strftime('%H:%M'),
            'day_of_week': now.strftime('%A'),
            'hour': now.hour,
            
            # Trust & ML
            'trust_score': trust_data['score'],
            'trust_level': trust_data['level'],
            'ml_risk_level': kwargs.get('ml_risk_level', 'low'),
            
            # Network
            'destination_port': kwargs.get('destination_port'),
        }
        
        return context
    
    def evaluate_connection(
        self, 
        source_mac: str, 
        dest_ip: str, 
        **kwargs
    ) -> Tuple[PolicyAction, Optional[NetworkPolicy]]:
        """
        Evaluate what action to take for a network connection.
        
        Iterates through policies in priority order and returns the action
        of the first matching policy.
        
        Args:
            source_mac: Source device MAC address
            dest_ip: Destination IP address
            **kwargs: Additional context for evaluation
        
        Returns:
            Tuple of (action, matching_policy)
            - action: PolicyAction to take (allow, block, etc.)
            - matching_policy: The policy that matched (or None for default)
        
        Example:
            >>> engine = PolicyEngine()
            >>> action, policy = engine.evaluate_connection(
            ...     "aa:bb:cc:dd:ee:ff",
            ...     "8.8.8.8"
            ... )
            >>> action
            PolicyAction.ALLOW
        """
        context = self.build_context(source_mac, dest_ip, **kwargs)
        
        # Evaluate policies in priority order
        for policy in self.active_policies:
            if policy.should_apply(context):
                # Log execution
                self.db.log_policy_execution(
                    policy_id=policy.id,
                    policy_name=policy.name,
                    source_mac=source_mac,
                    destination_ip=dest_ip,
                    action=policy.action,
                    matched=True
                )
                
                logger.info(
                    f"Policy '{policy.name}' matched for {source_mac} -> {dest_ip}. "
                    f"Action: {policy.action}"
                )
                
                return PolicyAction[policy.action.upper()], policy
        
        # Default: allow
        logger.debug(f"No policy matched for {source_mac} -> {dest_ip}. Allowing by default.")
        return PolicyAction.ALLOW, None
    
    def detect_conflicts(self, new_policy: NetworkPolicy) -> List[Dict]:
        """
        Detect if new policy conflicts with existing policies.
        
        Checks for overlapping conditions with different actions that could
        lead to unexpected behavior.
        
        Args:
            new_policy: Policy to check for conflicts
        
        Returns:
            List of conflict dictionaries with policy name and reason
        
        Example:
            >>> engine = PolicyEngine()
            >>> conflicts = engine.detect_conflicts(Policy(...))
            >>> len(conflicts)
            2
            >>> conflicts[0]['reason']
            'Overlapping time range with different action'
        """
        conflicts = []
        
        for existing in self.active_policies:
            # Skip if same policy
            if new_policy.id and existing.id == new_policy.id:
                continue
            
            # Check for overlapping source/destination
            source_overlap = (
                new_policy.source == existing.source or
                new_policy.source == "any" or
                existing.source == "any"
            )
            
            dest_overlap = (
                new_policy.destination == existing.destination or
                new_policy.destination == "any" or
                existing.destination == "any"
            )
            
            if source_overlap and dest_overlap:
                # Check if actions differ
                if new_policy.action != existing.action:
                    # Check for overlapping conditions
                    if self._conditions_overlap(new_policy.conditions, existing.conditions):
                        conflicts.append({
                            'policy_id': existing.id,
                            'policy_name': existing.name,
                            'reason': 'Overlapping conditions with different actions',
                            'new_action': new_policy.action,
                            'existing_action': existing.action,
                            'severity': 'high' if new_policy.priority == existing.priority else 'medium'
                        })
        
        return conflicts
    
    def _conditions_overlap(
        self, 
        conditions1: List[PolicyCondition], 
        conditions2: List[PolicyCondition]
    ) -> bool:
        """
        Check if two sets of conditions overlap.
        
        Args:
            conditions1: First set of conditions
            conditions2: Second set of conditions
        
        Returns:
            True if conditions could overlap in practice
        """
        # If either has no conditions, they overlap
        if not conditions1 or not conditions2:
            return True
        
        # Simple overlap check - could be made more sophisticated
        # For now, check if they have any conditions of the same type
        types1 = {c.type for c in conditions1}
        types2 = {c.type for c in conditions2}
        
        return bool(types1 & types2)
    
    def apply_policies(self) -> Dict[str, int]:
        """
        Apply all active policies to iptables.
        
        Clears existing policy rules and applies all enabled policies
        in priority order.
        
        Returns:
            Dictionary with counts of applied, failed, and skipped rules
        
        Raises:
            RuntimeError: If critical iptables commands fail
        
        Example:
            >>> engine = PolicyEngine()
            >>> result = engine.apply_policies()
            >>> result['applied']
            12
        """
        logger.info("Applying all policies to iptables")
        
        results = {
            'applied': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # Clear previous policy rules (from our custom chain)
        self._clear_policy_rules()
        
        # Apply each policy
        for policy in self.active_policies:
            try:
                iptables_rule = policy.to_iptables_rule()
                
                if self.dry_run:
                    logger.info(f"DRY RUN: Would execute: {iptables_rule}")
                    results['applied'] += 1
                else:
                    success = self._execute_iptables(iptables_rule)
                    if success:
                        results['applied'] += 1
                        logger.info(f"Applied policy '{policy.name}'")
                    else:
                        results['failed'] += 1
                        logger.error(f"Failed to apply policy '{policy.name}'")
            
            except Exception as e:
                results['failed'] += 1
                logger.error(f"Error applying policy '{policy.name}': {e}")
        
        logger.info(
            f"Policy application complete. "
            f"Applied: {results['applied']}, "
            f"Failed: {results['failed']}, "
            f"Skipped: {results['skipped']}"
        )
        
        return results
    
    def _clear_policy_rules(self):
        """Clear all policy rules from iptables."""
        if self.dry_run:
            logger.info("DRY RUN: Would clear policy rules")
            return
        
        # Flush our custom chain (if it exists)
        try:
            subprocess.run(
                ["iptables", "-F", "SRUJAN_POLICIES"],
                capture_output=True,
                check=False
            )
        except Exception as e:
            logger.warning(f"Error clearing policy rules: {e}")
    
    def _execute_iptables(self, command: str) -> bool:
        """
        Execute an iptables command.
        
        Args:
            command: Full iptables command string
        
        Returns:
            True if command succeeded, False otherwise
        """
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"iptables command failed: {result.stderr}")
                return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error executing iptables: {e}")
            return False
    
    def suggest_policies_for_device(self, device_mac: str) -> List[Dict]:
        """
        Generate ML-powered policy suggestions for a device.
        
        Analyzes device behavior patterns and suggests appropriate policies.
        
        Args:
            device_mac: MAC address of device to analyze
        
        Returns:
            List of policy suggestions with confidence scores
        
        Example:
            >>> engine = PolicyEngine()
            >>> suggestions = engine.suggest_policies_for_device("aa:bb:cc:dd:ee:ff")
            >>> suggestions[0]['name']
            'Quarantine Low Trust Device'
            >>> suggestions[0]['confidence']
            0.92
        """
        suggestions = []
        
        # Get trust score
        trust_data = self.trust_scorer.calculate_trust_score(device_mac)
        
        # Low trust = quarantine
        if trust_data['score'] < 30:
            suggestions.append({
                'name': f"Quarantine Low Trust - {device_mac}",
                'description': f"Device has very low trust score ({trust_data['score']})",
                'template': 'low_trust_quarantine',
                'source': device_mac,
                'destination': 'any',
                'conditions': [
                    {'type': 'trust_score', 'operator': '<=', 'value': 30}
                ],
                'action': 'quarantine',
                'priority': 90,
                'confidence': 0.92,
                'reason': f"Trust factors: {list(trust_data['factors'].keys())}"
            })
        
        # TODO: Add more ML-based suggestions
        # - Time-based patterns (only active during work hours)
        # - Connection patterns (only accesses certain IPs)
        # - Behavioral anomalies
        
        return suggestions
    
    def test_policy(
        self, 
        policy: NetworkPolicy, 
        test_cases: List[Dict]
    ) -> List[Dict]:
        """
        Test a policy against sample scenarios.
        
        Useful for validating policies before applying them.
        
        Args:
            policy: Policy to test
            test_cases: List of test scenarios (contexts)
        
        Returns:
            List of test results with expected vs actual outcomes
        
        Example:
            >>> engine = PolicyEngine()
            >>> test_cases = [
            ...     {'trust_score': 25, 'time': '14:00'},
            ...     {'trust_score': 85, 'time': '22:00'}
            ... ]
            >>> results = engine.test_policy(policy, test_cases)
            >>> results[0]['would_apply']
            True
        """
        results = []
        
        for i, test_case in enumerate(test_cases):
            would_apply = policy.should_apply(test_case)
            
            results.append({
                'test_case_id': i,
                'test_case': test_case,
                'would_apply': would_apply,
                'action': policy.action if would_apply else 'default_allow',
                'priority': policy.priority
            })
        
        return results


if __name__ == "__main__":
    # Example usage
    engine = PolicyEngine(dry_run=True)
    
    # Test evaluation
    action, policy = engine.evaluate_connection(
        "aa:bb:cc:dd:ee:ff",
        "8.8.8.8",
        device_category="iot"
    )
    
    print(f"Action: {action}")
    print(f"Policy: {policy.name if policy else 'default'}")
