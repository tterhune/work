import copy
import requests
import urllib3

import afc_magic.shared.defines as defines
import afc_magic.afc.switches as switches_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_port_str(afc_host, token, ports):
    port_str = str()
    for p in ports:
        s = switches_module.get_switch(afc_host, token, p['switch_uuid'])
        port_str += '\t\t{}: {} {}\n'.format(s['name'], p['name'], p['uuid'])

    return port_str


def get_port(host, token, port_uuid):
    """Get AFC port based on port UUID.

    Args:
        host (str): AFC hostname
        token (str): AFC token
        port_uuid (str): UUID of port

    Returns:
        dict: The port
    """
    path = 'ports/{}'.format(port_uuid)
    params = dict()

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()

    port = r.json()['result']
    return port


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


def patch_port_policies(host, token, port, policies, op):
    path = 'ports'

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    policy_uuids = [p['uuid'] for p in policies]
    data = [
        {
            'uuids': [port['uuid']],
            'patch': [
                {
                    'path': '/qos_ingress_policies',
                    'value': policy_uuids,
                    'op': op
                }
            ]
        }
    ]

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.patch(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    print('Succeeded ({}) Patch Operation: {} for Policies: {} on Port: {}'.format(
        r.status_code,
        op,
        ', '.join([p['name'] for p in policies]),
        port['name']))


def apply_policies_to_port(host, token, port, policies):
    path = 'ports/{}'.format(port['uuid'])

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    data = copy.deepcopy(port)
    data['qos_ingress_policies'] = [p['uuid'] for p in policies]

    data['speed'].pop('configure')
    data.pop('pause')
    data.pop('ecn')
    data.pop('enable_lossless')

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.put(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    print('Succeeded ({}) when applying policies {} to port = {}'.format(
        r.status_code,
        ', '.join([p['name'] for p in policies]),
        port['name']))


def delete_policies_from_port(host, token, port):
    if not port:
        return False

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
