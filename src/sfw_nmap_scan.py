#!/usr/bin/python3
"""Nmap scanning module for Srujan.

This module handles running Nmap scans on devices, parsing the results,
and sending the data to Elasticsearch.
"""
import json
import sys
from datetime import datetime
from lib.utils import send2es
from lib.config import *
from libnmap.parser import NmapParserException, NmapParser
from libnmap.process import NmapProcess
from libnmap.reportjson import ReportEncoder
import time

# start a new nmap scan on localhost with some specific options
def do_scan(targets, options):
    """Executes an Nmap scan.

    Args:
        targets (str): The target IP address(es) or range.
        options (str): Nmap command-line options.

    Returns:
        NmapReport: The parsed Nmap report, or None if parsing fails.
    """
    parsed = None
    nmproc = NmapProcess(targets, options)
    rc = nmproc.run()
    if rc != 0:
        print("nmap scan failed: {0}".format(nmproc.stderr))
    print(type(nmproc.stdout))

    try:
        parsed = NmapParser.parse(nmproc.stdout)
    except NmapParserException as e:
        print("Exception raised while parsing scan: {0}".format(e.msg))

    return parsed


# print scan results from a nmap report
def process_report(nmap_report):
    """Processes an Nmap report and sends results to Elasticsearch.

    Args:
        nmap_report (NmapReport): The Nmap report object to process.
    """
    for host in nmap_report.hosts:
        if len(host.hostnames):
            tmp_host = host.hostnames.pop()
        else:
            tmp_host = host.address

        for serv in host.services:
            jdata = {}
            jdata["ip_address"] = host.address
            jdata["hostname"] = tmp_host
            if len(serv.banner):
                jdata["service_port"] =str(serv.port)
                jdata["service_protocol"] = serv.protocol
                jdata["service_state"] = serv.state
                jdata["service_name"] = serv.service

                banner_product = None
                banner_devicetype = None
                if "devicetype:" in serv.banner:
                    banner_devicetype = serv.banner.split("devicetype:")[-1]
                if "product:" in serv.banner:
                    banner_product = serv.banner.split("product:")[-1].split("devicetype:")[0]
                if banner_product:
                    jdata["service_banner"] = banner_product
                if banner_devicetype:
                    jdata["service_banner_devicetype"] = banner_devicetype
            else:
                jdata["service_port"] =str(serv.port)
                jdata["service_protocol"] = serv.protocol
                jdata["service_state"] = serv.state
                jdata["service_name"] = serv.service

            if host.os_fingerprinted:
                cpelist = host.os.os_cpelist()
                if len(cpelist):
                    mcpe = cpelist.pop()
                    jdata['vendor'] = mcpe.get_vendor()
                    jdata['product'] = mcpe.get_product()
                    jdata['os_name'] = host.os.osmatches[0].name

            ret = send2es(jdata,index_name=NMAP_SCAN_INDEX)
            if ret:
                print("ES Success\n")
            else:
                print("ES Fail\n")
            print(jdata)
            time.sleep(5)
    print(nmap_report.summary)


# print scan results from a nmap report
"""
def print_scan(nmap_report):
    for host in nmap_report.hosts:
        if len(host.hostnames):
            tmp_host = host.hostnames.pop()
        else:
            tmp_host = host.address

        print("Nmap scan report for {0} ({1})".format(
            tmp_host,
            host.address))
        print("Host is {0}.".format(host.status))
        print("  PORT     STATE         SERVICE")

        for serv in host.services:
            pserv = "{0:>5s}/{1:3s}  {2:12s}  {3}".format(
                    str(serv.port),
                    serv.protocol,
                    serv.state,
                    serv.service)
            if len(serv.banner):
                pserv += " ({0})".format(serv.banner)
            print(pserv)
        if host.os_fingerprinted:
            print("OS Fingerprint:")
            msg = ''

            for osm in host.os.osmatches:
                print("Found Match:{0} ({1}%)".format(osm.name, osm.accuracy))
                for osc in osm.osclasses:
                    print("\tOS Class: {0}".format(osc.description))
                    for cpe in osc.cpelist:
                        print("\tCPE: {0}".format(cpe.cpestring))
        else:
            print("No fingerprint available")

    print(nmap_report.summary)

    # print(json.dumps(nmap_report, cls=ReportEncoder))

"""


def nmap_scan_ip(ip):
    """Initiates an Nmap scan for a specific IP address.

    Waits for 20 seconds before scanning to allow the device to settle.
    Scans with options: -Pn -O -sV --max-os-tries=1 --osscan-guess -T4.

    Args:
        ip (str): The IP address to scan.
    """
    time.sleep(20)
    try:
        report = do_scan(ip, "-Pn -O -sV --max-os-tries=1 --osscan-guess -T4")
        if report:
            # create a json object from an NmapReport instance
            process_report(report)
    except:
        pass

