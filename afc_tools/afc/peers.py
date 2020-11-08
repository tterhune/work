import collections
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


class Connection:

    def __init__(self):
        self._local_switch = None
        self._local_port = None
        self._remote_switch = None
        self._remote_port = None

    @property
    def local_switch(self):
        return self._local_switch

    @local_switch.setter
    def local_switch(self, local_switch):
        self._local_switch = local_switch

    @property
    def local_port(self):
        return self._local_port

    @local_port.setter
    def local_port(self, local_port):
        self._local_port = local_port

    @property
    def remote_switch(self):
        return self._remote_switch

    @remote_switch.setter
    def remote_switch(self, remote_switch):
        self._remote_switch = remote_switch

    @property
    def remote_port(self):
        return self._remote_port

    @remote_port.setter
    def remote_port(self, remote_port):
        self._remote_port = remote_port


def _connection_exists(peers: list, local_switch: str, connection: dict) -> bool:
    local_port = connection['local_port_name']
    remote_switch = connection['remote_station_name']
    remote_port = connection['remote_port_name']

    # See if the connection is in the list
    for peer in peers:
        # print(peer)
        if peer['remote_station_name'] == local_switch and peer['remote_port_name'] == local_port:
            return True

    return False


def display(peers: list) -> None:
    total = 0

    peering = collections.defaultdict(list)
    for peer in sorted(peers, key=lambda p: p['local_station_name']):
        peering[peer['local_station_name']].extend(peer['peers'])

    # import pprint
    # print('{}'.format(pprint.pformat(peering, indent=4)))

    for switch, peers in peering.items():
        title = 'AFC Peers For: {}'.format(switch)
        print('\n{}'.format(title))
        print('{}'.format('-' * len(title)))

        print('\n{0: ^20} {1: ^15} {2: ^15}'.format('Remote Switch', 'Remote Port', 'Local Port'))
        print('{0: ^20} {1: ^15} {2: ^15}'.format('-' * 13, '-' * 11, '-' * 10))

        for peer_entry in sorted(peers, key=lambda r: r['remote_station_name']):
            remote_switch = peer_entry['remote_station_name']

            valid = False
            if _connection_exists(peering[remote_switch], switch, peer_entry):
                valid = True

            print('{0: ^20} {1: ^15} {2: ^15} {3: ^10}'.format(
                  remote_switch,
                  peer_entry['remote_port_name'],
                  peer_entry['local_port_name'],
                  'valid' if valid else 'invalid'))

            total += 1

    print('\nTotal AFC Peers: {}'.format(total))
