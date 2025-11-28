#!/usr/bin/python3
"""DHCP management module for Srujan.

This module handles DHCP configuration, device tagging, and interaction with
the dnsmasq service.
"""
import os
import json
import subprocess

from lib.config import *
from lib.utils import *


def seed_dhcp__tags():
    """Seeds the DHCP configuration with initial device tags.

    Reads the seed device category file and configures initial MAC and vendor class tags
    for IoT and non-IoT devices.
    """
    # create_config_file(TAG_CONF_PATH)
    # create_config_file(NON_IOT_CONF_PATH)
    conf_file = DNSMASQ_CONFIGURATION_PATH + "iot" + DNSMASQ_CONFIGURATION_EXT
    remove_config_file(conf_file)
    conf_file = DNSMASQ_CONFIGURATION_PATH + "non_iot" + DNSMASQ_CONFIGURATION_EXT
    remove_config_file(conf_file)
    try:
        with open(SEED_DEVICE_CATEGORY) as json_data_file:
            seed_tags = json.load(json_data_file)
            mac_tags = seed_tags["mac"]
            vendor_class_tags = seed_tags["vendor_class"]

            for iot_mac in mac_tags["iot"]:
                add_mac_tag("iot", iot_mac)

            for non_iot_mac in mac_tags["non_iot"]:
                add_mac_tag("non_iot", non_iot_mac)  # Fixed: was incorrectly "iot"

            for iot_vendorclass in vendor_class_tags["iot"]:
                add_vendorclass_tag("iot", iot_vendorclass)

            for non_iot_vendorclass in vendor_class_tags["non_iot"]:
                add_vendorclass_tag("non_iot", non_iot_vendorclass)
    except FileNotFoundError:
        print(f"Error: {SEED_DEVICE_CATEGORY} not found")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing {SEED_DEVICE_CATEGORY}: {e}")
        return


def mac_to_oui(mac):
    """Converts a MAC address to its OUI format (XX:XX:XX:*:*:*).

    Args:
        mac (str): The MAC address.

    Returns:
        str: The OUI representation of the MAC address.
        
    Raises:
        ValueError: If MAC address format is invalid.
    """
    mac_tmp = mac.split(":")
    if len(mac_tmp) < 3:
        raise ValueError(f"Invalid MAC address format: {mac}")
    return ":".join(mac_tmp[:3]) + ":*:*:*"


def log_ip_mac(mac, ip):
    """Logs the IP and MAC address mapping to Elasticsearch.

    Args:
        mac (str): The MAC address.
        ip (str): The IP address.
    """
    # log to ELK function
    vendor = mac_to_vendor(mac)
    jdata = {"mac": mac, "ip": ip,"manufacturer" : vendor}
    send2es(json_data=jdata, index_name="mac_ip")


def restart_dnsmasq():
    """Restarts the dnsmasq service and clears the lease file."""
    try:
        subprocess.run(["systemctl", "stop", "dnsmasq"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error stopping dnsmasq: {e}")
    
    try:
        os.unlink(DNSMASQ_DHCP_LEASE_FILE)
    except FileNotFoundError:
        pass  # File doesn't exist, that's fine
    except Exception as e:
        print(f"Error removing lease file: {e}")
    
    try:
        subprocess.run(["systemctl", "restart", "dnsmasq"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error restarting dnsmasq: {e}")

def process_new_device(mac):
    """Processes a new device connecting to the network.

    Determines the device category, adds appropriate tags, and restarts dnsmasq.

    Args:
        mac (str): The MAC address of the new device.
    """
    try:
        device_category = get_device_category(mac)
        print(f"MAC: {mac}, Category: {device_category}")
        add_mac_tag(device_category, mac)
        restart_dnsmasq()
    except ValueError as e:
        print(f"Error processing device {mac}: {e}")
    except Exception as e:
        print(f"Unexpected error processing {mac}: {e}")


# dhcp-mac=set:non-iot,D0:04:01:*:*:*
def add_mac_tag(tag, mac):
    """Adds a DHCP MAC tag to the configuration.

    Args:
        tag (str): The tag name (e.g., 'iot', 'non-iot').
        mac (str): The MAC address to tag.
    """
    mac_oui = mac_to_oui(mac)
    tag_data = f"dhcp-mac=set:{tag.strip()},{mac_oui}\n"
    write_config(DNSMASQ_CONFIGURATION_PATH + tag + DNSMASQ_CONFIGURATION_EXT, tag_data,overwrite=False)


# dhcp-vendorclass=set:non-iot,"MSFT"
def add_vendorclass_tag(tag, vendorid, overwrite=False):
    """Adds a DHCP vendor class tag to the configuration.

    Args:
        tag (str): The tag name.
        vendorid (str): The vendor class identifier.
        overwrite (bool, optional): Whether to overwrite existing config. Defaults to False.
    """
    tag_data = f"dhcp-vendorclass=set:{tag.strip()},{vendorid}\n"
    write_config(DNSMASQ_CONFIGURATION_PATH + tag + DNSMASQ_CONFIGURATION_EXT, tag_data,overwrite=False)


def remove_tag(tag, tag_data):
    """Removes a tag from the configuration.

    Args:
        tag (str): The tag name.
        tag_data (str): The data associated with the tag to remove.
    """
    if len(tag_data) == 18:
        tag_data = mac_to_oui(tag_data)
    new_config_file = []
    config_file = read_config(DNSMASQ_CONFIGURATION_PATH + tag + ".conf")
    if config_file is None:
        print(f"Warning: Could not read config for tag {tag}")
        return
    for line in config_file:
        if tag_data not in line:
            new_config_file.append(line)
    write_config(DNSMASQ_CONFIGURATION_PATH + tag + ".conf", new_config_file)

def get_device_category(mac):
    """Determines the category of a device based on its MAC address.

    Args:
        mac (str): The MAC address.

    Returns:
        str: The device category (e.g., 'iot', 'non_iot').
    """
    vendor = mac_to_vendor(mac)
    if vendor is None:
        return DEFAULT_DEVICE_CATEGORY
    return vendor_to_category(vendor)


def vendor_to_category(found_vendor):
    """Maps a manufacturer name to a device category.

    Args:
        found_vendor (str): The manufacturer name.

    Returns:
        str: The device category.
    """
    config_content = read_config(MANUFACTURER_CATEGORY_MAPPING)
    if config_content is None:
        print(f"Warning: Could not read {MANUFACTURER_CATEGORY_MAPPING}")
        return DEFAULT_DEVICE_CATEGORY
    
    try:
        vendor_category_mapping = json.loads(config_content)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from {MANUFACTURER_CATEGORY_MAPPING}: {e}")
        return DEFAULT_DEVICE_CATEGORY
    
    for category in vendor_category_mapping:
        for manufacturer_name in vendor_category_mapping[category]:
            if found_vendor and found_vendor.lower() == manufacturer_name.lower():
                return category

    return DEFAULT_DEVICE_CATEGORY

