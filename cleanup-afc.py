#!/usr/bin/env python

import sys
import urllib3

import policies.afc as afc_module
import policies.policy as policies_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(argv):
    if len(argv) < 2:
        print('Usage: {} <AFC host>'.format(argv[0]))
        sys.exit(1)
    
    afc_host = argv[1]
    token = afc_module.get_token(afc_host)
    
    policies_module.cleanup_policies(afc_host, token)
    policies_module.cleanup_qualifiers(afc_host, token)


if __name__ == '__main__':
    main(sys.argv)
