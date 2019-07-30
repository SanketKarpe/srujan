#!/usr/bin/python3
import os
import ipaddress
import json
from lib.utils import *
from lib.config import GSB_ENABLE
from sfw_lookup import ti_lookup


def seed_dns_blacklist():
    """

    Args:

    Returns:

    """
    # create_config_file(DNS_BLACKLIST_PATH)
    remove_config_file(DNSMASQ_DNS_BLOCKLIST)
    with open(SEED_DNS_BLOCKLIST) as json_data_file:
        dns_blacklists = json.load(json_data_file)
        sink_ip = dns_blacklists["sink_ip"]
        for dns_entry in dns_blacklists["urls"]:
            add_dns_block(sink_ip, dns_entry)


def add_dns_block(sink_ip, dns_entry):
    """

    Args:
        sink_ip ():
        dns_entry ():

    Returns:

    """
    dns_blacklists_data = "address=/" + dns_entry.strip() + "/" + sink_ip + "\n"
    write_config(DNSMASQ_DNS_BLOCKLIST, dns_blacklists_data, overwrite=False)


def remove_dns_block(dns_entry):
    """

    Args:
        dns_entry ():

    Returns:

    """
    new_config_file = []
    config_data = read_config(DNSMASQ_DNS_BLOCKLIST)
    for line in config_data:
        if not line.__contains__(dns_entry):
            new_config_file.append(line)
    write_config(DNSMASQ_DNS_BLOCKLIST, new_config_file)


# To Do : Add more lookups sources
def enrich_dns(dns):
    """

    Args:
        dns ():

    Returns:

    """
    result = []
    if TI_ENABLE:
        result = ti_lookup(dns)
    if GSB_ENABLE:
        result.append(gsb_lookup(dns))
    if dns.__contains__("malware"):
        result.append("MALICIOUS")
    return result


def log_dns(dns, ip):
    """

    Args:
        dns ():
        ip ():

    Returns:

    """
    ti_tag = []
    ti_tag = enrich_dns(dns)

    jdata = {"ip": ip, "dns": dns}
    if ti_tag is not None:
        jdata["tags"] = ti_tag

    send2es(json_data=jdata, index_name="ip_dns")
