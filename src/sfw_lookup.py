#!/usr/bin/python3
"""Threat Intelligence lookup module for Srujan.

This module provides functionality to check domains against local blacklists.
External threat intelligence sources (Spamhaus, HpHosts) have been removed
as the 'spam_lists' library is no longer maintained.
"""
import os

blacklist_path = 'Banlist'


def ti_lookup(dns):
    """Checks a domain against local blacklists.

    Args:
        dns (str): The domain name to check.

    Returns:
        list: A list of local blacklist files where the domain was found.
    """
    result = []
    try:
        # External lookups removed due to deprecated libraries
        
        for root, dirs, files in os.walk(blacklist_path):
            for filename in files:
                with open(os.path.join(root, filename)) as fp:
                    blacklist_hosts = fp.readlines()
                    for host in blacklist_hosts:
                        if dns == host.rstrip():
                            result.append(filename.strip('.txt'))

        # Return list of tags where dns is found
        if result:
            print(result)
    except Exception as e:
        print(f"Error in ti_lookup: {e}")
    return result


if __name__ == '__main__':
    ti_lookup('007freepics.com')
