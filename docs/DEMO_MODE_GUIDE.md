# Demo Mode Testing Guide

## Quick Start - Test Without Raspberry Pi

You can test the entire Srujan dashboard using demo/mock data without needing a Raspberry Pi, Elasticsearch, or any real network devices!

---

## Option 1: Using Demo API (Recommended)

### Step 1: Generate Mock Data

```bash
cd src/demo
pip install Faker
python3 mock_data_generator.py
```

This creates `mock_data.json` with:
- 20 realistic devices
- 10-30 threat detections
- 5-20 ML anomaly alerts
- Network statistics

### Step 2: Enable Demo Mode in API

**Edit `src/api/main.py`** and add demo router:

```python
# Import demo router
try:
    from routes import demo
    DEMO_ENABLED = True
except ImportError:
    DEMO_ENABLED = False

# Register demo router
if DEMO_ENABLED:
    app.include_router(demo.router)
```

### Step 3: Update Frontend to Use Demo Endpoints

**Edit `web/src/services/api.js`** - add demo mode switch:

```javascript
// At the top of the file
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true';
const API_BASE = DEMO_MODE ? '/api/v1/demo' : '/api/v1';

// Update axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}${API_BASE}`,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Step 4: Create `.env` file in `web/` directory

```bash
cd web
echo "VITE_DEMO_MODE=true" > .env
echo "VITE_API_URL=http://localhost:8000" >> .env
```

### Step 5: Start Everything

**Terminal 1 - API:**
```bash
cd src/api
python3 main.py
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
```

**Terminal 3 - Generate Data (optional):**
```bash
cd src/demo
python3 mock_data_generator.py
```

### Step 6: Access Dashboard

Open browser to: `http://localhost:3000`

**Skip setup wizard:**
```javascript
// In browser console:
localStorage.setItem('srujan_setup_complete', 'true')
// Then refresh page
```

---



## Option 3: Browser-Only Demo (No Backend)

For the ultimate simplicity, use mock data directly in the frontend:

### Create `web/src/services/mockData.js`:

```javascript
export const mockDevices = [
  {
    mac: "aa:bb:cc:dd:ee:01",
    ip: "192.168.1.100",
    hostname: "smart-tv-1",
    manufacturer: "Samsung",
    device_type: "Smart TV",
    category: "iot",
    status: "active",
    last_seen: new Date().toISOString()
  },
  // ... more devices
];

export const mockStats = {
  timestamp: new Date().toISOString(),
  devices: { total: 15, active: 14, blocked: 1, new_today: 2 },
  security: { threats_today: 3, threats_blocked: 3, gsb_enabled: true }
};

export const mockThreats = [
  {
    timestamp: new Date().toISOString(),
    device_ip: "192.168.1.100",
    dns_query: "malware-site.xyz",
    tags: ["GSB", "Malware"],
    severity: "high"
  }
];
```

### Update API client to use mock data when API fails:

```javascript
// In web/src/services/api.js
import { mockDevices, mockStats, mockThreats } from './mockData';

export const deviceAPI = {
  getAll: async () => {
    try {
      return await api.get('/devices');
    } catch (error) {
      console.log('Using mock data');
      return { data: { devices: mockDevices, total: mockDevices.length } };
    }
  },
  // ... rest of API
};
```

---

## Mock Data Customization

### Regenerate with Different Settings

```python
from mock_data_generator import MockDataGenerator

# More devices
generator = MockDataGenerator(num_devices=50)
generator.save_mock_data("mock_data.json")

# Generate specific device
device = {
    "mac": "aa:bb:cc:dd:ee:ff",
    "hostname": "my-test-device",
    "manufacturer": "Custom",
    # ... more fields
}
```

### Manual Editing

Edit `mock_data.json` directly:

```json
{
  "devices": [
    {
      "mac": "aa:bb:cc:dd:ee:01",
      "ip": "192.168.1.100",
      "hostname": "my-device",
      "manufacturer": "Samsung",
      "device_type": "Smart TV",
      "category": "iot",
      "status": "active"
    }
  ],
  "threats": [],
  "ml_alerts": []
}
```

---

## Testing Scenarios

### Test Anomaly Detection

Add high-risk ML alert in `mock_data.json`:

```json
{
  "ml_alerts": [
    {
      "mac": "aa:bb:cc:dd:ee:01",
      "detected_at": "2025-11-28T19:00:00Z",
      "anomaly_score": -0.45,
      "confidence": 92,
      "risk_level": "critical",
      "false_positive": false
    }
  ]
}
```

### Test Threat Detection

Add malicious connection:

```json
{
  "threats": [
    {
      "timestamp": "2025-11-28T19:00:00Z",
      "device_ip": "192.168.1.100",
      "dns_query": "malware-c2.evil.com",
      "tags": ["GSB", "Malware", "C&C"],
      "severity": "high"
    }
  ]
}
```

### Test Device Blocking

Set device status:

```json
{
  "status": "blocked"
}
```

---

## Tips

### 1. Auto-reload Mock Data

The demo API loads `mock_data.json` on startup. To reload:
1. Regenerate data: `python3 mock_data_generator.py`
2. Restart API

### 2. Mix Real and Mock Data

You can run Elasticsearch for some data and use demo for ML:
- Real devices from Elasticsearch
- Mock ML alerts from demo mode

### 3. Screenshot Testing

Demo mode is perfect for:
- Creating documentation screenshots
- Video tutorials
- UI/UX testing
- Demonstrations

---

## Troubleshooting

### Frontend Can't Connect to API

```bash
# Check API is running
curl http://localhost:8000/api/v1/demo/devices

# Check CORS settings in main.py
# Should include: http://localhost:3000, http://localhost:5173
```

### No Data Showing

1. Check browser console for errors
2. Verify `mock_data.json` exists
3. Check API logs
4. Try Option 3 (browser-only demo)

### Demo Mode Not Activating

Check `.env` file in `web/`:
```
VITE_DEMO_MODE=true
```

Restart dev server after changing `.env`!

---

## Production Note

**NEVER enable demo mode in production!**

Demo mode is for:
- ✅ Development
- ✅ Testing
- ✅ Demonstrations
- ✅ Screenshots
- ❌ Production deployments

---

**Quick Command Summary:**

```bash
# Generate mock data
cd src/demo && python3 mock_data_generator.py

# Start demo API
cd src/api && python3 main.py

# OR start standalone mock server
cd src/demo && python3 mock_server.py

# Start frontend in demo mode
cd web && echo "VITE_DEMO_MODE=true" > .env && npm run dev

# Skip setup wizard (in browser console)
localStorage.setItem('srujan_setup_complete', 'true')
```

**Access:** http://localhost:3000

Enjoy testing! 🎉
