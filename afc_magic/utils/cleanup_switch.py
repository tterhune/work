#!/usr/bin/env python

import sys
import urllib3

import afc_magic.afc.afc_utils as afc_module
import afc_magic.aruba.aruba_utils as aruba_module
import afc_magic.afc.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def cleanup_switch(switch):
    cookie_jar = aruba_module.switch_login(switch)
    aruba_module.switch_logout(switch, cookie_jar)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    
    switches = switch_module.get_switches(afc_host, token)
    for switch in switches:
        cleanup_switch(switch)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
