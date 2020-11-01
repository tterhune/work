import datetime
import requests
from typing import List
import urllib3

import shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_macs(afc_host: str, token: str, switch_uuids=None, interfaces=False) -> List[dict]:
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


def display(macs):
    total = 0
    if macs:
        print('\n{0: ^20}  {1}  {2: ^10}  {3: ^7} {4: ^18}'.format(
            'AFC MAC Address',
            'VLAN',
            'Interface',
            'Type',
            'Last Modified'))

        print('{}  {}  {}  {}  {}'.format('-' * 20, '-' * 4, '-' * 10, '-' * 7, '-' * 18))

        for mac in macs:
            last_mod = datetime.datetime.fromtimestamp(mac['last_modified']).strftime(
                '%m-%d-%Y %H:%M:%S')
            total += 1
            print('{0: ^20}  {1: ^4}  {2: ^10}  {3: ^7}  {4}'.format(
                mac['mac_address'],
                mac['vlan'],
                mac['interface_object']['name'],
                mac['interface_type'],
                last_mod))

    print(f'\nTotal AFC MAC Addresses: {total}')
