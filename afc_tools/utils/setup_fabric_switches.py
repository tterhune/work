#!/usr/bin/env python

import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host, fabric_name, switch_prefix):
    """Create fabric, discover switches and assign to fabric.

    Args:
        afc_host (str): AFC host to talk to
        fabric_name (str): name of our new fabric
        switch_prefix (str): name of the set of switches

    Returns:
        None
    """
    token = afc_module.get_token(afc_host)

    fabrics = switch_module.get_fabrics(afc_host, token)
    switches = switch_module.get_switches(afc_host, token)
    if switches:
        print('Found some switches, cleaning up')
        for switch in switches:
            print('Deleting switch: {}'.format(switch['name']))
            switch_module.delete_switch(afc_host, token, switch['uuid'])

    if fabrics:
        print('Found some fabrics, cleaning up')
        for fabric in fabrics:
            print('Deleting fabric: {}'.format(fabric['name']))
            switch_module.delete_fabric(afc_host, token, fabric['uuid'])

    fabric = switch_module.create_fabric(afc_host, token, fabric_name)

    print('Fabric {}: {}'.format(fabric['uuid'], fabric['name']))

    switch_module.do_discovery(afc_host, token, fabric['uuid'], switch_prefix, all_at_once=True)

    switches = switch_module.get_switches(afc_host, token)
    for switch in switches:
        print('Switch: {} {} {} {} {}'.format(
            switch['name'],
            switch['status'],
            switch['ip_address'],
            switch['role'],
            switch['switch_class']))
