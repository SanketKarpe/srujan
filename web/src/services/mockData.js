export const mockDevices = [
    {
        mac: "aa:bb:cc:dd:ee:01",
        ip: "192.168.1.100",
        hostname: "smart-tv-living-room",
        manufacturer: "Samsung",
        device_type: "Smart TV",
        category: "iot",
        status: "active",
        last_seen: new Date().toISOString()
    },
    {
        mac: "aa:bb:cc:dd:ee:02",
        ip: "192.168.1.101",
        hostname: "alexa-kitchen",
        manufacturer: "Amazon",
        device_type: "Smart Speaker",
        category: "iot",
        status: "active",
        last_seen: new Date().toISOString()
    },
    {
        mac: "aa:bb:cc:dd:ee:03",
        ip: "192.168.1.105",
        hostname: "macbook-pro",
        manufacturer: "Apple",
        device_type: "Laptop",
        category: "general",
        status: "active",
        last_seen: new Date().toISOString()
    },
    {
        mac: "aa:bb:cc:dd:ee:04",
        ip: "192.168.1.110",
        hostname: "unknown-device",
        manufacturer: "Unknown",
        device_type: "Unknown",
        category: "iot",
        status: "blocked",
        last_seen: new Date().toISOString()
    },
    {
        mac: "aa:bb:cc:dd:ee:05",
        ip: "192.168.1.115",
        hostname: "philips-hue-bridge",
        manufacturer: "Philips",
        device_type: "Hub",
        category: "iot",
        status: "active",
        last_seen: new Date().toISOString()
    }
];

export const mockStats = {
    timestamp: new Date().toISOString(),
    devices: {
        total: 15,
        active: 14,
        blocked: 1,
        new_today: 2
    },
    security: {
        threats_today: 3,
        threats_blocked: 3,
        gsb_enabled: true
    }
};

export const mockThreats = [
    {
        timestamp: new Date().toISOString(),
        device_ip: "192.168.1.100",
        dns_query: "malware-site.xyz",
        tags: ["GSB", "Malware"],
        severity: "high"
    },
    {
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        device_ip: "192.168.1.110",
        dns_query: "tracking-pixel.ad",
        tags: ["Privacy", "Tracker"],
        severity: "medium"
    },
    {
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        device_ip: "192.168.1.101",
        dns_query: "botnet-c2.org",
        tags: ["GSB", "Botnet"],
        severity: "critical"
    }
];

export const mockMLAlerts = [
    {
        mac: "aa:bb:cc:dd:ee:01",
        detected_at: new Date().toISOString(),
        anomaly_score: -0.45,
        confidence: 92,
        risk_level: "critical",
        false_positive: false
    },
    {
        mac: "aa:bb:cc:dd:ee:02",
        detected_at: new Date(Date.now() - 86400000).toISOString(),
        anomaly_score: -0.25,
        confidence: 75,
        risk_level: "medium",
        false_positive: false
    }
];
