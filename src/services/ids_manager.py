"""
IDS Manager Service
Manages Suricata rules and process state.
"""
import logging
import re
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import platform

from services.policy_database import PolicyDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IDSManager:
    """
    Manages IDS rules and process.
    """
    
    def __init__(self, rules_path: str = 'config/suricata.rules', db_path: str = 'data/policies.db'):
        self.rules_path = Path(rules_path)
        self.db = PolicyDatabase(db_path)
        self.is_windows = platform.system() == "Windows"
        
        # Ensure config dir exists
        self.rules_path.parent.mkdir(parents=True, exist_ok=True)
        
    def parse_rules_file(self):
        """Parse rules file and update database"""
        if not self.rules_path.exists():
            logger.warning(f"Rules file {self.rules_path} not found")
            return
            
        logger.info(f"Parsing rules from {self.rules_path}")
        
        with open(self.rules_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                rule = self._parse_rule(line)
                if rule:
                    self.db.upsert_ids_rule(rule)
                    
    def _parse_rule(self, line: str) -> Optional[Dict]:
        """Parse a single Snort/Suricata rule"""
        # Basic regex to extract SID and msg
        # alert tcp $EXTERNAL_NET any -> $HOME_NET 22 (msg:"ET SCAN LibSSH Based Scanner"; sid:2027974; rev:1;)
        
        try:
            # Extract options
            options_match = re.search(r'\((.*)\)', line)
            if not options_match:
                return None
                
            options_str = options_match.group(1)
            options = {}
            
            for part in options_str.split(';'):
                part = part.strip()
                if not part:
                    continue
                
                if ':' in part:
                    key, val = part.split(':', 1)
                    options[key.strip()] = val.strip().strip('"')
                else:
                    options[part] = True
            
            if 'sid' not in options:
                return None
                
            return {
                'sid': int(options['sid']),
                'rev': int(options.get('rev', 1)),
                'signature': options.get('msg', 'Unknown Rule'),
                'category': options.get('classtype', 'misc-activity'),
                'severity': int(options.get('priority', 3)),
                'enabled': not line.startswith('#'),
                'raw_rule': line
            }
            
        except Exception as e:
            logger.error(f"Error parsing rule: {line[:50]}... - {e}")
            return None

    def toggle_rule(self, sid: int, enabled: bool) -> bool:
        """Enable or disable a rule"""
        # In a real system, we would rewrite the rules file
        # For now, we just update the DB
        logger.info(f"Toggling rule {sid} to {enabled}")
        
        # TODO: Implement file rewriting logic
        return True

    def start_ids(self) -> bool:
        """Start the IDS process"""
        if self.is_windows:
            logger.info("Mocking Suricata start on Windows")
            return True
            
        # Linux implementation
        try:
            subprocess.run(["systemctl", "start", "suricata"], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to start Suricata: {e}")
            return False

    def stop_ids(self) -> bool:
        """Stop the IDS process"""
        if self.is_windows:
            logger.info("Mocking Suricata stop on Windows")
            return True
            
        try:
            subprocess.run(["systemctl", "stop", "suricata"], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to stop Suricata: {e}")
            return False

    def get_status(self) -> Dict:
        """Get IDS status"""
        return {
            "running": True,  # Mocked
            "rules_loaded": len(self.db.get_ids_rules()),
            "last_update": "Just now"
        }

if __name__ == "__main__":
    # Test manager
    manager = IDSManager()
    
    # Create dummy rules file
    with open('config/suricata.rules', 'w') as f:
        f.write('alert tcp any any -> any 80 (msg:"TEST RULE HTTP"; sid:1000001; rev:1; classtype:web-application-attack; priority:2;)\n')
        f.write('alert udp any any -> any 53 (msg:"TEST RULE DNS"; sid:1000002; rev:1; classtype:trojan-activity; priority:1;)\n')
    
    manager.parse_rules_file()
    print(f"Status: {manager.get_status()}")
