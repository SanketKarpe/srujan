# IDS/IPS Integration Guide 🛡️

## Overview
The Srujan Intrusion Detection System (IDS) is built on the **Suricata** architecture. It provides real-time network threat detection, logging, and visualization.

> [!NOTE]
> In the current Windows development environment, the Suricata engine is **simulated**. The system generates realistic `eve.json` logs to demonstrate the full pipeline from detection to visualization.

## Architecture

### 1. Data Plane (Simulated)
- **Suricata Engine**: Analyzes network traffic against signatures.
- **Output**: Writes alerts to `eve.json`.
- **Simulation**: `src/demo/mock_data_generator.py` generates realistic attack traffic (SQL Injection, DDoS, Malware).

### 2. Control Plane
- **IDS Manager** (`src/services/ids_manager.py`):
    - Manages `.rules` files.
    - Controls the Suricata process (Start/Stop/Reload).
    - Toggles individual signatures.

### 3. Analysis Plane
- **Log Monitor** (`src/services/log_monitor.py`):
    - Tails `eve.json` in real-time.
    - Parses alerts and stores them in SQLite (`ids_alerts`).
    - Triggers Trust Score penalties for high-severity alerts.

### 4. Visualization
- **IDS Dashboard**: Real-time view of attack trends and recent alerts.
- **Rule Manager**: Interface to search and enable/disable detection rules.

## Configuration

### Rules
Rules are stored in `config/suricata.rules`. They follow the standard Snort/Suricata syntax:
```
alert tcp $EXTERNAL_NET any -> $HOME_NET 22 (msg:"ET SCAN LibSSH Based Scanner"; sid:2027974; rev:1;)
```

### API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/ids/alerts` | Get recent alerts (supports filtering) |
| `GET` | `/api/v1/ids/rules` | List all available signatures |
| `POST` | `/api/v1/ids/rules/{sid}/toggle` | Enable/Disable a rule |
| `GET` | `/api/v1/ids/stats` | Get attack statistics (24h) |

## Usage

### Viewing Alerts
Navigate to the **IDS / IPS** section in the sidebar. The dashboard shows:
- **Total Alerts**: Number of threats detected in the last 24 hours.
- **Severity Breakdown**: High vs Medium vs Low severity events.
- **Recent Alerts**: Detailed list of the latest detections.

### Managing Rules
1. Go to **IDS / IPS** -> **Rules** (or click "Manage Rules" on the dashboard).
2. Use the search bar to find specific signatures (e.g., "SQL", "Trojan").
3. Toggle the switch to Enable/Disable a rule.
4. Changes are applied immediately (mocked in dev, triggers reload in prod).

## Troubleshooting

### No Alerts Appearing?
1. Ensure the demo server is running: `python src/demo/demo_server.py`.
2. Check if `eve.json` is being generated in the root directory.
3. Verify `LogMonitor` logs in the console.

### API Errors
- Check `http://localhost:8000/docs` to verify endpoints are up.
- Ensure `src` is in your `PYTHONPATH`.
