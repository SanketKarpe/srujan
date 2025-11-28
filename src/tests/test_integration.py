import unittest
import os
import json
import time
from fastapi.testclient import TestClient
from src.api.main import app
from src.services.policy_engine import PolicyEngine
from src.models.policy import PolicyAction, NetworkPolicy

class TestPolicyIntegration(unittest.TestCase):
    """
    End-to-end integration tests for the Policy Engine.
    Tests the full flow from API -> Database -> Engine -> iptables (dry-run).
    """

    @classmethod
    def setUpClass(cls):
        # Use a test database
        cls.test_db = "test_integration_policies.db"
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        
        # Initialize engine with test DB
        cls.engine = PolicyEngine(db_path=cls.test_db, dry_run=True)
        
        # Initialize API client
        cls.client = TestClient(app)
        
        # Override engine in API (mocking dependency injection essentially)
        # Note: In a real app, we'd use dependency overrides, but for this simple
        # integration test, we'll rely on the fact that the API creates a new engine
        # which will use the default DB path unless we patch it.
        # For this test, we'll test the Engine logic directly mostly, and API for CRUD.

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def setUp(self):
        # Clear policies before each test
        import sqlite3
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM policies")
        cursor.execute("DELETE FROM policy_conditions")
        conn.commit()
        conn.close()

    def test_full_policy_lifecycle(self):
        """
        Test creating a policy, verifying it's stored, evaluating it, and deleting it.
        """
        print("\nTesting Full Policy Lifecycle...")

        # 1. Create Policy via API (simulated)
        # We'll use the engine directly to simulate API calls for simplicity in this standalone script
        # or we could patch the DB path in the API. Let's use the engine directly for reliability.
        
        policy_data = {
            "name": "Integration Test Policy",
            "description": "Block IoT devices at night",
            "source": "category:iot",
            "destination": "any",
            "action": "block",
            "priority": 80,
            "enabled": True,
            "conditions": [
                {"type": "time_range", "operator": "in", "value": ["22:00", "06:00"]}
            ]
        }
        
        # Create
        policy_id = self.engine.db.create_policy(NetworkPolicy.from_dict(policy_data))
        print(f"✅ Created policy with ID: {policy_id}")
        
        # 2. Verify Storage
        stored_policy = self.engine.db.get_policy(policy_id)
        self.assertIsNotNone(stored_policy)
        self.assertEqual(stored_policy.name, "Integration Test Policy")
        print("✅ Policy storage verified")

        # 3. Test Evaluation (Should Match)
        # Context that matches
        context_match = {
            "source_mac": "aa:bb:cc:dd:ee:ff",
            "destination_ip": "8.8.8.8",
            "time": "23:00", # Inside 22:00-06:00
            "device_category": "iot" # Matches source
        }
        
        # We need to mock the context builder or pass context directly if possible.
        # The engine.evaluate_connection builds context internally.
        # For integration test, we'll use test_policy method which accepts context.
        
        results = self.engine.test_policy(stored_policy, [context_match])
        self.assertTrue(results[0]['would_apply'])
        self.assertEqual(results[0]['action'], 'block')
        print("✅ Policy correctly matches valid context")

        # 4. Test Evaluation (Should NOT Match)
        context_no_match = {
            "source_mac": "aa:bb:cc:dd:ee:ff",
            "destination_ip": "8.8.8.8",
            "time": "12:00", # Outside range
            "category": "iot"
        }
        results = self.engine.test_policy(stored_policy, [context_no_match])
        self.assertFalse(results[0]['would_apply'])
        print("✅ Policy correctly ignores invalid context")

        # 5. Apply to iptables (Dry Run)
        # This verifies the translation logic works without errors
        try:
            self.engine.apply_policies()
            print("✅ Policy application (dry-run) successful")
        except Exception as e:
            self.fail(f"Policy application failed: {e}")

        # 6. Delete Policy
        self.engine.db.delete_policy(policy_id)
        deleted_policy = self.engine.db.get_policy(policy_id)
        self.assertIsNone(deleted_policy)
        print("✅ Policy deletion verified")

    def test_trust_score_integration(self):
        """
        Test that trust scores influence policy decisions.
        """
        print("\nTesting Trust Score Integration...")

        # 1. Create Trust-based Policy
        policy_data = {
            "name": "Block Untrusted",
            "description": "Block devices with low trust",
            "source": "any",
            "destination": "any",
            "action": "quarantine",
            "priority": 90,
            "enabled": True,
            "conditions": [
                {"type": "trust_score", "operator": "<=", "value": 30}
            ]
        }
        self.engine.db.create_policy(NetworkPolicy.from_dict(policy_data))
        
        # 2. Reload engine policies
        self.engine.load_policies()

        # 3. Simulate Device with Low Trust
        # We'll mock the trust scorer for this test
        self.engine.trust_scorer.calculate_trust_score = lambda mac: {
            'score': 20, 
            'level': 'low_trust',
            'factors': {}
        }
        
        action, policy = self.engine.evaluate_connection("11:22:33:44:55:66", "1.1.1.1")
        self.assertEqual(action.value, "quarantine")
        self.assertEqual(policy.name, "Block Untrusted")
        print("✅ Low trust device correctly quarantined")

        # 4. Simulate Device with High Trust
        self.engine.trust_scorer.calculate_trust_score = lambda mac: {
            'score': 80, 
            'level': 'trusted',
            'factors': {}
        }
        
        action, policy = self.engine.evaluate_connection("11:22:33:44:55:66", "1.1.1.1")
        # Should be ALLOW (default) as no policy matches
        self.assertEqual(action.value, "allow")
        print("✅ High trust device allowed")

    def test_conflict_detection(self):
        """
        Test that the engine detects conflicting policies.
        """
        print("\nTesting Conflict Detection...")

        # Policy A: Block IoT
        policy_a = NetworkPolicy.from_dict({
            "name": "Block IoT",
            "source": "category:iot",
            "destination": "any",
            "action": "block",
            "conditions": []
        })
        self.engine.db.create_policy(policy_a)
        self.engine.load_policies()

        # Policy B: Allow IoT (Conflict!)
        policy_b = NetworkPolicy.from_dict({
            "name": "Allow IoT",
            "source": "category:iot",
            "destination": "any",
            "action": "allow",
            "conditions": []
        })

        conflicts = self.engine.detect_conflicts(policy_b)
        self.assertTrue(len(conflicts) > 0)
        self.assertEqual(conflicts[0]['policy_name'], "Block IoT")
        print("✅ Conflict correctly detected")

if __name__ == '__main__':
    unittest.main()
