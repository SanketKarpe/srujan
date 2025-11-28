"""
Unit Tests for Policy Engine
Tests policy evaluation, conflict detection, and iptables integration.
"""
import unittest
from datetime import datetime
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.policy_engine import PolicyEngine
from models.policy import NetworkPolicy, PolicyCondition, PolicyAction
from services.policy_database import PolicyDatabase


class TestPolicyEngine(unittest.TestCase):
    """Test cases for PolicyEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = PolicyEngine(db_path='test_policies.db', dry_run=True)
        
        # Create test policy
        self.test_policy = NetworkPolicy(
            id=None,
            name="Test Low Trust Block",
            description="Block devices with low trust",
            source="any",
            destination="any",
            conditions=[
                PolicyCondition(type="trust_score", operator="<=", value=30)
            ],
            action="block",
            priority=90
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Delete test database
        import os
        if os.path.exists('test_policies.db'):
            os.remove('test_policies.db')
    
    def test_build_context(self):
        """Test context building for policy evaluation."""
        context = self.engine.build_context(
            "aa:bb:cc:dd:ee:ff",
            "8.8.8.8",
            device_category="iot"
        )
        
        # Check required fields
        self.assertIn('source_mac', context)
        self.assertIn('destination_ip', context)
        self.assertIn('trust_score', context)
        self.assertIn('time', context)
        self.assertIn('day_of_week', context)
        
        # Check values
        self.assertEqual(context['source_mac'], "aa:bb:cc:dd:ee:ff")
        self.assertEqual(context['destination_ip'], "8.8.8.8")
        self.assertEqual(context['device_category'], "iot")
        self.assertIsInstance(context['trust_score'], int)
        self.assertTrue(0 <= context['trust_score'] <= 100)
    
    def test_policy_evaluation_allow(self):
        """Test policy evaluation returns correct action."""
        # Add a policy that should NOT match
        high_trust_policy = NetworkPolicy(
            id=None,
            name="High Trust Only",
            description="Block low trust",
            source="any",
            destination="any",
            conditions=[
                PolicyCondition(type="trust_score", operator=">=", value=80)
            ],
            action="allow",
            priority=50
        )
        
        self.engine.db.create_policy(high_trust_policy)
        self.engine.load_policies()
        
        # Evaluate - should return default ALLOW (no match)
        action, policy = self.engine.evaluate_connection(
            "aa:bb:cc:dd:ee:ff",
            "8.8.8.8"
        )
        
        self.assertIn(action, [PolicyAction.ALLOW])
    
    def test_conflict_detection_same_source(self):
        """Test conflict detection for overlapping policies."""
        # Create conflicting policy
        conflicting_policy = NetworkPolicy(
            id=None,
            name="Test Conflicting Allow",
            description="Allow devices with low trust (conflicts with block)",
            source="any",
            destination="any",
            conditions=[
                PolicyCondition(type="trust_score", operator="<=", value=30)
            ],
            action="allow",  # Different action!
            priority=90
        )
        
        # Add first policy
        self.engine.db.create_policy(self.test_policy)
        self.engine.load_policies()
        
        # Check for conflicts with second policy
        conflicts = self.engine.detect_conflicts(conflicting_policy)
        
        self.assertGreater(len(conflicts), 0)
        self.assertEqual(conflicts[0]['policy_name'], "Test Low Trust Block")
        self.assertIn('different actions', conflicts[0]['reason'].lower())
    
    def test_apply_policies_dry_run(self):
        """Test applying policies in dry-run mode."""
        # Add test policy
        self.engine.db.create_policy(self.test_policy)
        self.engine.load_policies()
        
        # Apply policies
        results = self.engine.apply_policies()
        
        self.assertGreater(results['applied'], 0)
        self.assertEqual(results['failed'], 0)
    
    def test_policy_suggestions_low_trust(self):
        """Test ML-powered policy suggestions for low trust device."""
        # This test depends on trust scorer returning low score
        # In production, you'd mock the trust scorer
        
        suggestions = self.engine.suggest_policies_for_device("aa:bb:cc:dd:ee:ff")
        
        # Should return suggestions (could be empty if trust is high)
        self.assertIsInstance(suggestions, list)
        
        # If there are suggestions, check structure
        if suggestions:
            self.assertIn('name', suggestions[0])
            self.assertIn('confidence', suggestions[0])
            self.assertIn('action', suggestions[0])
    
    def test_policy_testing(self):
        """Test policy testing framework."""
        test_cases = [
            {'trust_score': 25, 'time': '14:00', 'source_mac': 'aa:bb:cc:dd:ee:ff'},
            {'trust_score': 85, 'time': '22:00', 'source_mac': 'aa:bb:cc:dd:ee:ff'},
            {'trust_score': 50, 'time': '10:00', 'source_mac': 'aa:bb:cc:dd:ee:ff'}
        ]
        
        results = self.engine.test_policy(self.test_policy, test_cases)
        
        self.assertEqual(len(results), 3)
        
        # First case should match (trust_score <= 30)
        self.assertTrue(results[0]['would_apply'])
        self.assertEqual(results[0]['action'], 'block')
        
        # Second case should NOT match (trust_score > 30)
        self.assertFalse(results[1]['would_apply'])
        
        # Third case should NOT match
        self.assertFalse(results[2]['would_apply'])


class TestPolicyModels(unittest.TestCase):
    """Test cases for Policy data models."""
    
    def test_policy_condition_evaluation(self):
        """Test policy condition evaluation logic."""
        # Test >= operator
        condition = PolicyCondition(type="trust_score", operator=">=", value=70)
        
        context_pass = {'trust_score': 75}
        context_fail = {'trust_score': 65}
        
        self.assertTrue(condition.evaluate(context_pass))
        self.assertFalse(condition.evaluate(context_fail))
    
    def test_policy_condition_in_operator(self):
        """Test 'in' operator for conditions."""
        condition = PolicyCondition(
            type="day_of_week",
            operator="in",
            value=["Monday", "Tuesday", "Wednesday"]
        )
        
        context_pass = {'day_of_week': 'Monday'}
        context_fail = {'day_of_week': 'Saturday'}
        
        self.assertTrue(condition.evaluate(context_pass))
        self.assertFalse(condition.evaluate(context_fail))
    
    def test_network_policy_should_apply(self):
        """Test network policy evaluation."""
        policy = NetworkPolicy(
            id=1,
            name="Test Policy",
            description="Test",
            source="any",
            destination="any",
            conditions=[
                PolicyCondition(type="trust_score", operator="<=", value=30),
                PolicyCondition(type="time", operator="==", value="14:00")
            ],
            action="block",
            priority=50
        )
        
        # Both conditions met
        context_match = {
            'trust_score': 25,
            'time': '14:00',
            'source_mac': 'aa:bb:cc:dd:ee:ff'
        }
        
        # Only one condition met
        context_no_match = {
            'trust_score': 25,
            'time': '22:00',
            'source_mac': 'aa:bb:cc:dd:ee:ff'
        }
        
        self.assertTrue(policy.should_apply(context_match))
        self.assertFalse(policy.should_apply(context_no_match))
    
    def test_policy_to_iptables(self):
        """Test iptables rule generation."""
        policy = NetworkPolicy(
            id=1,
            name="Block Test",
            description="Test",
            source="aa:bb:cc:dd:ee:ff",
            destination="any",
            conditions=[],
            action="block",
            priority=50
        )
        
        rule = policy.to_iptables_rule()
        
        self.assertIn('iptables', rule)
        self.assertIn('DROP', rule)
        self.assertIn('aa:bb:cc:dd:ee:ff', rule)


def run_tests():
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
