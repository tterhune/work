#!/usr/bin/env python

import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    """Create fabric, discover switches and assign to fabric.

    Args:
        afc_host (str): AFC host to talk to

    Returns:
        None
    """
    token = afc_module.get_token(afc_host)

    fabrics = switch_module.get_fabrics(afc_host, token)
    switches = switch_module.get_switches(afc_host, token)

    for fabric in fabrics:
        print('Fabric: {}'.format(fabric['name']))

    for switch in switches:
        print('Switch: {} {} {} {} {}'.format(
            switch['name'],
            switch['status'],
            switch['ip_address'],
            switch['role'],
            switch['switch_class']))

    for switch in switches:
        print('Deleting Switch: {}'.format(switch['name']))
        switch_module.delete_switch(afc_host, token, switch['uuid'])

    for fabric in fabrics:
        print('Deleting Fabric : {}'.format(fabric['name']))
        switch_module.delete_fabric(afc_host, token, fabric['uuid'])


