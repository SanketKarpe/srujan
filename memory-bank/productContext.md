# Product Context

## Problem Statement
Smart homes are increasingly populated by IoT devices (cameras, speakers, thermostats) that often lack robust security, receive infrequent patches, and may have privacy-invasive "call-home" features. These "low-trust" devices share the same network as "high-trust" devices (laptops, phones), creating a risk where a compromised toaster could attack a personal computer (cross-infection).

## Solution
Srujan acts as a secure gateway and network manager. It segregates the home network into zones, isolating vulnerable IoT devices from critical personal devices. It actively monitors traffic for malicious activity and blocks communication with known bad actors.

## User Experience
- **Setup**: User installs Srujan on a Raspberry Pi, configuring it as the network gateway/DHCP server.
- **Operation**: Srujan automatically identifies devices and assigns them to appropriate VLANs or subnets.
- **Monitoring**: Users view a dashboard to see connected devices, their status, and any blocked threats.
- **Control**: Users can manually quarantine devices or adjust security settings.
