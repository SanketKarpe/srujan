#!/usr/bin/python3
"""DNS management module for Srujan.

This module handles DNS blacklisting, enrichment with threat intelligence,
and logging of DNS queries.
"""
import os
import ipaddress
import json
from lib.utils import *
from lib.config import GSB_ENABLE
from sfw_lookup import ti_lookup


def seed_dns_blacklist():
    """Seeds the DNS blacklist configuration.

    Reads the seed DNS blocklist file and configures dnsmasq to block specified domains
    by redirecting them to a sinkhole IP.
    """
    # create_config_file(DNS_BLACKLIST_PATH)
    remove_config_file(DNSMASQ_DNS_BLOCKLIST)
    try:
        with open(SEED_DNS_BLOCKLIST) as json_data_file:
            dns_blacklists = json.load(json_data_file)
            sink_ip = dns_blacklists["sink_ip"]
            for dns_entry in dns_blacklists["urls"]:
                add_dns_block(sink_ip, dns_entry)
    except FileNotFoundError:
        print(f"Error: {SEED_DNS_BLOCKLIST} not found")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {SEED_DNS_BLOCKLIST}: {e}")


def add_dns_block(sink_ip, dns_entry):
    """Adds a DNS block rule to the configuration.

    Args:
        sink_ip (str): The IP address to redirect blocked domains to.
        dns_entry (str): The domain name to block.
    """
    dns_blacklists_data = f"address=/{dns_entry.strip()}/{sink_ip}\n"
    write_config(DNSMASQ_DNS_BLOCKLIST, dns_blacklists_data, overwrite=False)


def remove_dns_block(dns_entry):
    """Removes a DNS block rule from the configuration.

    Args:
        dns_entry (str): The domain name to unblock.
    """
    new_config_file = []
    config_data = read_config(DNSMASQ_DNS_BLOCKLIST)
    for line in config_data:
        if not line.__contains__(dns_entry):
            new_config_file.append(line)
    write_config(DNSMASQ_DNS_BLOCKLIST, new_config_file)


# To Do : Add more lookups sources
def enrich_dns(dns):
    """Enriches a DNS query with threat intelligence data.

    Checks the domain against enabled threat intelligence sources (Spamhaus, Google Safe Browsing, etc.).

    Args:
        dns (str): The domain name to check.

    Returns:
        list: A list of tags or threat indicators found for the domain.
    """
    result = []
    if TI_ENABLE:
        result = ti_lookup(dns)
    if GSB_ENABLE:
        gsb_result = gsb_lookup(dns)
        if gsb_result:
            result.append("GSB")
    if dns.__contains__("malware"):
        result.append("MALICIOUS")
    return result


def log_dns(dns, ip):
    """Logs a DNS query and its enrichment data to Elasticsearch.

    Args:
        dns (str): The domain name queried.
        ip (str): The IP address of the client.
    """
    ti_tag = []
    ti_tag = enrich_dns(dns)

    jdata = {"ip": ip, "dns": dns}
    if ti_tag is not None:
        jdata["tags"] = ti_tag

    send2es(json_data=jdata, index_name="ip_dns")
