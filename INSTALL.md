# Installation steps for Srujan

## Quick Start (Demo Mode)
Run Srujan in demo mode on your local machine without a Raspberry Pi. This simulates devices and threats.

### Prerequisites
- Python 3.8+
- Node.js 16+

### Steps
1. **Install Backend Dependencies**
   ```bash
   pip install -r src/demo/requirements.txt
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd web
   npm install
   ```

3. **Start Demo Server**
   ```bash
   # From project root
   python src/demo/demo_server.py
   ```

4. **Start Frontend**
   ```bash
   # From web/ directory
   npm run dev
   ```
   Access the dashboard at `http://localhost:3000`.

---

## Full Installation (Raspberry Pi)

### OS requirements
Install latest version of Raspbian on Raspberry Pi 3 or 4.

### Packages to install
```bash
sudo apt install isc-dhcp-server
pip install -r requirements.txt
```

### Hardware requirements
Use any USB 3.0 to RJ45 Gigabit Ethernet Network Adapter (Can be skipped for Raspberry Pi 4).

### Configuration
1. Configure DHCP server to provide static IP on different subnets to eth0 and eth1.
2. Add route from eth0 to eth1 using:
   ```bash
   ip route add 192.168.1.0/24 via 192.168.10.1
   ```

