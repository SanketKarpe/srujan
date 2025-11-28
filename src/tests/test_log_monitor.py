import unittest
import threading
import time
import json
import os
from pathlib import Path
from services.log_monitor import LogMonitor
from services.policy_database import PolicyDatabase

class TestLogMonitor(unittest.TestCase):
    def setUp(self):
        self.test_log = 'test_eve.json'
        self.test_db = 'test_ids.db'
        
        # Clean up previous run
        if os.path.exists(self.test_log):
            os.remove(self.test_log)
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
        # Create empty log file
        Path(self.test_log).touch()
        
        self.monitor = LogMonitor(log_path=self.test_log, db_path=self.test_db)
        self.db = PolicyDatabase(self.test_db)
        
    def tearDown(self):
        self.monitor.stop()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2.0)
            
        if os.path.exists(self.test_log):
            try:
                os.remove(self.test_log)
            except PermissionError:
                print("Warning: Could not remove test log file (still in use)")
                
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                print("Warning: Could not remove test db file")

    def test_alert_ingestion(self):
        """Test that alerts are ingested into DB"""
        # Start monitor in thread
        self.monitor_thread = threading.Thread(target=self.monitor.start)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # Give it a moment to start
        time.sleep(1)
        
        # Write an alert to the log
        alert_event = {
            "timestamp": "2023-10-27T10:00:00.000000+0000",
            "flow_id": 123456789,
            "event_type": "alert",
            "src_ip": "192.168.1.100",
            "src_port": 12345,
            "dest_ip": "8.8.8.8",
            "dest_port": 53,
            "proto": "UDP",
            "alert": {
                "action": "allowed",
                "gid": 1,
                "signature_id": 1001,
                "rev": 1,
                "signature": "TEST ALERT",
                "category": "Test",
                "severity": 1
            }
        }
        
        with open(self.test_log, 'a') as f:
            f.write(json.dumps(alert_event) + "\n")
            f.flush()
            
        # Wait for processing
        time.sleep(1)
        
        # Check DB
        alerts = self.db.get_recent_alerts()
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]['alert_signature'], "TEST ALERT")
        self.assertEqual(alerts[0]['src_ip'], "192.168.1.100")
        print("✅ Alert successfully ingested")

    def test_ignore_non_alerts(self):
        """Test that non-alert events are ignored"""
        # Start monitor
        self.monitor_thread = threading.Thread(target=self.monitor.start)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        time.sleep(1)
        
        # Write a DNS event (not alert)
        dns_event = {
            "timestamp": "2023-10-27T10:00:00.000000+0000",
            "event_type": "dns",
            "src_ip": "192.168.1.100"
        }
        
        with open(self.test_log, 'a') as f:
            f.write(json.dumps(dns_event) + "\n")
            f.flush()
            
        time.sleep(1)
        
        # Check DB - should be empty
        alerts = self.db.get_recent_alerts()
        self.assertEqual(len(alerts), 0)
        print("✅ Non-alert event correctly ignored")

if __name__ == '__main__':
    unittest.main()
