# Tech Context

## Technology Stack
- **Language**: Python 3
- **OS**: Raspbian (Linux)
- **Infrastructure**:
    - **Redis**: Used for state management and task queues (`rq`).
        - **Queues**: `dhcp` (device processing), `mac_ip` (logging), `ip_scan` (nmap), `dns` (logging).
    - **Elasticsearch**: Used for data storage/indexing.
        - **Indices**: `mac_ip` (device mapping), `ip_scan` (scan results), `ip_dns` (DNS logs).
- **Key Python Libraries**:
    - `python-libnmap`: Interface for Nmap.
    - `rq`: Redis Queue for background job processing.
    - `manuf`: MAC address to manufacturer parsing.
    - `tailer`: For reading log files.
    - *(Removed: `gglsbl`, `spam_lists` due to deprecation)*
- **System Dependencies**:
    - `dnsmasq`: For DHCP and DNS services (replaces `isc-dhcp-server`).
    - `iptables`: For firewalling.
    - `nmap`: For device scanning.

## Development Setup
- **Source**: `src/` directory contains the Python logic.
- **Config**: `src/config_files/` and `src/system_config_files/` hold templates or default configurations.
- **Installation**: `pip install -r requirements.txt` and system package installs via `apt`.

## Key Constraints
- **Hardware**: Limited resources of Raspberry Pi. Running Elasticsearch on a Pi might be resource-intensive.
- **Network**: Requires physical setup with dual NICs (built-in + USB adapter).
