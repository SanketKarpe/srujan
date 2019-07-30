#!/usr/bin/python3
from lib.utils import *
from lib.config import *
import iptc

"""
SEED IPTABLES RULES

- Seed iptable rules to be provided as json or as iptables-save ?
Iptables-save is easier and better as no need to create new format schema to save

- can create all rules manually and then do iptables-save
- modify iptables-save file and replace IP with variable names
- python script will replace the variables with IP range specified by user or based on environment

Rule Sequence

- Flush all rules
- 

- Deny All flow to non_iot from IOT with logging enabled
- Allow all flow from non_iot to IOT  logging enabled
- Allow all EXISTING flows from IOT to non_iot
- DENY Too many packets from IOT to NON_IOT //why
- Allow UDP broadcast from IOT to NON_IOT
- FORWARD all broadcast packet from non_iot to IOT

"""

"""
CUSTOM IPTABLES RULES

e.g

MAIN == NON_IOT ( Use MAIN as non_iot subnet name

IOT + IOT
- 

"""


def seed_dhcp__tags(seed_tags):
    # create_config_file(TAG_CONF_PATH)
    # create_config_file(NON_IOT_CONF_PATH)

    iot_tags = seed_tags["tags"]["iot"]
    non_iot_tags = seed_tags["tags"]["non_iot"]

    for mac in iot_tags["mac"]:
        add_mac_tag("iot", mac)

    for vendorid in iot_tags["vendorclass"]:
        add_vendorclass_tag("iot", vendorid)


def seed_dns_blacklist(dns_blacklists):
    # create_config_file(DNS_BLACKLIST_PATH)
    sink_ip = dns_blacklists["sink_ip"]
    for dns_entry in dns_blacklists["urls"]:
        add_dns_block(sink_ip, dns_entry)


def seed_iptables_rules(seed_rules):
    return
