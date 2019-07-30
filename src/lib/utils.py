#!/usr/bin/python3
import os
import pathlib
from lib.config import *
from gglsbl import SafeBrowsingList

import requests

from elasticsearch import Elasticsearch
from datetime import datetime
from manuf import manuf


sbl = None


# deprecated
def create_config_file_dep(config_file):
    """

    Args:
        config_file ():

    Returns:

    """
    file = pathlib.Path(config_file)
    if file.exists():
        return
    else:
        with open(config_file, 'w') as fp:
            fp.write(CONFIG_FILE_HEADER)


def gsb_init():
    """

    Returns:

    """
    # noinspection PyBroadException
    try:
        return SafeBrowsingList(GSB_API_KEY, db_path=os.getcwd() + GSB_DB_NAME)
    except:
        return None


def remove_config_file(config_file):
    """

    Args:
        config_file ():

    Returns:

    """
    file = pathlib.Path(config_file)
    if file.exists():
        os.unlink(config_file)


def write_config(config_file, data,overwrite=True):
    """

    Args:
        config_file ():
        data ():
        overwrite ():

    Returns:

    """
    file = pathlib.Path(config_file)
    mode = 'w'
    if overwrite is True:
        if file.exists():
            os.rename(config_file,"/tmp/" + file.stem)
    else:
        mode = 'a'

    with open(config_file, mode) as fp:
        fp.write(data)


def read_config(config_file):
    """

    Args:
        config_file ():

    Returns:

    """
    file = pathlib.Path(config_file)
    if file.exists():
        with open(config_file, 'r') as fp:
            content = fp.read()
    else:
        content = None
    return content


def gsb_sync_local_db(sbl):
    """

    Args:
        sbl ():

    Returns:

    """
    sbl.update_hash_prefix_cache()


def gsb_lookup(dns):
    """

    Args:
        dns ():

    Returns:

    """
    try:
        return sbl.lookup_url(dns)
    except:
        return None


def remove_config(config_file, config_option):
    """

    Args:
        config_file ():
        config_option ():

    Returns:

    """
    new_config_file = []
    with open(config_file, 'r') as fp:
        for line in fp.readlines():
            if not line.__contains__(config_option):
                new_config_file.append(line)

    with open(config_file, 'w') as fp:
        for lines in new_config_file:
            fp.write(lines)



def send2es(json_data, index_name):
    """

    Args:
        json_data ():
        index_name ():

    Returns:

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
    file = pathlib.Path("/var/lib/misc/dnsmasq.leases")
    if file.exists():
        file.unlink()
    os.system("service dnsmasq stop")


def restart_dnsmasq():
    file = pathlib.Path("/var/lib/misc/dnsmasq.leases")
    if file.exists():
        file.unlink()
    os.system("service dnsmasq restart")


def mac_to_vendor(mac):
    """

    Args:
        mac ():

    Returns:

    """
    p = manuf.MacParser(update=False)
    return p.get_manuf_long(mac)

