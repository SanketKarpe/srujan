# Srujan Web Dashboard - Setup Guide

## Quick Start

This guide will help you set up and run the Srujan web dashboard.

---

## Prerequisites

- Python 3.8+
- Node.js 18+ and npm
- Raspberry Pi or Linux system with Srujan installed
- Running Elasticsearch and Redis instances

---

## Backend API Setup

### 1. Install API Dependencies

```bash
cd src/api
pip install -r requirements.txt
```

### 2. Start the API Server

**Development:**
```bash
cd src/api
python3 main.py
```

Or using uvicorn directly:
```bash
cd src/api
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Production (with systemd):**

Create `/etc/systemd/system/srujan-api.service`:
```ini
[Unit]
Description=Srujan API Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/srujan/src/api
ExecStart=/usr/bin/python3 /home/pi/srujan/src/api/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable srujan-api
sudo systemctl start srujan-api
sudo systemctl status srujan-api
```

---

## Frontend Dashboard Setup

### 1. Install Dependencies

```bash
cd web
npm install
```

### 2. Start Development Server

```bash
cd web
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### 3. Build for Production

```bash
cd web
npm run build
```

This creates a `dist/` folder with optimized static files.

### 4. Serve Production Build

**Option A: Using Nginx**

Install nginx:
```bash
sudo apt-get install nginx
```

Create `/etc/nginx/sites-available/srujan`:
```nginx
server {
    listen 80;
    server_name srujan.local;

    root /home/pi/srujan/web/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/v1/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/srujan /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Option B: Simple Python Server**

```bash
cd web/dist
python3 -m http.server 3000
```

---

## Configuration

### Environment Variables

Create `.env` file in `web/` directory (optional):
```
VITE_API_URL=http://localhost:8000
```

### API Configuration

The API uses configuration from `src/lib/config.py`. Make sure:
- Elasticsearch is running on configured host/port
- Redis is running
- GSB API key is set (if using Google Safe Browsing)

---

## Accessing the Dashboard

### Local Access
- Development: `http://localhost:3000`
- Production: `http://raspberry-pi-ip`

### Remote Access

**Option 1: SSH Tunnel**
```bash
ssh -L 3000:localhost:3000 pi@raspberry-pi-ip
```
Then access `http://localhost:3000` on your machine

**Option 2: Tailscale/ZeroTier**
Install Tailscale on your Raspberry Pi for secure remote access

---

## Features

### Current (MVP)
- ✅ Real-time device discovery and listing
- ✅ Network statistics dashboard
- ✅ Device blocking/allowing
- ✅ Threat feed from Elasticsearch
- ✅ WebSocket real-time updates
- ✅ Mobile-responsive design

### Coming Soon
- ⏳ Device detail pages
- ⏳ Network topology visualization
- ⏳ Custom device naming
- ⏳ Traffic analytics
- ⏳ Setup wizard
- ⏳ Settings management

---

## Troubleshooting

### API Not Starting
```bash
# Check if port 8000 is in use
sudo netstat -tlnp | grep 8000

# Check API logs
cd src/api
python3 main.py
```

### Frontend Build Errors
```bash
# Clear node modules and reinstall
cd web
rm -rf node_modules package-lock.json
npm install
```

### No Devices Showing
- Check if dnsmasq is running: `sudo systemctl status dnsmasq`
- Check if dnsmasq.leases file exists: `ls /var/lib/misc/dnsmasq.leases`
- Check Elasticsearch: `curl http://localhost:9200/_cat/indices`

### WebSocket Connection Failed
- Check if API is running
- Check browser console for errors
- Ensure WebSocket endpoint is accessible

---

## Development

### Backend Development
API code is in `src/api/main.py`. The API automatically reloads when code changes.

### Frontend Development
Components are in `web/src/components/`. Vite provides hot module replacement.

### API Endpoints

```
GET    /api/v1/devices              # List all devices
GET    /api/v1/devices/{mac}        # Get device details
POST   /api/v1/devices/{mac}/block  # Block device
POST   /api/v1/devices/{mac}/allow  # Allow device
GET    /api/v1/network/stats        # Network statistics
GET    /api/v1/threats/recent       # Recent threats
WS     /api/v1/ws                   # WebSocket endpoint
```

Full API documentation: `http://localhost:8000/docs` (FastAPI auto-generated)

---

## Security Notes

1. **Production Access:** Always use HTTPS in production
2. **Authentication:** Currently no authentication - add auth before exposing to internet
3. **Firewall:** Restrict API access to trusted networks
4. **Updates:** Keep dependencies updated regularly

---

## Support

- GitHub Issues: https://github.com/SanketKarpe/srujan/issues
- Documentation: See `docs/` folder

---

**Happy Monitoring! 🛡️**
