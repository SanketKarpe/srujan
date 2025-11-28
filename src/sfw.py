#!/usr/bin/python3
"""Main controller script for Srujan.

This script monitors dnsmasq logs for DHCP and DNS events, and queues tasks
for device processing, IP scanning, and DNS logging.
"""
import ipaddress
import re
import time

import tailer
from redis import Redis
from rq import Queue

from lib.config import DNSMASQ_LOG_FILE, GSB_ENABLE
from lib.utils import gsb_init
from sfw_dhcp import process_new_device, log_ip_mac, restart_dnsmasq
from sfw_dns import log_dns
from sfw_nmap_scan import nmap_scan_ip

"""

Jun 24 00:21:24 dnsmasq-dhcp[1022]: DHCPDISCOVER(eth0) d0:04:01:5d:01:cd
Jun 24 00:21:24 dnsmasq-dhcp[1022]: DHCPOFFER(eth0) 192.168.1.82 d0:04:01:5d:01:cd
Jun 24 00:21:24 dnsmasq-dhcp[1022]: DHCPDISCOVER(eth1) d0:04:01:5d:01:cd no address available
Jun 24 00:21:24 dnsmasq-dhcp[1022]: DHCPREQUEST(eth0) 192.168.1.82 d0:04:01:5d:01:cd
Jun 24 00:21:24 dnsmasq-dhcp[1022]: DHCPACK(eth0)04:01:5d 192.168.1.82 d0::01:cd
Jun 24 00:21:25 dnsmasq-dhcp[1022]: DHCPREQUEST(eth1) 192.168.1.82 d0:04:01:5d:01:cd
Jun 24 00:21:25 dnsmasq-dhcp[1022]: DHCPNAK(eth1) 192.168.1.82 d0:04:01:5d:01:cd wrong server-ID

Jun 24 00:28:30 dnsmasq-dhcp[1719]: DHCPDISCOVER(eth0) d0:04:01:5d:01:cd no address available
Jun 24 00:28:30 dnsmasq-dhcp[1719]: DHCPDISCOVER(eth1) d0:04:01:5d:01:cd no address available
Jun 24 00:28:32 dnsmasq-dhcp[1719]: DHCPDISCOVER(eth0) d0:04:01:5d:01:cd no address available
Jun 24 00:28:32 dnsmasq-dhcp[1719]: DHCPDISCOVER(eth1) d0:04:01:5d:01:cd no address available

Jul  5 16:11:23 lib-prime dnsmasq[1650]: query[A] api.peer5.com from 192.168.1.82

"""

DHCPDISCOVER_NO_ADDRESS_ETH0 = r'.*(DHCPDISCOVER)\(eth0\).*([0-9a-f]{2}(?::[0-9a-f]{2}){5}).*no address available'
DHCPDISCOVER_NO_ADDRESS_ETH1 = r'.*(DHCPDISCOVER)\(eth1\).*([0-9a-f]{2}(?::[0-9a-f]{2}){5}).*no address available'
DHCPACK_IP_ADDRESS = r'.*DHCPOFFER.*\s((?:[0-9]{1,3}\.){3}[0-9]{1,3}).* ([0-9a-f]{2}(?::[0-9a-f]{2}){5})'
DNS_QUERY = r'.*query\[A\]\s(.*)\sfrom\s((?:[0-9]{1,3}\.){3}[0-9]{1,3})'

# Compile regex patterns at module level for performance
DHCPDISCOVER_NO_ADDRESS_ETH0_RE = re.compile(DHCPDISCOVER_NO_ADDRESS_ETH0)
DHCPDISCOVER_NO_ADDRESS_ETH1_RE = re.compile(DHCPDISCOVER_NO_ADDRESS_ETH1)
DHCPACK_IP_ADDRESS_RE = re.compile(DHCPACK_IP_ADDRESS)
DNS_QUERY_RE = re.compile(DNS_QUERY)

sbl = None

redis_conn = Redis()
new_device_queue = Queue('dhcp', connection=redis_conn)
ip_mac_queue = Queue('mac_ip', connection=redis_conn)
ip_scan_queue = Queue('ip_scan',connection=redis_conn)
dns_queue = Queue('dns', connection=redis_conn)


def add_dns_query_q(dns, ip):
    """Adds a DNS query to the processing queue.

    Args:
        dns (str): The domain name queried.
        ip (str): The IP address of the client making the query.
    """
    try:
        ip_class = ipaddress.IPv4Address(ip)
    except ValueError:
        print(f"Invalid IP address: {ip}")
        return
    
    # Do not process or log link-local or loopback DNS queries
    if not ip_class.is_link_local and not ip_class.is_loopback:
        dns_queue.enqueue(log_dns, dns, ip)


def add_device_q(mac):
    """Adds a new device to the processing queue.

    Args:
        mac (str): The MAC address of the new device.
    """
    new_device_queue.enqueue(process_new_device, mac)
    return


def add_ip_mac_log_q(ip, mac):
    """Adds an IP-MAC mapping to the logging queue.

    Args:
        ip (str): The IP address.
        mac (str): The MAC address.
    """
    ip_mac_queue.enqueue(log_ip_mac, mac, ip)
    return

def add_ip_scan_q(ip):
    """Adds an IP address to the scan queue.

    Args:
        ip (str): The IP address to scan.
    """
    ip_scan_queue.enqueue(nmap_scan_ip,ip,job_timeout=900)
    return


def run_sfw():
    """Main loop for Srujan Firewall.

    Monitors the dnsmasq log file for DHCP and DNS events and triggers appropriate actions.
    """
    prev_logline = ''
    
    # Initialize Google Safe Browsing client
    if GSB_ENABLE:
        sbl = gsb_init()

    prev_allocated_mac = ""
    
    # Use context manager to ensure file is properly closed
    with open(DNSMASQ_LOG_FILE) as log_file:
        for logline in tailer.follow(log_file):

            dhcp_ack = DHCPACK_IP_ADDRESS_RE.search(logline)
            if dhcp_ack:
                add_ip_mac_log_q(dhcp_ack.group(1), dhcp_ack.group(2))
                add_ip_scan_q(dhcp_ack.group(1))
                continue

            dhcp_discover_eth0 = DHCPDISCOVER_NO_ADDRESS_ETH0_RE.search(logline)
            dhcp_discover_eth1_prev = DHCPDISCOVER_NO_ADDRESS_ETH1_RE.search(prev_logline)
            # print("prev :",prev_logline)
            # print("current :", logline)
            if dhcp_discover_eth0 and dhcp_discover_eth1_prev:
                print("eth0,eth1 : ", dhcp_discover_eth0.group(2))
                if prev_allocated_mac != dhcp_discover_eth0.group(2):
                    add_device_q(dhcp_discover_eth0.group(2))
                    prev_logline = ""  # New need to confirm working
                    prev_allocated_mac = dhcp_discover_eth0.group(2)
                    time.sleep(1)
                    continue

            dhcp_discover_eth1 = DHCPDISCOVER_NO_ADDRESS_ETH1_RE.search(logline)
            dhcp_discover_eth0_prev = DHCPDISCOVER_NO_ADDRESS_ETH0_RE.search(prev_logline)
            if dhcp_discover_eth1 and dhcp_discover_eth0_prev:
                print("eth1,eth0 : ", dhcp_discover_eth1.group(2))
                if prev_allocated_mac != dhcp_discover_eth1.group(2):
                    add_device_q(dhcp_discover_eth1.group(2))
                    prev_logline = ""
                    prev_allocated_mac = dhcp_discover_eth1.group(2)
                    time.sleep(1)
                    continue

            dns_query = DNS_QUERY_RE.search(logline)
            if dns_query:
                # print(dns_query.group(1) + "," + dns_query.group(2))
                add_dns_query_q(dns_query.group(1), dns_query.group(2))
            prev_logline = logline


def main():
    """Entry point for the script."""
    restart_dnsmasq()
    run_sfw()


if __name__ == "__main__":
    main()
