import copy
import pprint
import requests
import urllib3

import afc_tools.shared.defines as defines
import afc_tools.afc.afc_utils as utils
import afc_tools.afc.ports as ports_module
import afc_tools.afc.switches as switches_module
import tabulate


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get_port(afc_host, token, switch):
    ports = ports_module.get_ports(afc_host, token, switches=[switch['uuid']])
    port = None
    for port in ports:
        if port['type'] == 'access' and port['admin_state'] == 'disabled':
            print('Port = {}'.format(pprint.pformat(port, indent=4)))
            break

    return port


def _port_properties(port_uuids, mlag):
    lacp = {
        'mode': 'off',
        'priority': 1,
        'interval': 'fast',
    }

    speed = {
        'current': 25000
    }

    port_properties_list = []
    if mlag:
        for port_uuid in port_uuids:
            port_properties_list.append({
                'lacp': lacp,
                'speed': speed,
                'port_uuids': [port_uuid]
            })
    else:
        port_properties_list.append({
            'lacp': lacp,
            'speed': speed,
            'port_uuids': port_uuids
        })

    return port_properties_list


def create_mlag(afc_host, token, switches, used_port_uuids=None):
    """Create an MLAG across two switches.

    Args:
        afc_host (str): AFC hostname
        token (str): AFC token
        switches (list): list of AFC switch objects
        used_port_uuids (list[str]): UUIDs of ports already used in other LAGs

    Returns:
        tuple (dict, list[tuple]): AFC LAG dict, and tuple of port, switch
    """
    used_port_uuids = [] if used_port_uuids is None else used_port_uuids

    leaf_switches = list()
    for switch in switches:
        if switch['role'] == defines.SWITCH_ROLE_LEAF and switch['status'] == 'SYNCED':
            leaf_switches.append(switch)

    if len(leaf_switches) < 2:
        print('Need two leaf switches that are in sync, only found: {}'.format(leaf_switches))
        return

    # Pick two ports on two different switches
    lag_ports = []
    for switch in leaf_switches:
        port = _get_port(afc_host, token, switch)
        if port['uuid'] not in used_port_uuids:
            lag_ports.append((port, switch))

    for lag_port in lag_ports:
        print('Using port: {} on switch: {}'.format(lag_port[0]['name'], lag_port[1]['name']))

    # Create MLAG
    port_uuids = [lp[0]['uuid'] for lp in lag_ports]
    mlag_uuid = create_lag(afc_host, token, port_uuids)

    mlag = get_lag(afc_host, token, mlag_uuid)
    return mlag, lag_ports


def create_lag(afc_host, token, port_uuids, mlag=True):
    """Create a (m)LAG on one (or more) ports.

    Args:
        afc_host (str): AFC hostname
        token (str): AFC token
        port_uuids (list): one or more AFC port UUIDs

    Returns:
        str: UUID of the (m)LAG
    """
    path = 'lags'

    data = dict(name=utils.generate_unique_name('lag'))
    data['native_vlan'] = 1
    data['ungrouped_vlans'] = '200'
    data['vlan_group_uuids'] = []
    data['port_properties'] = _port_properties(port_uuids, mlag)
    data['lacp_fallback'] = False
    data['enable_lossless'] = False

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    print('Create (m)LAG on ports = {}'.format(port_uuids))

    url = defines.vURL.format(host=afc_host, path=path, version='v1')
    r = requests.post(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    lag = r.json()['result']
    return lag


def delete_lags(afc_host, token, lag_uuids):
    """Delete a bunch of LAGs.

    Args:
        afc_host (str): Hostname of the AFC
        token (str): AFC token
        lag_uuids (list): list of LAG UUIDs to delete
    """
    path = 'lags'
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    params = dict()
    params['lags'] = lag_uuids

    url = defines.vURL.format(host=afc_host, path=path, version='v1')
    r = requests.delete(url, headers=headers, params=params, verify=False)
    r.raise_for_status()


def get_lag_str(lags):
    lag_str = str()
    for lg in lags:
        lag_str += '{} {} {}\n'.format(lg['uuid'], lg['name'], lg['type'])

    return lag_str


def get_lag(host, token, lag_uuid):
    path = 'lags/{}'.format(lag_uuid)
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    lag = r.json()['result']
    return lag


def get_lags(host, token, lag_type=None):
    path = 'lags'
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    } 

    params = dict()
    if lag_type:
        params['type'] = lag_type
        
    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()

    lags = r.json()['result']
    return lags


def patch_lag_policies(host, token, lag, policies, op):
    """Patch LAG specifying some operation for a list of policies.

    Args:
        host (str): AFC hostname
        token (str): AFC token
        lag (dict): AFC lag database object
        policies (list): list of policies to apply
        op (str): Add or Remove

    Returns:
        None
    """
    path = 'lags'

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    policy_uuids = [p['uuid'] for p in policies]
    data = [
        {
            'uuids': [lag['uuid']],
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

    print('Succeeded ({}) when applying policies: {} to LAG: {}'.format(
        r.status_code,
        ', '.join([p['name'] for p in policies]),
        lag['name']))


def apply_policies_to_lag(host, token, lag, policies):
    path = 'lags/{}'.format(lag['uuid'])

    data = copy.deepcopy(lag)
    data['qos_ingress_policies'] = [p['uuid'] for p in policies]

    for p in policies:
        print('Applying policy {} to lag {}'.format(p['name'], lag['name']))

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    } 

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.put(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    print('Succeeded ({}) applying policies {} to LAG: {} of type: {}'.format(
        r.status_code,
        ', '.join([p['name'] for p in policies]),
        lag['name'],
        lag['type']))


def delete_policies_from_lag(host, token, lag):
    path = 'lags/{}'.format(lag['uuid'])
    
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    } 

    data = copy.deepcopy(lag)
    data['qos_ingress_policies'] = []

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.put(url, headers=headers, json=data, verify=False)
    r.raise_for_status()
    print('Succeeded ({}) deleting ALL policies from LAG = {}'.format(r.status_code, lag['name']))


def display(host, token):
    switches = switches_module.get_switches(host, token)
    switch_map = {s['uuid']: s for s in switches}

    headers = ['Switch Name', 'LAG name', 'Type', 'MLAG', 'UUID', 'Ports']
    lags = get_lags(host, token, defines.LAG_TYPE_PROVISIONED)
    lag_table = []

    # lag_display = collections.defaultdict(list)
    for lag in lags:
        for port_info in lag['port_properties']:
            switch_uuid = port_info['switch_uuid']
            port_uuids = port_info['port_uuids']
            ports = []
            for port_uuid in port_uuids:
                port = ports_module.get_port(host, token, port_uuid)
                ports.append(port)

            port_names = [p['name'] for p in ports]
            port_names = '\n'.join(port_names)

            switch_name = switch_map[switch_uuid]['name']
            lag_info = [switch_name,
                        lag['name'],
                        lag['type'],
                        lag['mlag'],
                        lag['uuid'],
                        port_names]
            lag_table.append(lag_info)

        print(tabulate.tabulate(lag_table, headers=headers))


def display_lags(host, token, lags):
    import pprint
    header = ['Name', 'UUID', 'Type', 'MLAG']
    for lag in lags:
        print('LAG = {}'.format(pprint.pformat(lag)))
