
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