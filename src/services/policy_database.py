"""
Policy Database
SQLite database for storing network policies and trust scores
"""
import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json

from models.policy import NetworkPolicy, PolicyCondition


class PolicyDatabase:
    def __init__(self, db_path: str = 'data/policies.db'):
        """Initialize policy database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Policies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                source VARCHAR(255),
                destination VARCHAR(255),
                action VARCHAR(50),
                priority INTEGER DEFAULT 50,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Policy conditions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policy_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_id INTEGER,
                type VARCHAR(50),
                operator VARCHAR(10),
                value TEXT,
                FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE
            )
        ''')
        
        # Trust scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trust_scores (
                device_mac VARCHAR(17) PRIMARY KEY,
                score INTEGER,
                level VARCHAR(20),
                factors TEXT,
                last_calculated TIMESTAMP,
                manual_override BOOLEAN DEFAULT FALSE,
                manual_score INTEGER
            )
        ''')
        
        # Policy logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS policy_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                policy_id INTEGER,
                policy_name VARCHAR(255),
                source_mac VARCHAR(17),
                destination_ip VARCHAR(15),
                action VARCHAR(50),
                matched BOOLEAN
            )
        ''')
        
        # IDS Alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ids_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                event_type VARCHAR(20),
                src_ip VARCHAR(15),
                src_port INTEGER,
                dest_ip VARCHAR(15),
                dest_port INTEGER,
                proto VARCHAR(10),
                alert_signature_id INTEGER,
                alert_signature VARCHAR(255),
                alert_category VARCHAR(100),
                alert_severity INTEGER,
                action VARCHAR(20),
                raw_json TEXT
            )
        ''')
        
        # IDS Rules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ids_rules (
                sid INTEGER PRIMARY KEY,
                revision INTEGER,
                signature VARCHAR(255),
                category VARCHAR(100),
                severity INTEGER,
                enabled BOOLEAN DEFAULT TRUE,
                raw_rule TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # Policy CRUD operations
    
    def create_policy(self, policy: NetworkPolicy) -> int:
        """Create new policy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert policy
            cursor.execute('''
                INSERT INTO policies (name, description, source, destination, action, priority, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                policy.name,
                policy.description,
                policy.source,
                policy.destination,
                policy.action,
                policy.priority,
                policy.enabled
            ))
            
            policy_id = cursor.lastrowid
            
            # Insert conditions
            for condition in policy.conditions:
                cursor.execute('''
                    INSERT INTO policy_conditions (policy_id, type, operator, value)
                    VALUES (?, ?, ?, ?)
                ''', (
                    policy_id,
                    condition.type,
                    condition.operator,
                    json.dumps(condition.value)
                ))
            
            conn.commit()
            return policy_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_policy(self, policy_id: int) -> Optional[NetworkPolicy]:
        """Get policy by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Get policy
            cursor.execute('SELECT * FROM policies WHERE id = ?', (policy_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Get conditions
            cursor.execute('SELECT * FROM policy_conditions WHERE policy_id = ?', (policy_id,))
            condition_rows = cursor.fetchall()
            
            conditions = [
                PolicyCondition(
                    type=c['type'],
                    operator=c['operator'],
                    value=json.loads(c['value'])
                )
                for c in condition_rows
            ]
            
            return NetworkPolicy(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                source=row['source'],
                destination=row['destination'],
                conditions=conditions,
                action=row['action'],
                priority=row['priority'],
                enabled=bool(row['enabled']),
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
        finally:
            conn.close()
    
    def get_all_policies(self) -> List[NetworkPolicy]:
        """Get all policies"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM policies ORDER BY priority DESC, created_at ASC')
            policy_ids = [row['id'] for row in cursor.fetchall()]
            
            return [self.get_policy(pid) for pid in policy_ids if self.get_policy(pid)]
            
        finally:
            conn.close()
    
    def get_enabled_policies(self) -> List[NetworkPolicy]:
        """Get only enabled policies"""
        all_policies = self.get_all_policies()
        return [p for p in all_policies if p.enabled]
    
    def update_policy(self, policy_id: int, updates: Dict) -> bool:
        """Update policy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build update query
            fields = []
            values = []
            
            for key, value in updates.items():
                if key in ['name', 'description', 'source', 'destination', 'action', 'priority', 'enabled']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            
            if not fields:
                return False
            
            fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(policy_id)
            
            query = f"UPDATE policies SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_policy(self, policy_id: int) -> bool:
        """Delete policy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM policies WHERE id = ?', (policy_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    # Trust score operations
    
    def save_trust_score(self, mac: str, score_data: Dict):
        """Save or update trust score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO trust_scores
                (device_mac, score, level, factors, last_calculated)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                mac,
                score_data['score'],
                score_data['level'],
                json.dumps(score_data['factors']),
                score_data['calculated_at'].isoformat() if isinstance(score_data['calculated_at'], datetime) else score_data['calculated_at']
            ))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_trust_score(self, mac: str) -> Optional[Dict]:
        """Get trust score for device"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM trust_scores WHERE device_mac = ?', (mac,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return {
                'device_mac': row['device_mac'],
                'score': row['score'],
                'level': row['level'],
                'factors': json.loads(row['factors']),
                'last_calculated': row['last_calculated'],
                'manual_override': bool(row['manual_override']),
                'manual_score': row['manual_score']
            }
        finally:
            conn.close()
    
    def get_all_trust_scores(self) -> List[Dict]:
        """Get trust scores for all devices"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM trust_scores ORDER BY score DESC')
            rows = cursor.fetchall()
            
            return [
                {
                    'device_mac': row['device_mac'],
                    'score': row['score'],
                    'level': row['level'],
                    'factors': json.loads(row['factors']),
                    'last_calculated': row['last_calculated']
                }
                for row in rows
            ]
        finally:
            conn.close()
    
    # Policy logging
    
    def log_policy_execution(self, policy_id: int, policy_name: str, source_mac: str, 
                            destination_ip: str, action: str, matched: bool):
        """Log policy execution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO policy_logs (policy_id, policy_name, source_mac, destination_ip, action, matched)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (policy_id, policy_name, source_mac, destination_ip, action, matched))
            
            conn.commit()
        finally:
            conn.close()
    
    def get_policy_logs(self, policy_id: Optional[int] = None, limit: int = 100) -> List[Dict]:
        """Get policy execution logs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if policy_id:
                cursor.execute('''
                    SELECT * FROM policy_logs 
                    WHERE policy_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (policy_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM policy_logs 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        finally:
            conn.close()

    # IDS Operations
    
    def log_ids_alert(self, event: Dict):
        """Log IDS alert to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            alert = event.get('alert', {})
            
            cursor.execute('''
                INSERT INTO ids_alerts (
                    timestamp, event_type, src_ip, src_port, dest_ip, dest_port, proto,
                    alert_signature_id, alert_signature, alert_category, alert_severity,
                    action, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('timestamp'),
                event.get('event_type'),
                event.get('src_ip'),
                event.get('src_port'),
                event.get('dest_ip'),
                event.get('dest_port'),
                event.get('proto'),
                alert.get('signature_id'),
                alert.get('signature'),
                alert.get('category'),
                alert.get('severity'),
                alert.get('action', 'allowed'),
                json.dumps(event)
            ))
            
            conn.commit()
        finally:
            conn.close()
            
    def get_recent_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent IDS alerts"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM ids_alerts 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
            
    def upsert_ids_rule(self, rule: Dict):
        """Insert or update IDS rule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO ids_rules (
                    sid, revision, signature, category, severity, enabled, raw_rule, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                rule['sid'],
                rule.get('rev', 1),
                rule['signature'],
                rule.get('category', 'Unknown'),
                rule.get('severity', 3),
                rule.get('enabled', True),
                rule.get('raw_rule', ''),
                datetime.now().isoformat()
            ))
            conn.commit()
        finally:
            conn.close()
            
    def get_ids_rules(self) -> List[Dict]:
        """Get all IDS rules"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM ids_rules ORDER BY sid')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()


if __name__ == "__main__":
    # Test database operations
    db = PolicyDatabase('test_policies.db')
    
    # Create test policy
    from models.policy import NetworkPolicy, PolicyCondition
    
    policy = NetworkPolicy(
        id=None,
        name="Test Block Low Trust",
        description="Block devices with low trust",
        source="any",
        destination="any",
        conditions=[
            PolicyCondition(type="trust_score", operator="<=", value=30)
        ],
        action="block",
        priority=90
    )
    
    policy_id = db.create_policy(policy)
    print(f"Created policy ID: {policy_id}")
    
    # Retrieve it
    retrieved = db.get_policy(policy_id)
    print(f"Retrieved: {retrieved.to_dict()}")
    
    # List all
    all_policies = db.get_all_policies()
    print(f"Total policies: {len(all_policies)}")
