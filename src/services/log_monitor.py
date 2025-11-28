"""
IDS Log Monitor
Monitors Suricata eve.json logs and ingests alerts into the database.
"""
import time
import json
import logging
import os
from pathlib import Path
from typing import Optional, Callable

from services.policy_database import PolicyDatabase
from services.trust_scorer import TrustScorer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogMonitor:
    """
    Monitors Suricata log file for alerts.
    """
    
    def __init__(self, log_path: str = 'eve.json', db_path: str = 'data/policies.db'):
        self.log_path = Path(log_path)
        self.db = PolicyDatabase(db_path)
        self.trust_scorer = TrustScorer()
        self.running = False
        
    def start(self, callback: Optional[Callable] = None):
        """
        Start monitoring the log file.
        
        Args:
            callback: Optional function to call for each new alert
        """
        self.running = True
        logger.info(f"Starting LogMonitor on {self.log_path}")
        
        # Ensure file exists
        if not self.log_path.exists():
            logger.warning(f"Log file {self.log_path} does not exist. Waiting for it...")
            while not self.log_path.exists() and self.running:
                time.sleep(1)
        
        # Open file and seek to end
        with open(self.log_path, 'r') as f:
            f.seek(0, os.SEEK_END)
            
            while self.running:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                try:
                    event = json.loads(line)
                    self.process_event(event)
                    
                    if callback:
                        callback(event)
                        
                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON log line")
                except Exception as e:
                    logger.error(f"Error processing log line: {e}")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info("Stopping LogMonitor")

    def process_event(self, event: dict):
        """Process a single Suricata event"""
        if event.get('event_type') != 'alert':
            return
            
        # Log to database
        self.db.log_ids_alert(event)
        
        # Handle high severity alerts
        alert = event.get('alert', {})
        severity = alert.get('severity', 3)
        src_ip = event.get('src_ip')
        
        # Severity 1 (High) or 2 (Medium)
        if severity <= 2 and src_ip:
            # TODO: Map IP to MAC for trust scoring
            # For now, we log the impact
            logger.warning(f"High severity alert from {src_ip}: {alert.get('signature')}")
            
            # In a real system, we would look up the MAC address from the IP
            # and lower the trust score.
            # self.trust_scorer.penalize_device(mac, severity)

if __name__ == "__main__":
    # Test monitor
    monitor = LogMonitor(log_path='eve.json')
    try:
        monitor.start()
    except KeyboardInterrupt:
        monitor.stop()
