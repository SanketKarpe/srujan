# Project Brief: Srujan

Srujan is a network segregation system designed for smart homes, running on Raspberry Pi. It aims to secure home networks by isolating low-trust IoT devices from high-trust devices like computers and smartphones.

## Core Features
- **Intelligent Segregation**: Separates devices into different network zones based on device type.
- **Threat Detection**: Identifies and alerts on contacts to blacklisted IPs/domains (Google Safe Browsing, hpHosts, Spamhaus).
- **Device Management**: Quarantine untrusted devices, prevent call-home pings.
- **Integration**: Works with ANWI (All New Wireless IDS) and SIEM systems.
- **Reporting**: Provides a dashboard for network usage and threats.

## Goals
- Mitigate cross-infection risks from vulnerable IoT devices.
- Enhance privacy by blocking unauthorized data transmission.
- Provide visibility into home network traffic and device behavior.
