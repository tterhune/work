import collections
import pprint
import requests
import time
import urllib3

import afc_tools.shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_fabrics(host, token):
    """Get all of the configured fabrics.

    Arguments:
        host (str): AFC hostname
        token (str): AFC token to use

    Returns:
        list[dict]: list of fabric dicts
    """
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


def delete_fabric(host, token, fabric_uuid):
    path = 'fabrics/{}'.format(fabric_uuid)
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.delete(url, headers=headers, verify=False)
    r.raise_for_status()


def delete_switch(host, token, switch_uuid):
    path = 'switches/{}'.format(switch_uuid)
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.delete(url, headers=headers, verify=False)
    r.raise_for_status()


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
    print('Creating fabric: {}'.format(fabric_name))

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


def assign_switches_to_fabric(host, token, fabric_uuid, switches_and_roles):
    """Assign some switches to a fabric.

    Args:
        host (str): AFC hostname
        token (str): AFC token
        fabric_uuid (str): Fabric UUID to assign switches
        switches_and_roles (dict): key: role, value: list switch uuids

    Returns:
    """
    #  PATCH /api/v1/switches
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    path = 'switches'

    all_switch_uuids = []
    role_patches = []
    for role, switch_uuids in switches_and_roles.items():
        all_switch_uuids.extend(switch_uuids)
        role_patches.append(
            {
                'uuids': switch_uuids,
                'patch': [
                    {
                        'path': '/role',
                        'value': role,
                        'op': 'replace'
                    }
                ]
            }
        )

    fabric_patch = {
        'uuids': all_switch_uuids,
        'patch': [
            {
                'path': '/fabric_uuid',
                'value': fabric_uuid,
                'op': 'replace'
            }
        ]
    }
    data = [fabric_patch]
    data.extend(role_patches)

    print('Assign to switches to fabric patch = {}'.format(pprint.pformat(data)))

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.patch(url, headers=headers, json=data, verify=False)
    r.raise_for_status()
    return r.json()['result']


def discover_switches(host, token, hostnames, afc_pwd, admin_pwd):
    """Make API call to discover a switch.

    Args:
        host (str): AFC host
        token (str): API token
        hostnames (list): switch FQDNs
        afc_pwd (str): password for afc_admin on switch
        admin_pwd (str): admin switch password

    Returns:
        list
    """
    # POST /api/v1/switches/discover
    # data: {"switches": ["six-sw-01.lab.plexxi.com"], "afc_admin_passwd": "plexxi",
    #        "admin_passwd": "plexxi"}
    print('Trying to discover switches: {}'.format(',\n'.join(hostnames)))

    path = 'switches/discover'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    data = {
        'switches': hostnames,
        'afc_admin_passwd': afc_pwd,
        'admin_passwd': admin_pwd
    }

    url = defines.vURL.format(host=host, path=path, data=data, version='v1')
    r = requests.post(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    result = r.json()['result']
    print('Discover response = {}'.format(result))

    return result


def discover_switch(host, token, hostname, afc_pwd, admin_pwd):
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


def do_discovery(afc_host, token, fabric_uuid, switch_prefix, all_at_once=False):
    start = time.time()
    afc_pwd = 'aruba'
    admin_pwd = 'plexxi'
    switches = [
        {
            'name': '{switch_prefix}-sw-01.lab.plexxi.com'.format(switch_prefix=switch_prefix),
            'role': defines.SWITCH_ROLE_LEAF
        },
        {
            'name': '{switch_prefix}-sw-02.lab.plexxi.com'.format(switch_prefix=switch_prefix),
            'role': defines.SWITCH_ROLE_LEAF
        },
        {
            'name': '{switch_prefix}-sw-03.lab.plexxi.com'.format(switch_prefix=switch_prefix),
            'role': defines.SWITCH_ROLE_SPINE

        },
        {
            'name': '{switch_prefix}-sw-04.lab.plexxi.com'.format(switch_prefix=switch_prefix),
            'role': defines.SWITCH_ROLE_SPINE
        },
        {
            'name': '{switch_prefix}-sw-05.lab.plexxi.com'.format(switch_prefix=switch_prefix),
            'role': defines.SWITCH_ROLE_BORDER_LEAF
        },
        {
            'name': '{switch_prefix}-sw-06.lab.plexxi.com'.format(switch_prefix=switch_prefix),
            'role': defines.SWITCH_ROLE_BORDER_LEAF
        }
    ]

    hostnames = [s['name'] for s in switches]
    roles_and_switches = collections.defaultdict(list)

    if all_at_once:
        result = discover_switches(afc_host, token, hostnames, afc_pwd, admin_pwd)
        for r in result:
            for s in switches:
                if s['name'].startswith(r['hostname_str']):
                    roles_and_switches[s['role']].append(r['switch_uuid'])

        r = assign_switches_to_fabric(afc_host, token, fabric_uuid, roles_and_switches)
        print('Assign to fabric: {}', r)
    else:
        for switch in switches:
            r = discover_switch(afc_host, token, switch['name'], afc_pwd, admin_pwd)[0]
            d = {
                switch['role']: [r['switch_uuid']]
            }
            assign_switches_to_fabric(afc_host, token, fabric_uuid, d)

    print('It took {} seconds to discover {} switches'.format(time.time() - start, len(switches)))


def display(afc_host, fabrics, switches):
    print('\nFabrics:')
    for fabric in fabrics:
        print('\tName: {} UUID: {}'.format(fabric['name'], fabric['uuid']))

    if not fabrics:
        print('\t... no fabrics defined')

    max_name_len = 0
    for switch in sorted(switches, key=lambda s: s['name']):
        max_name_len = max(max_name_len, len(switch['name']))

    print('\n')
    print('{0: <{1}} {2: <15} {3: <15} {4: <15} {5: <15}'.format('Name',
                                                                 max_name_len,
                                                                 'Status',
                                                                 'IP Address',
                                                                 'Role',
                                                                 'Class'))

    print('{0: <{1}} {2: <15} {3: <15} {4: <15} {5: <15}'.format('-' * max_name_len,
                                                                 max_name_len,
                                                                 '-' * 15,
                                                                 '-' * 15,
                                                                 '-' * 15,
                                                                 '-' * 15))

    for switch in sorted(switches, key=lambda s: s['name']):
        print('{0: <{1}} {2: <15} {3: <15} {4: <15} {5: <15} {6}'.format(
            switch['name'],
            str(max_name_len),
            switch['status'],
            switch['ip_address'],
            switch['role'],
            switch['switch_class'],
            switch['uuid']))

    if not switches:
        print('\t... no switches defined')
