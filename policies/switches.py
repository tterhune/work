import requests
import time
import urllib3

import shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
        'description': '',
    }

    params = dict(type='Leaf-Spine')

    url = defines.vURL.format(host=host, path=path, params=params, data=data, version='v1')
    r = requests.post(url, headers=headers, json=data, verify=False)
    r.raise_for_status()


def assign_switch_to_fabric(host, token, fabric_uuid, switch_uuid, role):
    #  PATCH /api/v1/switches
    #  data: [{
    #   "uuids": ["dc4d5df9-2836-40bd-a070-7b0c5a38bdcb", "e1cfcd67-96a3-47ae-af99-bfd3d198fda6"],
    #   "patch":[
    #       {
    #           "path": "/fabric_uuid",
    #           "value":"a5f40462-f6ce-44be-98f0-43ab44257564",
    #           "op":"replace"
    #        }
    #    ]
    #  },
    #  {
    #       "uuids":["dc4d5df9-2836-40bd-a070-7b0c5a38bdcb"],
    #       "patch":[
    #           {
    #               "path":"/role",
    #               "value":"leaf",
    #               "op":"replace"
    #            }
    #        ]
    #  },
    #  {
    #       "uuids":["e1cfcd67-96a3-47ae-af99-bfd3d198fda6"],
    #       "patch":[
    #           {
    #               "path":"/role",
    #               "value":"leaf",
    #               "op":"replace"
    #           }
    #       ]
    #   }
    # ]
    pass


def discover_switch(host, token, hostname, afc_pwd, admin_pwd):
    # POST /api/v1/switches/discover
    # data: {"switches": ["six-sw-01.lab.plexxi.com"], "afc_admin_passwd": "plexxi",
    #        "admin_passwd": "plexxi"}
    print(f'Trying to discover switch: {hostname}')

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


def do_discover(afc_host, token, fabric_uuid):
    afc_pwd = 'plexxi'
    admin_pwd = 'plexxi'
    switch_names = [
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

    for switch_name, role in switch_names.items():
        r = discover_switch(afc_host, token, switch_name, afc_pwd, admin_pwd)
        time.sleep(1)
        assign_switch_to_fabric(afc_host, token, fabric_uuid, r['switch_uuid'], role)

