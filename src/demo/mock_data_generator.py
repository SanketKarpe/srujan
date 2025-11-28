"""
Demo Mode - Mock Data Generator for Testing
Generates realistic dummy data for testing dashboard without Raspberry Pi
"""
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Mock device manufacturers and types
MANUFACTURERS = [
    "Samsung", "Apple", "Google", "Amazon", "TP-Link", "Xiaomi",
    "Philips", "Sonos", "Ring", "Nest", "LG", "Sony"
]

DEVICE_TYPES = {
    "Samsung": ["Smart TV", "Smart Fridge", "Smart Phone"],
    "Apple": ["iPhone", "iPad", "MacBook", "Apple Watch"],
    "Google": ["Nest Hub", "Chromecast", "Pixel Phone"],
    "Amazon": ["Echo Dot", "Fire TV", "Ring Camera"],
    "TP-Link": ["Smart Plug", "Smart Bulb", "Router"],
    "Xiaomi": ["Mi Band", "Smart Camera", "Smart Bulb"],
    "Philips": ["Hue Bulb", "Hue Bridge"],
    "Sonos": ["Speaker"],
    "Ring": ["Doorbell", "Security Camera"],
    "Nest": ["Thermostat", "Smoke Detector"],
    "LG": ["Smart TV", "Washing Machine"],
    "Sony": ["PlayStation", "Smart TV"]
}

class MockDataGenerator:
    def __init__(self, num_devices=15):
        self.num_devices = num_devices
        self.devices = self._generate_devices()
        self.threats = self._generate_threats()
        self.ml_alerts = self._generate_ml_alerts()
        
    def _generate_mac(self):
        """Generate a random MAC address"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def _generate_ip(self, network="192.168.1"):
        """Generate a random IP address"""
        return f"{network}.{random.randint(10, 254)}"
    
    def _generate_devices(self):
        """Generate mock device list"""
        devices = []
        
        for i in range(self.num_devices):
            manufacturer = random.choice(MANUFACTURERS)
            device_type = random.choice(DEVICE_TYPES[manufacturer])
            
            # Determine category
            iot_brands = ["TP-Link", "Xiaomi", "Philips", "Sonos", "Ring", "Nest", "Amazon"]
            category = "iot" if manufacturer in iot_brands else "non_iot"
            
            mac = self._generate_mac()
            device = {
                "mac": mac,
                "ip": self._generate_ip(),
                "hostname": f"{device_type.lower().replace(' ', '-')}-{i+1}",
                "manufacturer": manufacturer,
                "device_type": device_type,
                "category": category,
                "status": random.choice(["active"] * 9 + ["blocked"]),
                "first_seen": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
                "last_seen": (datetime.now() - timedelta(minutes=random.randint(0, 60))).isoformat()
            }
            devices.append(device)
        
        return devices
    
    def _generate_threats(self):
        """Generate mock threat detections"""
        threats = []
        
        for _ in range(random.randint(10, 30)):
            device = random.choice(self.devices)
            
            # Generate malicious domains
            suspicious_domains = [
                "malware-download.xyz",
                "phishing-site.com",
                "botnet-command.net",
                "crypto-miner.org",
                "tracking-ads.info"
            ]
            
            threat = {
                "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
                "device_ip": device["ip"],
                "dns_query": random.choice(suspicious_domains),
                "tags": random.sample(["GSB", "Malware", "Phishing", "Blacklist"], random.randint(1, 2)),
                "severity": random.choice(["high", "high", "medium", "low"])  # Bias toward high
            }
            threats.append(threat)
        
        # Sort by timestamp (most recent first)
        threats.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return threats
    
    def _generate_ml_alerts(self):
        """Generate mock ML anomaly alerts"""
        alerts = []
        
        for _ in range(random.randint(5, 20)):
            device = random.choice(self.devices)
            
            risk_level = random.choice(["critical", "high", "medium", "low"])
            
            # Confidence correlates with risk
            confidence_map = {
                "critical": random.randint(85, 99),
                "high": random.randint(70, 89),
                "medium": random.randint(55, 75),
                "low": random.randint(40, 60)
            }
            
            # Anomaly score correlates with risk
            score_map = {
                "critical": random.uniform(-0.5, -0.4),
                "high": random.uniform(-0.4, -0.3),
                "medium": random.uniform(-0.3, -0.2),
                "low": random.uniform(-0.2, -0.1)
            }
            
            alert = {
                "mac": device["mac"],
                "detected_at": (datetime.now() - timedelta(hours=random.randint(0, 168))).isoformat(),
                "anomaly_score": score_map[risk_level],
                "confidence": confidence_map[risk_level],
                "risk_level": risk_level,
                "false_positive": random.choice([False] * 9 + [True])  # 10% false positives
            }
            alerts.append(alert)
        
        return alerts
    
    def get_network_stats(self):
        """Generate network statistics"""
        active_devices = [d for d in self.devices if d["status"] == "active"]
        blocked_devices = [d for d in self.devices if d["status"] == "blocked"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "devices": {
                "total": len(self.devices),
                "active": len(active_devices),
                "blocked": len(blocked_devices),
                "new_today": random.randint(0, 3)
            },
            "security": {
                "threats_today": len([t for t in self.threats if
                    datetime.fromisoformat(t["timestamp"]) > datetime.now() - timedelta(hours=24)
                ]),
                "threats_blocked": len(self.threats),
                "gsb_enabled": True
            }
        }
    
    def get_ml_insights(self, mac):
        """Generate ML insights for a specific device"""
        device = next((d for d in self.devices if d["mac"] == mac), None)
        if not device:
            return None
        
        # Generate current behavior features
        current_behavior = {
            "dns_query_count": random.randint(50, 500),
            "unique_domains": random.randint(10, 100),
            "dns_diversity": random.uniform(0.1, 0.9),
            "threat_count": random.randint(0, 5),
            "threat_ratio": random.uniform(0, 0.1),
            "domain_entropy": random.uniform(3.0, 5.0),
            "connection_count": random.randint(20, 300),
            "unique_ips": random.randint(5, 50),
            "ip_diversity": random.uniform(0.2, 0.8),
            "external_connections": random.randint(10, 200),
            "external_ratio": random.uniform(0.3, 0.9)
        }
        
        # Determine if anomaly
        is_anomaly = random.choice([True, False, False, False])  # 25% chance
        
        if is_anomaly:
            risk_level = random.choice(["critical", "high", "medium"])
            risk_score = random.randint(60, 95)
            anomaly_score = random.uniform(-0.5, -0.2)
            confidence = random.randint(70, 95)
        else:
            risk_level = "low"
            risk_score = random.randint(10, 40)
            anomaly_score = random.uniform(-0.1, 0.3)
            confidence = random.randint(60, 85)
        
        # Generate recommendations
        recommendations = []
        
        if is_anomaly:
            recommendations.append({
                "severity": "high",
                "title": "Unusual Behavior Detected",
                "description": f"Device is exhibiting abnormal patterns with {confidence}% confidence",
                "action": "Consider quarantining this device temporarily"
            })
        
        if current_behavior["threat_count"] > 0:
            recommendations.append({
                "severity": "critical",
                "title": "Malicious Connections Detected",
                "description": f"{current_behavior['threat_count']} connections to known malicious domains",
                "action": "Block this device immediately"
            })
        
        if not recommendations:
            recommendations.append({
                "severity": "info",
                "title": "Normal Behavior",
                "description": "Device is operating within normal parameters",
                "action": "No action required"
            })
        
        return {
            "mac": mac,
            "current_behavior": current_behavior,
            "baseline": None,  # TODO: Could generate baseline data
            "anomaly_detection": {
                "success": True,
                "is_anomaly": is_anomaly,
                "anomaly_score": anomaly_score,
                "confidence": confidence,
                "risk_level": risk_level
            },
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recent_anomalies_count": random.randint(0, 15),
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_mock_data(self, filename="mock_data.json"):
        """Save mock data to JSON file"""
        import json
        
        data = {
            "devices": self.devices,
            "threats": self.threats,
            "ml_alerts": self.ml_alerts,
            "network_stats": self.get_network_stats()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Mock data saved to {filename}")


if __name__ == "__main__":
    # Generate and save mock data
    print("Generating mock data...")
    generator = MockDataGenerator(num_devices=20)
    
    print(f"Generated {len(generator.devices)} devices")
    print(f"Generated {len(generator.threats)} threats")
    print(f"Generated {len(generator.ml_alerts)} ML alerts")
    
    generator.save_mock_data()
    print("Done!")
