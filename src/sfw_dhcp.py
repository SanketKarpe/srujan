#!/usr/bin/python3
import os
import json

from lib.config import *
from lib.utils import *


def seed_dhcp__tags():
    """

    Args:
        seed_tags ():

    Returns:

    """
    # create_config_file(TAG_CONF_PATH)
    # create_config_file(NON_IOT_CONF_PATH)
    conf_file = DNSMASQ_CONFIGURATION_PATH + "iot" + DNSMASQ_CONFIGURATION_EXT
    remove_config_file(conf_file)
    conf_file = DNSMASQ_CONFIGURATION_PATH + "non_iot" + DNSMASQ_CONFIGURATION_EXT
    remove_config_file(conf_file)
    with open(SEED_DEVICE_CATEGORY) as json_data_file:
        seed_tags = json.load(json_data_file)
        mac_tags = seed_tags["mac"]
        vendor_class_tags = seed_tags["vendor_class"]

        for iot_mac in mac_tags["iot"]:
            add_mac_tag("iot", iot_mac)

        for non_iot_mac in mac_tags["non_iot"]:
            add_mac_tag("iot", non_iot_mac)

        for iot_vendorclass in vendor_class_tags["iot"]:
            add_vendorclass_tag("iot", iot_vendorclass)

        for non_iot_vendorclass in vendor_class_tags["non_iot"]:
            add_vendorclass_tag("non_iot", non_iot_vendorclass)


def mac_to_oui(mac):
    """

    Args:
        mac ():

    Returns:

    """
    mac_tmp = mac.split(":")
    mac_oui = mac_tmp[0] + ":" + mac_tmp[1] + ":" + mac_tmp[2] + ":*:*:*"
    return mac_oui


def log_ip_mac(mac, ip):
    """

    Args:
        mac ():
        ip ():

    Returns:

    """
    # log to ELK function
    vendor = mac_to_vendor(mac)
    jdata = {"mac": mac, "ip": ip,"manufacturer" : vendor}
    send2es(json_data=jdata, index_name="mac_ip")


def restart_dnsmasq():
    """

    Returns:

    """
    os.system("service dnsmasq stop")
    try:
        os.unlink(DNSMASQ_DHCP_LEASE_FILE)
    except:
        pass
    os.system("service dnsmasq restart")

def process_new_device(mac):
    """

    Args:
        mac ():

    Returns:

    """
    device_category = get_device_category(mac)
    print("MAC : " + str(mac) + "," + device_category)
    add_mac_tag(device_category, mac)
    restart_dnsmasq()


# dhcp-mac=set:non-iot,D0:04:01:*:*:*
def add_mac_tag(tag, mac):
    """

    Args:
        tag ():
        mac ():

    Returns:

    """
    mac_oui = mac_to_oui(mac)
    tag_data = "dhcp-mac=set:" + tag.strip() + "," + mac_oui + "\n"
    write_config(DNSMASQ_CONFIGURATION_PATH + tag + DNSMASQ_CONFIGURATION_EXT, tag_data,overwrite=False)


# dhcp-vendorclass=set:non-iot,"MSFT"
def add_vendorclass_tag(tag, vendorid,overwrite=False):
    """

    Args:
        tag ():
        vendorid ():

    Returns:

    """
    tag_data = "dhcp-vendorclass=set:" + tag.strip() + "," + vendorid + "\n"
    write_config(DNSMASQ_CONFIGURATION_PATH + tag + DNSMASQ_CONFIGURATION_EXT, tag_data,overwrite=False)


def remove_tag(tag, tag_data):
    """

    Args:
        tag ():
        tag_data ():

    Returns:

    """
    if len(tag_data) == 18:
        tag_data = mac_to_oui(tag_data)
    new_config_file = []
    config_file = read_config(DNSMASQ_CONFIGURATION_PATH + tag + ".conf")
    for line in config_file:
        if not line.__contains__(tag_data):
            new_config_file.append(line)
    write_config(DNSMASQ_CONFIGURATION_PATH + tag + ".conf", new_config_file)

def get_device_category(mac):
    """

    Args:
        mac ():

    Returns:

    """
    vendor = mac_to_vendor(mac)
    return vendor_to_category(vendor)


def vendor_to_category(found_vendor):
    """

    Args:
        found_vendor ():

    Returns:

    """
    vendor_category_mapping = json.loads(read_config(MANUFACTURER_CATEGORY_MAPPING))
    for category in vendor_category_mapping:
        for manufacturer_name in vendor_category_mapping[category]:
            if found_vendor.lower() == manufacturer_name.lower():
                return category

    return DEFAULT_DEVICE_CATEGORY

