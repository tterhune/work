import requests
import time
import urllib3

import afc_tools.shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_fabrics(host, token):
    path = 'fabrics'
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    fabrics = r.json()['result']
    return fabrics


def get_switch(host, token, switch_uuid):
    path = 'switches/{}'.format(switch_uuid)
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    switch = r.json()['result']
    return switch


def get_switches(host, token):
    path = 'switches'
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    } 

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    switches = r.json()['result']
    return switches


def create_fabric(host, token, fabric_name):
    print(f'Creating fabric: {fabric_name}')

    path = 'fabrics'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    data = {
        'name': fabric_name,
        'description': 'Fabric created by Tim script',
        'password': 'plexxi',

    }

    params = dict(fabric_class='Leaf-Spine')

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.post(url, headers=headers, json=data, params=params, verify=False)
    r.raise_for_status()
    return r.json()['result']


def assign_switch_to_fabric(host, token, fabric_uuid, switch_uuid, role):
    #  PATCH /api/v1/switches
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    path = 'switches'
    data = [
        {
            'uuids': [switch_uuid],
            'patch': [
                {
                    'path': '/fabric_uuid',
                    'value': fabric_uuid,
                    'op': 'replace'
                }
            ]
        },
        {
            'uuids': [switch_uuid],
            'patch': [
                {
                    'path': '/role',
                    'value': role,
                    'op': 'replace'
                }
            ]
        }
    ]

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.patch(url, headers=headers, json=data, verify=False)
    r.raise_for_status()
    return r.json()['result']


def discover_switch(host: str, token: str, hostname: str, afc_pwd: str, admin_pwd: str) -> list:
    """Make API call to discover a switch.

    Args:
        host (str): AFC host
        token (str): API token
        hostname (str): new switch FQDN
        afc_pwd (str): password for afc_admin on switch
        admin_pwd (str): admin switch password

    Returns:
        list
    """
    # POST /api/v1/switches/discover
    # data: {"switches": ["six-sw-01.lab.plexxi.com"], "afc_admin_passwd": "plexxi",
    #        "admin_passwd": "plexxi"}
    print('Trying to discover switch: {}'.format(hostname))

    path = 'switches/discover'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    data = {
        'switches': [hostname],
        'afc_admin_passwd': afc_pwd,
        'admin_passwd': admin_pwd
    }

    url = defines.vURL.format(host=host, path=path, data=data, version='v1')
    r = requests.post(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    result = r.json()['result']
    print('Discover response = {}'.format(result))

    return result


def do_discovery(afc_host, token, fabric_uuid):
    afc_pwd = 'plexxi'
    admin_pwd = 'plexxi'
    switches = [
        {
            'name': 'six-sw-01.lab.plexxi.com',
            'role': defines.SWITCH_ROLE_LEAF
        },
        {
            'name': 'six-sw-02.lab.plexxi.com',
            'role': defines.SWITCH_ROLE_LEAF
        },
        {
            'name': 'six-sw-03.lab.plexxi.com',
            'role': defines.SWITCH_ROLE_SPINE

        },
        {
            'name': 'six-sw-04.lab.plexxi.com',
            'role': defines.SWITCH_ROLE_SPINE
        },
        {
            'name': 'six-sw-05.lab.plexxi.com',
            'role': defines.SWITCH_ROLE_BORDER_LEAF
        },
        {
            'name': 'six-sw-06.lab.plexxi.com',
            'role': defines.SWITCH_ROLE_BORDER_LEAF
        }
    ]

    for switch in switches:
        r = discover_switch(afc_host, token, switch['name'], afc_pwd, admin_pwd)[0]
        time.sleep(1)
        assign_switch_to_fabric(afc_host, token, fabric_uuid, r['switch_uuid'], switch['role'])


def display(fabrics, switches):
    print('\nFabrics:')
    for fabric in fabrics:
        print('\tName: {} UUID: {}'.format(fabric['name'], fabric['uuid']))

    if not fabrics:
        print('\t... no fabrics defined')

    print('\n')
    print('{0: <10} {1: <10} {2: <15} {3: <15} {4: <15}'.format('Name',
                                                                'Status',
                                                                'IP Address',
                                                                'Role',
                                                                'Class'))

    print('{0: <10} {1: <10} {2: <15} {3: <15} {4: <15}'.format('-'*10, '-'*10, '-'*15, '-'*15,
                                                                '-'*15))

    for switch in sorted(switches, key=lambda s: s['name']):
        print('{0: <10} {1: <10} {2: <15} {3: <15} {4: <15}'.format(
            switch['name'],
            switch['status'],
            switch['ip_address'],
            switch['role'],
            switch['switch_class']))

    if not switches:
        print('\t... no switches defined')
