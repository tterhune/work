import copy
import requests
import urllib3

import afc_tools.shared.defines as defines
import afc_tools.afc.afc_utils as utils
import tabulate


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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

    print('Create LAG on ports = {}'.format(port_uuids))

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


def display_lags(host, token, lags):
    import pprint
    header = ['Name', 'UUID', 'Type', 'MLAG']
    for lag in lags:
        print('LAG = {}'.format(pprint.pformat(lag)))
