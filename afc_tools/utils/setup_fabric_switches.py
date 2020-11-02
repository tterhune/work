#!/usr/bin/env python

import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host: str, fabric_name: str) -> None:
    """Create fabric, discover switches and assign to fabric.

    Args:
        afc_host (str): AFC host to talk to
        fabric_name (str): name of our new fabric

    Returns:
        None
    """
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
