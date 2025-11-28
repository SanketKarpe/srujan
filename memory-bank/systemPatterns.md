# System Patterns

## Architecture
Srujan operates as a network appliance, likely sitting between the ISP modem and the home network, or acting as a router for a sub-network.

- **Hardware**: Raspberry Pi (3 or 4).
- **Network Interface**: Requires two network interfaces (eth0, eth1) – one for upstream (WAN/existing LAN) and one for the segregated network (LAN).
- **Core Services**:
    - **DHCP Server (`dnsmasq`)**: Manages IP assignment, directs devices to specific subnets/VLANs based on fingerprints, and logs events for the controller.
    - **Firewall (`iptables`)**: Enforces isolation rules, blocking traffic between zones and to blacklisted external IPs.
    - **DNS/Lookup**: Intercepts DNS requests or monitors traffic to check against threat feeds (Google Safe Browsing, etc.).

## Key Components
- **`sfw.py`**: **Main Controller**. Monitors `dnsmasq` logs for DHCP (DISCOVER, ACK) and DNS queries. Pushes events to Redis queues (`dhcp`, `mac_ip`, `ip_scan`, `dns`).
- **`sfw_dhcp.py`**: **DHCP Manager**. Handles device categorization (IoT vs Non-IoT), tagging in `dnsmasq` config, and restarting the service.
- **`sfw_nmap_scan.py`**: **Scanner**. Consumes from `ip_scan` queue. Performs active Nmap scans (`-Pn -O -sV`) to fingerprint devices and pushes results to Elasticsearch (`ip_scan` index).
- **`sfw_dns.py`**: **DNS Guard**. Consumes from `dns` queue. Enriches DNS queries with threat intel (Spamhaus, GSB) and logs to Elasticsearch (`ip_dns` index).
- **`sfw_iptables.py`**: **Firewall Manager**. Seeds `iptables` rules based on device tags and DNS blacklists (redirecting to sinkhole).
- **`sfw_lookup.py`**: **Threat Intel**. Provides `ti_lookup` function to check domains against Spamhaus (ZEN, DBL) and HpHosts.
- **`sfw_setup.py`**: **Configurator**. Generates `dnsmasq` configuration files (core, DHCP, DNS) from a master JSON config.

## Data Flow
1.  **Event Ingestion**: `sfw.py` tails `dnsmasq.log`.
2.  **DHCP Events**:
    *   New device (DHCPDISCOVER) -> `dhcp` queue -> `sfw_dhcp.py` (Categorize & Tag).
    *   IP Assignment (DHCPACK) -> `mac_ip` queue -> `sfw_dhcp.py` (Log to ES).
    *   IP Assignment (DHCPACK) -> `ip_scan` queue -> `sfw_nmap_scan.py` (Active Scan).
3.  **DNS Events**:
    *   Query Logged -> `dns` queue -> `sfw_dns.py` (Enrich & Log to ES).
4.  **Storage**:
    *   **Redis**: Queues and state.
    *   **Elasticsearch**: Long-term storage for device info (`mac_ip`), scan results (`ip_scan`), and DNS logs (`ip_dns`).

## Design Patterns
- **Log-Based Event Bus**: The system relies on parsing `dnsmasq` logs to trigger actions, decoupling the core network service from the Python logic.
- **Producer-Consumer**: `sfw.py` produces events to Redis queues; worker scripts (`sfw_dhcp`, `sfw_dns`, `sfw_nmap_scan`) consume and process them.
- **Configuration-as-Code**: `sfw_setup.py` generates infrastructure config (dnsmasq) from a structured JSON definition.
