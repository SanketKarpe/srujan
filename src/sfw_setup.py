#!/usr/bin/python3
# import sys
import json
from datetime import datetime
# import traceback
from lib.utils import *
from lib.config import *
# from lib.logger import QLogger
from sfw_dhcp import seed_dhcp__tags
from sfw_dns import seed_dns_blacklist
from argparse import ArgumentParser
import string


# logger_obj = QLogger("setup", ".", "lib-logfile.log")
# log = logger_obj.q_logger


def create_core_config(core_config):
    """

    Args:
        core_config ():

    Returns:

    """
    core_config_data = [CONFIG_FILE_HEADER]
    for interfaces in core_config["interfaces"]:
        core_config_data.append("interface=" + interfaces + "\n")

    core_config_data.append("\n")
    log_path = core_config["logging"]["log_path"]
    core_config_data.append("log-facility=" + log_path["log-facility"] + "\n")

    core_config_data.append("\n")
    for options_directive, option_status in core_config["logging"]["logging_options"].items():
        if option_status is True:
            core_config_data.append(options_directive + "\n")
    write_config(DNSMASQ_CORE_CONFIGURATION, "".join(core_config_data))


def create_dhcp_config(dhcp_config):
    """

    Args:
        dhcp_config ():

    Returns:

    """

    dhcp_config_data = [CONFIG_FILE_HEADER]
    for options_directive, option_status in dhcp_config["dhcp-core-options"].items():
        if option_status is True:
            dhcp_config_data.append(options_directive)

    dhcp_config_data.append("\n")
    dhcp_script_log_path = dhcp_config["dhcp-script"]
    dhcp_config_data.append("dhcp-script=" + dhcp_script_log_path + "\n")

    for subnet in dhcp_config["subnets"]:
        dhcp_range = "dhcp-range=tag:" + subnet + SEP + dhcp_config["subnets"][subnet]["dhcp-range"]["start_ip"] + SEP + \
                     dhcp_config["subnets"][subnet]["dhcp-range"]["end_ip"] + SEP + dhcp_config["subnets"][subnet]["dhcp-range"]["duration"]
        dhcp_config_data.append(dhcp_range + "\n")

        for dhcp_option, option_value in dhcp_config["subnets"][subnet]["dhcp-options"].items():
            dhcp_config_data.append("dhcp-option=tag:" + subnet + SEP + dhcp_option + SEP + option_value + "\n")
        dhcp_config_data.append("\n")
    write_config(DNSMASQ_DHCP_CONFIGURATION, "".join(dhcp_config_data))


def create_dns_config(dns_config):
    """

    Args:
        dns_config ():

    Returns:

    """
    dns_config_data = [CONFIG_FILE_HEADER]

    for options_directive, option_status in dns_config["dns-options"].items():
        if option_status is True:
            dns_config_data.append(options_directive + "\n")

    for server_ip in dns_config["servers"]:
        dns_config_data.append("server=" + server_ip + "\n")

    write_config(DNSMASQ_DNS_CONFIGURATION, "".join(dns_config_data))


def create_sfw_config_files(json_file):
    """

    Args:
        json_file ():

    Returns:

    """

    try:
        print("Stopping dnsmasq service : " + str(datetime.now() ))
        stop_dnsmasq()
        with open(json_file) as json_data_file:
            config_data = json.load(json_data_file)
            create_core_config(config_data["core"])
            create_dhcp_config(config_data["dhcp"])
            create_dns_config(config_data["dns"])
        seed_dns_blacklist()
        seed_dhcp__tags()
        # log.info(logger_obj.format_msg(description="Config loaded"))
        restart_dnsmasq()
        print("Restarted dnsmasq service : " + str(datetime.now() ))
        return True
    except Exception as e:
        # log.info(logger_obj.format_msg(error_code=500, description="Internal Server Error:  %s") % e)
        print(e)
        return False


def configure_ip_forward():
    with open("/etc/sysctl.conf","r+") as conf:
        for line in conf:
            if line.strip() == "net.ipv4.ip_forward=1":
                return
    with open("/etc/sysctl.conf","a") as conf:
        conf.write("net.ipv4.ip_forward=1")


if __name__ == "__main__":

    configure_ip_forward()
    # parse command line arguments
    usage = "usage: %prog [options] arg1"

    parser = ArgumentParser()
    parser.add_argument('-i', '--config', action="store", dest="config_file",
                        help="Path to config file",
                        default=SFW_DEFAULT_CONFIG_PATH)

    args = parser.parse_args()

    if args.config_file is not None:
        print("Using %s as config file" % SFW_DEFAULT_CONFIG_PATH)
        if create_sfw_config_files(args.config_file):
            print("SFW configuration created successfully")
        else:
            print("Error in creating configuration files. Please check error logs")
    else:
        parser.print_help()
