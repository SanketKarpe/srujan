#!/usr/bin/python3
"""Iptables management module for Srujan.

This module handles the seeding of iptables rules and related configurations
based on device tags and DNS blacklists.
"""
from lib.utils import *
from lib.config import *
from sfw_dhcp import add_mac_tag, add_vendorclass_tag
from sfw_dns import add_dns_block
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
    """Seeds DHCP tags for iptables integration.

    Configures MAC and vendor class tags based on the provided seed tags.

    Args:
        seed_tags (dict): A dictionary containing 'tags' with 'iot' and 'non_iot' lists.
    """
    # create_config_file(TAG_CONF_PATH)
    # create_config_file(NON_IOT_CONF_PATH)

    iot_tags = seed_tags["tags"]["iot"]
    non_iot_tags = seed_tags["tags"]["non_iot"]

    for mac in iot_tags["mac"]:
        add_mac_tag("iot", mac)

    for vendorid in iot_tags["vendorclass"]:
        add_vendorclass_tag("iot", vendorid)


def seed_dns_blacklist(dns_blacklists):
    """Seeds DNS blacklist rules.

    Configures DNS blocking for specified URLs by redirecting them to a sinkhole IP.

    Args:
        dns_blacklists (dict): A dictionary containing 'sink_ip' and 'urls' list.
    """
    # create_config_file(DNS_BLACKLIST_PATH)
    sink_ip = dns_blacklists["sink_ip"]
    for dns_entry in dns_blacklists["urls"]:
        add_dns_block(sink_ip, dns_entry)


def seed_iptables_rules(seed_rules):
    """Seeds initial iptables rules.

    Args:
        seed_rules (dict): A dictionary containing initial iptables rules (currently unused).
    """
    return
