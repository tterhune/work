import copy
import requests
import urllib3

import shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_port(host, token, port_uuid):
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

