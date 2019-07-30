#!/usr/bin/python3
import os

CONFIG_FILE_HEADER = "# Configuration file created by SFW\n"
SEP = ","

SFW_DEFAULT_CONFIG_PATH = os.getcwd() + "/config_files/sfw_config.json"

# dnsmasq configuration file
DNSMASQ_CONFIGURATION_PATH = "/etc/dnsmasq.d/"
DNSMASQ_CORE_CONFIGURATION = DNSMASQ_CONFIGURATION_PATH + "sfw_core.conf"
DNSMASQ_DHCP_CONFIGURATION = DNSMASQ_CONFIGURATION_PATH + "sfw_dhcp.conf"
DNSMASQ_DNS_CONFIGURATION = DNSMASQ_CONFIGURATION_PATH + "sfw_dns.conf"
DNSMASQ_DNS_BLOCKLIST = DNSMASQ_CONFIGURATION_PATH + "sfw_dns_blocklist.conf"
DNSMASQ_LOG_FILE = "/var/log/dnsmasq.log"
DNSMASQ_DHCP_LEASE_FILE = "/var/lib/misc/dnmasq.leases"
DNSMASQ_CONFIGURATION_EXT = ".conf"


# SFW seed data
SEED_DNS_BLOCKLIST = os.getcwd() + "/config_files/seed_dns_blocklist.json"
SEED_DEVICE_CATEGORY = os.getcwd() + "/config_files/seed_device_category.json"

# Data required at runtime
MANUFACTURER_CATEGORY_MAPPING = os.getcwd() + "/data/manufacturer_category.json"
SFW_BLACKLIST_PATH = os.getcwd() + "/data/"
SFW_BLACKLIST_EXTENSION = "list"

DEFAULT_DEVICE_CATEGORY = "non_iot"

# Threat Intel Configuration
GSB_API_KEY = 'GSB_KEY'
GSB_DB_NAME = os.getcwd() + "data/gsb_v4.db"
# Configuration Flags
GSB_ENABLE = False
TI_ENABLE = True

# Elasticsearch Details
HOST_ADDR = 'localhost'
ES_PORT = '9200'
NMAP_SCAN_INDEX = "ip_scan"

# ELK Config

HOST_ADDR = "HOST_IP"
ES_PORT = "9200"
