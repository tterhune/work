import pprint
import requests
from typing import List, Optional
import urllib3
import uuid

import shared.defines as defines
import policies.lags as lags_module
import policies.ports as ports_module
import policies.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def generate_unique_name(prefix: Optional[str] = None) -> str:
    unique_name = uuid.uuid4().hex
    if prefix:
        unique_name = prefix + '-' + unique_name
    return unique_name


def get_qualifiers(host: str, token: str) -> List[dict]:
    path = 'qualifiers'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    url = defines.vURL.format(host=host, headers=headers, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    qualifiers = r.json()['result']
    return qualifiers


def get_qos_policies(host: str, token: str) -> List[dict]:
    """Get all QoS policies from a particular AFC.
    Args:
        host (str):
        token (str):

    Returns:
        list[dict]
    """
    path = 'policies/qos'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    params = {
        'interfaces': True,
        'tags': True
    }

    url = defines.vURL.format(host=host, headers=headers, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()

    policies = r.json()['result']
    return policies


def get_qos_policy(afc_host: str, token: str, policy_uuid: str) -> dict:
    """Get a particular QoS policy based on UUID.

    Args:
        afc_host (str):
        token (str):
        policy_uuid (str):

    Returns:
        dict: Qos Policy dict
    """
    path = 'policies/qos/{}'.format(policy_uuid)
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    params = {
        'interfaces': True,
        'tags': True
    }

    url = defines.vURL.format(host=afc_host, headers=headers, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False, params=params)
    r.raise_for_status()

    policy = r.json()['result']
    return policy


def delete_policy(host, token, policy):
    path = 'policies/qos/{}'.format(policy['uuid'])

    print('Deleting policy: {}/{}'.format(policy['name'], policy['uuid']))

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    url = defines.vURL.format(host=host, headers=headers, path=path, version='v1')
    r = requests.delete(url, headers=headers, verify=False)
    r.raise_for_status()


def delete_qualifier(host, token, qualifier):
    path = 'qualifiers/{}'.format(qualifier['uuid'])

    print('Deleting qualifier: {}/{}'.format(qualifier['name'], qualifier['uuid']))

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.delete(url, headers=headers, verify=False)
    r.raise_for_status()


def create_qualifier(host, token, vlans, name=None):
    if not name:
        name = generate_unique_name('qual')

    path = 'qualifiers'
    print(f'Creating qualifier: {name} with vlans: {vlans}')
    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    data = {
        'name': name,
        'vlans': vlans
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.post(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    qualifier_uuid = r.json()['result']
    print(f'Successfully created qualifier UUID: {qualifier_uuid}')

    return qualifier_uuid


def create_qos_policy(host, token, local_priority, pcp, qualifier_uuids, policy_name=None):
    if not policy_name:
        policy_name = generate_unique_name('policy')

    print(f'Creating policy: {policy_name} with LP/PCP: {local_priority} {pcp}')

    qualifiers = [{'object_uuid': quuid, 'object_type': 'qualifier'} for quuid in qualifier_uuids]
    print('With qualifiers: {}'.format(pprint.pformat(qualifiers, indent=4)))

    path = 'policies/qos'
    url = defines.vURL.format(host=host, path=path, version='v1')

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token,
    }
    
    data = {
        'name': policy_name,
        'description': 'Policy created running Tim script',
        'local_priority': local_priority,
        'pcp': pcp,
        'qualifiers': qualifiers
    }

    r = requests.post(url, headers=headers, json=data, verify=False)
    r.raise_for_status()

    policy_uuid = r.json()['result']

    print(f'Created policy UUID = {policy_uuid}')
    return policy_uuid


def cleanup_policies(afc_host, token):
    policies = get_qos_policies(afc_host, token)
    for policy in policies:
        print('Policy: {}'.format(pprint.pformat(policy, indent=4)))
        for intf in policy.get('interfaces', []):
            print('Intf: {} {}'.format(intf['object_type'], intf['object_uuid']))
            if intf['object_type'] == 'port':
                port = ports_module.get_port(afc_host, token, intf['object_uuid'])
                ports_module.patch_port_policies(afc_host, token, port, [policy],
                                                 defines.PATCH_OP_REMOVE)
            if intf['object_type'] == 'lag':
                lag = lags_module.get_lag(afc_host, token, intf['object_uuid'])
                lags_module.patch_lag_policies(afc_host, token, lag, [policy],
                                               defines.PATCH_OP_REMOVE)
        delete_policy(afc_host, token, policy)


def cleanup_qualifiers(afc_host, token):
    qualifiers = get_qualifiers(afc_host, token)
    for qualifier in qualifiers:
        print('Qualifier: {}'.format(pprint.pformat(qualifier, indent=4)))
        delete_qualifier(afc_host, token, qualifier)


def get_port_str(afc_host, token, ports):
    port_str = str()
    for p in ports:
        s = switch_module.get_switch(afc_host, token, p['switch_uuid'])
        port_str += '\t\t{}: {} {}\n'.format(s['name'], p['name'], p['uuid'])

    return port_str


def get_lag_str(afc_host, token, lags):
    lag_str = str()
    for lg in lags:
        lag_str += '\t\t{} {} {}'.format(lg['name'], lg['type'], lg['uuid'])

    return lag_str


def display(afc_host, token, policies, qualifiers):
    print('\nAFC Policy Info:')

    if qualifiers:
        print('AFC Qualifier:')
        for qualifier in qualifiers:
            print('\tQualifier: {}'.format(pprint.pformat(qualifier, indent=4)))
    else:
        print('{0: <15} {1}'.format('AFC Qualifier:', '=> no qualifiers configured'))

    if policies:
        print('AFC Policy:')
        for policy in policies:
            intfs = policy.get('interfaces', [])
            ports = []
            lags = []
            for intf in intfs:
                if intf['object_type'] == 'port':
                    port = ports_module.get_port(afc_host, token, intf['object_uuid'])
                    ports.append(port)
                elif intf['object_type'] == 'lag':
                    lag = lags_module.get_lag(afc_host, token, intf['object_uuid'])
                    lags.append(lag)

            # print('\tPolicy: {}'.format(pprint.pformat(policy, indent=4)))

            port_str = get_port_str(afc_host, token, ports)
            lag_str = get_lag_str(afc_host, token, lags)

            print('\tPolicy: {} {} {} {}'.format(policy['name'],
                                                 policy['pcp'],
                                                 policy['local_priority'],
                                                 policy['uuid']))
            print('\tPorts: \n{}'.format(port_str))
            print('\tLAGs: \n{}'.format(lag_str))
    else:
        print('{0: <15} {1}'.format('AFC Policy:', '=> no policies configured'))


def display_all(afc_host, token):
    qualifiers = get_qualifiers(afc_host, token)
    policies = get_qos_policies(afc_host, token)

    display(afc_host, token, policies, qualifiers)

