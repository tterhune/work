import requests
import tabulate
import urllib3

import afc_tools.shared.defines as defines
import afc_tools.afc.ports as ports_module
import afc_tools.afc.switches as switches_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_neighbors(afc_host, token, switch_uuids=None, neighbor_type=None):
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
    params['stale'] = True

    if switch_uuids:
        params['switches'] = switch_uuids

    if type:
        params['type'] = neighbor_type

    url = defines.vURL.format(host=afc_host, headers=headers, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()

    neighbors = r.json()['result']
    return neighbors


def display_full(neighbor, switch, port):
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
    print('Learned on Switch : {}'.format(switch['name']))
    print('Learned on Intf   : {} ({})'.format(port['name'], port['port_label']))
    print('Last Modified     : {}'.format(neighbor['last_modified']))


def display(afc_host, token, neighbors, verbose=False):
    if verbose:
        total = 0
        print('AFC Neighbors')
        print('-------------\n')
        for neighbor in neighbors:
            switch = switches_module.get_switch(afc_host, token, neighbor['switch_uuid'])
            port = ports_module.get_port(afc_host, token, neighbor['port_uuid'])
            display_full(neighbor, switch, port)
            print('\n')
            total += 1
        print('Total AFC Neighbors: {}\n'.format(total))

    header = ['Type', 'Learned\nOn', 'Stale', 'Chassis\nID', 'Port\nID', 'System\nName']
    table = []
    peer_table = []
    for neighbor in neighbors:
        switch = switches_module.get_switch(afc_host, token, neighbor['switch_uuid'])
        port = ports_module.get_port(afc_host, token, neighbor['port_uuid'])

        learned_on = '{}\n{}'.format(switch['name'], port['name'])

        row = [neighbor['neighbor_type'].upper(),
               learned_on,
               neighbor['stale'],
               neighbor['chassis_id'],
               neighbor['port_id'],
               #neighbor['station_mac_address']
               neighbor['system_name']]
               # neighbor['system_description']
               # neighbor.get('mgmt_address', 'None')
               # neighbor.get('mgmt_address_ifnum', 'None')
               # neighbor['port_description']
               # neighbor['port_vlanid']
               # neighbor['lag_id']
               # neighbor['stale'])
        if 'Aruba' in neighbor['system_description']:
            peer_table.append(row)
        else:
            table.append(row)

    print(tabulate.tabulate(peer_table, header, tablefmt='grid'))
    print(tabulate.tabulate(table, header, tablefmt='grid'))

