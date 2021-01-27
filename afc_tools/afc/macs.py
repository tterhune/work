import datetime
import requests
import urllib3

import afc_tools.shared.defines as defines
import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_macs(afc_host, token, switch_uuids=None, interfaces=False):
    """Get all AFC mac attachments, possibly for a set of switches.

    Args:
        afc_host (str): AFC hostname
        token (str): AFC token
        switch_uuids (list): Get MAC attachments for this list of switch UUIDs
        interfaces (bool): Get interface info with the MAC attachment?

    Returns:
        list(dict): list of MAC attachment dicts
    """
    path = 'mac_attachments'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    params = dict()
    if switch_uuids:
        params['switches'] = switch_uuids

    if interfaces:
        params['interfaces'] = True

    url = defines.vURL.format(host=afc_host, headers=headers, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()

    mac_attachments = r.json()['result']
    return mac_attachments


def display(switch, macs):
    if not macs:
        print('No AFC MAC attachments found for switch {}'.format(switch['name']))
        return

    header = ['MAC Address', 'VLAN', 'Interface', 'Type', 'Last\nModified', 'Switch']
    table = []
    for mac in macs:
        last_mod = datetime.datetime.fromtimestamp(mac['last_modified']).strftime(
                '%m-%d-%Y %H:%M:%S')
        row = [mac['mac_address'],
               mac['vlan'],
               mac['interface_object']['name'],
               mac['interface_type'],
               last_mod,
               switch['name']]
        table.append(row)
    print(tabulate.tabulate(table, header, tablefmt='grid'))

