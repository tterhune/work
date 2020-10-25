#!/usr/bin/env python

import sys
import urllib3

import policies.afc as afc_module
import policies.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(argv):
    if len(argv) < 3:
        print('Usage: {} <AFC host> <fabric-name>'.format(argv[0]))
        sys.exit(1)
    
    afc_host = argv[1]
    fabric_name = argv[2]
    token = afc_module.get_token(afc_host)
    
    fabric_uuid = switch_module.create_fabric(afc_host, token, fabric_name)

    print(f'Fabric {fabric_name}: {fabric_uuid}')

    switch_module.do_discovery(afc_host, token, fabric_uuid)

    switches = switch_module.get_switches(afc_host, token)
    for switch in switches:
        print('Switch: {} {} {} {} {}'.format(
            switch['name'],
            switch['status'],
            switch['ip_address'],
            switch['role'],
            switch['switch_class']))


if __name__ == '__main__':
    main(sys.argv)
