#!/usr/bin/env python

import sys
import urllib3

import afc.afc_utils as afc_module
import afc.switches as switches_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    fabrics = switches_module.get_fabrics(afc_host, token)
    switches = switches_module.get_switches(afc_host, token)
    switches_module.display(fabrics, switches)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
