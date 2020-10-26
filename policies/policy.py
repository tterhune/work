import requests
import urllib3
import pprint

import shared.defines as defines
import policies.lags as lags_module
import policies.ports as ports_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_qualifiers(host, token):
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


def get_qos_policies(host, token):
    path = 'policies/qos'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    url = defines.vURL.format(host=host, headers=headers, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    policies = r.json()['result']
    return policies


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


def create_qualifier(host, token, name, vlans):
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


def create_qos_policy(host, token, policy_name, local_priority, pcp, qualifier_uuids):
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
        for intf in policy['interfaces']:
            print('Intf: {}/{}'.format(intf['object_type'], intf['object_uuid']))
            if intf['object_type'] == 'port':
                port = ports_module.get_port(afc_host, token, intf['object_uuid'])
                ports_module.patch_port_policies(afc_host, token, port, policy['uuid'],
                                                 defines.PATCH_OP_REMOVE)
            if intf['object_type'] == 'lag':
                lag = lags_module.get_lag(afc_host, token, intf['object_uuid'])
                lags_module.patch_lag_policies(afc_host, token, lag, policy['uuid'],
                                               defines.PATCH_OP_REMOVE)


def cleanup_qualifiers(afc_host, token):
    qualifiers = get_qualifiers(afc_host, token)
    for qualifier in qualifiers:
        print('Qualifier: {}'.format(pprint.pformat(qualifier, indent=4)))


def display(policies, qualifiers):
    print('\nAFC Policy Info:')

    print('\nAFC Qualifier Info:')
    for qualifier in qualifiers:
        print('Qualifier: {}'.format(pprint.pformat(qualifier, indent=4)))

    if not qualifiers:
        print('\t... no qualifiers configured')

    print('\nPolicy Info:')
    for policy in policies:
        print('\tPolicy: {}'.format(pprint.pformat(policy, indent=4)))

    if not policies:
        print('\t... no policies configured')


def display_all(afc_host, token):
    qualifiers = get_qualifiers(afc_host, token)
    policies = get_qos_policies(afc_host, token)

    display(policies, qualifiers)

