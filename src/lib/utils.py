#!/usr/bin/python3
"""Utility functions for Srujan.

This module provides various utility functions for configuration management,
Google Safe Browsing integration, Elasticsearch interaction, and system operations.
"""
import os
import pathlib
import subprocess
from lib.config import *
from pysafebrowsing import SafeBrowsing

import requests

from elasticsearch import Elasticsearch
from datetime import datetime
from manuf import manuf


sbl = None

# Initialize MacParser once at module level for performance
try:
    _mac_parser = manuf.MacParser(update=False)
except Exception as e:
    print(f"Warning: Could not initialize MacParser: {e}")
    _mac_parser = None


# deprecated
def create_config_file_dep(config_file):
    """Creates a configuration file if it doesn't exist (Deprecated).

    Args:
        config_file (str): The path to the configuration file to create.
    """
    file = pathlib.Path(config_file)
    if file.exists():
        return
    else:
        with open(config_file, 'w') as fp:
            fp.write(CONFIG_FILE_HEADER)


def gsb_init():
    """Initializes the Google Safe Browsing client.

    Returns:
        SafeBrowsing: An instance of SafeBrowsing client if successful, None otherwise.
    """
    try:
        return SafeBrowsing(GSB_API_KEY)
    except Exception as e:
        print(f"Error initializing GSB: {e}")
        return None


def remove_config_file(config_file):
    """Removes a configuration file if it exists.

    Args:
        config_file (str): The path to the configuration file to remove.
    """
    file = pathlib.Path(config_file)
    if file.exists():
        os.unlink(config_file)


def write_config(config_file, data, overwrite=True):
    """Writes data to a configuration file.

    Args:
        config_file (str): The path to the configuration file.
        data (str): The data to write to the file.
        overwrite (bool, optional): Whether to overwrite the file if it exists. 
            If True, the existing file is moved to /tmp/. Defaults to True.
    """
    file = pathlib.Path(config_file)
    mode = 'w'
    if overwrite is True:
        if file.exists():
            # Fix path traversal vulnerability
            safe_stem = os.path.basename(file.stem)
            backup_path = os.path.join("/tmp", safe_stem)
            try:
                os.rename(config_file, backup_path)
            except (FileNotFoundError, OSError) as e:
                print(f"Warning: Could not backup config file: {e}")
    else:
        mode = 'a'

    with open(config_file, mode) as fp:
        fp.write(data)


def read_config(config_file):
    """Reads the content of a configuration file.

    Args:
        config_file (str): The path to the configuration file.

    Returns:
        str: The content of the file if it exists, None otherwise.
    """
    file = pathlib.Path(config_file)
    if file.exists():
        with open(config_file, 'r') as fp:
            content = fp.read()
    else:
        content = None
    return content


def gsb_sync_local_db(sbl):
    """Syncs the local Google Safe Browsing database.

    Note: pysafebrowsing uses the Lookup API, so no local DB sync is needed.
    This function is kept for compatibility but does nothing.

    Args:
        sbl (object): The SafeBrowsing instance.
    """
    pass


def gsb_lookup(dns):
    """Looks up a URL in the Google Safe Browsing database.

    Args:
        dns (str): The URL or domain to lookup.

    Returns:
        dict: The threat information if found, None otherwise.
    """
    try:
        # pysafebrowsing expects a list of URLs
        response = sbl.lookup_urls([dns])
        if response and dns in response and response[dns]['malicious']:
            return response[dns]
        return None
    except Exception as e:
        print(f"Error in GSB lookup: {e}")
        return None


def remove_config(config_file, config_option):
    """Removes lines containing a specific option from a configuration file.

    Args:
        config_file (str): The path to the configuration file.
        config_option (str): The option string to search for and remove.
    """
    new_config_file = []
    with open(config_file, 'r') as fp:
        for line in fp.readlines():
            if config_option not in line:
                new_config_file.append(line)

    with open(config_file, 'w') as fp:
        for lines in new_config_file:
            fp.write(lines)



def send2es(json_data, index_name):
    """Sends JSON data to Elasticsearch.

    Args:
        json_data (dict): The data to index.
        index_name (str): The name of the Elasticsearch index.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:

        es = Elasticsearch([{'host': HOST_ADDR, 'port': ES_PORT}])
        url = "http://"+HOST_ADDR+':'+ES_PORT
        #print(url)
        res = requests.get(url)
        if res.status_code != 200:
            return False
        if '@timestamp' not in json_data and json_data is not None:
            json_data['@timestamp'] = datetime.utcnow()
            es.index(index=index_name, body=json_data)
        return True
    except Exception as e:
        print(e)
        return False


def stop_dnsmasq():
    """Stops the dnsmasq service and removes the lease file."""
    file = pathlib.Path("/var/lib/misc/dnsmasq.leases")
    if file.exists():
        file.unlink()
    try:
        subprocess.run(["systemctl", "stop", "dnsmasq"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error stopping dnsmasq: {e}")


def restart_dnsmasq():
    """Restarts the dnsmasq service and removes the lease file."""
    file = pathlib.Path("/var/lib/misc/dnsmasq.leases")
    if file.exists():
        file.unlink()
    try:
        subprocess.run(["systemctl", "restart", "dnsmasq"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error restarting dnsmasq: {e}")


def mac_to_vendor(mac):
    """Resolves a MAC address to its manufacturer.

    Args:
        mac (str): The MAC address to resolve.

    Returns:
        str: The manufacturer name, or None if not found.
    """
    if _mac_parser is None:
        return None
    try:
        return _mac_parser.get_manuf_long(mac)
    except Exception:
        return None

