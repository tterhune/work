import datetime
import requests
from typing import List
import urllib3

import afc_tools.shared.defines as defines
import afc_tools.afc.ports as ports_module
import afc_tools.afc.switches as switches_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_neighbors(afc_host: str, token: str, switch_uuids=None, neighbor_type=None) -> List[dict]:
    """Get all AFC neighbors, possibly for a set of switches.

    Args:
        afc_host (str): AFC hostname
        token (str): AFC token
        switch_uuids (list): Get neighbors for this list of switch UUIDs
        neighbor_type (str): optional neighbor type

    Returns:
        list(dict): list of neighbor dicts
    """
    path = 'neighbor_discovery/neighbors'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    params = dict()
    params['include_stale'] = True

    if switch_uuids:
        params['switches'] = switch_uuids

    if type:
        params['type'] = neighbor_type

    url = defines.vURL.format(host=afc_host, headers=headers, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()

    neighbors = r.json()['result']
    return neighbors


def display(afc_host, token, neighbors):
    total = 0
    print('AFC Neighbors')
    print('-------------\n')
    if neighbors:
        for neighbor in neighbors:
            print('Type              : {}'.format(neighbor['neighbor_type'].upper()))
            print('Chassis ID        : {}'.format(neighbor['chassis_id']))
            print('Port ID           : {}'.format(neighbor['port_id']))
            print('Station MAC       : {}'.format(neighbor['station_mac_address']))
            print('System Name       : {}'.format(neighbor['system_name']))
            print('System Description: {}'.format(neighbor['system_description']))
            print('Management Address: {}'.format(neighbor.get('mgmt_address', 'None')))
            print('Management IF Num : {}'.format(neighbor.get('mgmt_address_ifnum', 'None')))
            print('Port Description  : {}'.format(neighbor['port_description']))
            print('Port VLAN ID      : {}'.format(neighbor['port_vlanid']))
            print('LAG ID            : {}'.format(neighbor['lag_id']))
            print('Stale             : {}'.format(neighbor['stale']))

            switch = switches_module.get_switch(afc_host, token, neighbor['switch_uuid'])
            port = ports_module.get_port(afc_host, token, neighbor['port_uuid'])
            print('Learned on Switch : {}'.format(switch['name']))
            print('Learned on Intf   : {} ({})'.format(port['name'], port['port_label']))
            print('Last Modified     : {}'.format(neighbor['last_modified']))
            print('\n')
            total += 1

    print('Total AFC Neighbors: {}\n'.format(total))
