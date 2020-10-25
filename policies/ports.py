import copy
import requests
import urllib3

import shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_ports(host, token, switches=None):
    params = dict()
    if switches:
        params['switches'] = switches

    print('Getting ports for {}'.format(switches))

    path = 'ports'
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    } 

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()

    ports = r.json()['result']
    return ports


def apply_policies_to_port(host, token, port, policies):
    path = 'ports/{}'.format(port['uuid'])

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    data = copy.deepcopy(port)
    data['qos_ingress_policies'] = [p['uuid'] for p in policies]

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.put(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    print('Succeeded ({}) when applying policies {} to port = {}'.format(
        r.status_code,
        ', '.join([p['name'] for p in policies]),
        port['name']))


def delete_policies_from_port(host, token, port):
    path = 'ports/{}'.format(port['uuid'])

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    data = copy.deepcopy(port)
    data['qos_ingress_policies'] = []

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.put(url, headers=headers, json=data, verify=False)
    r.raise_for_status()
    print('Succeeded ({}) deleting ALL policies from port = {}'.format(r.status_code, port['name']))
