#!/usr/bin/env python

import sys
import urllib3

import policies.afc as afc_module
import policies.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(argv):
    if len(argv) < 2:
        print('Usage: {} <AFC host>'.format(argv[0]))
        sys.exit(1)
    
    afc_host = argv[1]
    token = afc_module.get_token(afc_host)
    switches = switch_module.get_switches(afc_host, token)
    switch_module.display(switches)


if __name__ == '__main__':
    main(sys.argv)
