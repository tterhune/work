import datetime
import requests
from typing import List
import urllib3

import afc_tools.shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_peers(afc_host: str, token: str) -> List[dict]:
    """Get all AFC peers, possibly for a set of switches.

    Args:
        afc_host (str): AFC hostname
        token (str): AFC token

    Returns:
        list(dict): list of peer dicts
    """
    path = 'peers'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    url = defines.vURL.format(host=afc_host, headers=headers, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    return r.json()['result']


def display(peers):
    total = 0

    if peers:
        for peer in peers:
            switch = peer['local_station_name']

            title = 'AFC Peers {}'.format(switch)
            print('\n{}'.format(title))
            print('{}'.format('-' * len(title)))

            print('\n{0: ^20}  {1}  {2: ^20}'.format(
                  'Local Port',
                  'Remote Switch',
                  'Remote Port'
                  ))

            for remote_peer in peer['peers']:
                print('{} {} {}'.format(
                    remote_peer['local_port_name'],
                    remote_peer['remote_station_name'],
                    remote_peer['remote_port_name']))
                total += 1

    print('\nTotal AFC Peers: {}'.format(total))
