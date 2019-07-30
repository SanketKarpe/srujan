#!/usr/bin/python3
import os
from spam_lists.clients import SPAMHAUS_ZEN, SPAMHAUS_DBL, HpHosts

blacklist_path = 'Banlist'


def ti_lookup(dns):
    """

    Args:
        dns ():

    Returns:

    """
    result = []
    try:
        hpHost = HpHosts('spam-lists-test-suite')
        if hpHost.lookup(dns) is not None:
            result.append('HpHost')
        if SPAMHAUS_DBL.lookup(dns) is not None:
            result.append('SPAMHAUS')
        if SPAMHAUS_ZEN.lookup(dns) is not None:
            result.append('SPAMHAUS_ZEN')

        for root, dirs, files in os.walk(blacklist_path):
            for filename in files:
                with open(os.path.join(root, filename)) as fp:
                    blacklist_hosts = fp.readlines()
                    for host in blacklist_hosts:
                        if dns == host.rstrip():
                            result.append(filename.strip('.txt'))

        # Return list of tags where dns is found
        print(result)
    except:
        pass
    return result


if __name__ == '__main__':
    ti_lookup('007freepics.com')
