#!/usr/bin/python3
import sys
import os

import json
"""
'DNSMASQ_TAGS': 'non_iot eth0', 
'DNSMASQ_CLIENT_ID': '01:d0:04:01:5d:01:cd', 
'DNSMASQ_VENDOR_CLASS': 'android-dhcp-8.1.0',
'DNSMASQ_REQUESTED_OPTIONS': '1,3,6,15,26,28,51,58,59,43'

"""
with open("/home/sfw/sfw-core/out.log","a") as file:
    jdata = {}
    if 'add' in sys.argv[1]:
        if 'DNSMASQ_TAGS' in os.environ:
            jdata["DNSMASQ_TAGS"] = os.environ.get('DNSMASQ_TAGS')
        if 'DNSMASQ_CLIENT_ID' in os.environ:
            jdata["DNSMASQ_CLIENT_ID"] = os.environ.get('DNSMASQ_CLIENT_ID')
        if 'DNSMASQ_VENDOR_CLASS' in os.environ:
            jdata["DNSMASQ_VENDOR_CLASS"] = os.environ.get('DNSMASQ_VENDOR_CLASS')
        if 'DNSMASQ_REQUESTED_OPTIONS' in os.environ:
            jdata["DNSMASQ_REQUESTED_OPTIONS"] = os.environ.get('DNSMASQ_REQUESTED_OPTIONS')
    if len(jdata) > 0:
        file.write(json.dumps(jdata))
        file.write("\n")