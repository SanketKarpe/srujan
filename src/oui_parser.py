#!/usr/bin/python3
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from urllib.request import urlopen, Request
import re


def ParseIEEEOui(url="http://standards.ieee.org/develop/regauth/oui/oui.txt"):
    """Parses the IEEE OUI text file to extract MAC address and company mappings.

    Args:
        url (str, optional): The URL of the IEEE OUI text file. 
            Defaults to "http://standards.ieee.org/develop/regauth/oui/oui.txt".

    Returns:
        list: A list of dictionaries, where each dictionary contains 'mac' and 'company'.
    """
    req = Request(url)
    res = urlopen(req)
    data = res.read()
    IEEOUI = []
    for line in data.split('\n'):
        try:
            mac, company = re.search(r'([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+\(hex\)\s+(.+)', line).groups()
            IEEOUI.append(dict(mac=mac, company=company))
        except AttributeError:
            continue

    return IEEOUI
