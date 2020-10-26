#!/usr/bin/env python

import sys
import urllib3

import policies.afc as afc_module
import policies.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host, fabric_name):
    token = afc_module.get_token(afc_host)
    
    fabric = switch_module.create_fabric(afc_host, token, fabric_name)

    print('Fabric {}: {}'.format(fabric['uuid'], fabric['name']))

    switch_module.do_discovery(afc_host, token, fabric['uuid'])

    switches = switch_module.get_switches(afc_host, token)
    for switch in switches:
        print('Switch: {} {} {} {} {}'.format(
            switch['name'],
            switch['status'],
            switch['ip_address'],
            switch['role'],
            switch['switch_class']))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: {} [<AFC host>] <fabric name>'.format(sys.argv[0]))
        sys.exit(1)
    elif len(sys.argv) < 3:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
        my_fabric_name = sys.argv[2]
    else:
        my_afc_host = sys.argv[1]
        my_fabric_name = sys.argv[2]

    main(my_afc_host, my_fabric_name)
