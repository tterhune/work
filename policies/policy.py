import requests
import urllib3
import pprint

import shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_qualifiers(host, token):
    path = 'qualifiers'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': token
    }

    url = defines.vURL.format(host=host, path=path, version='v1')
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

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()

    policies = r.json()['result']
    return policies


def create_qualifier(host, token, name, vlans):
    print(f'Creating qualifier: {name} with vlans: {vlans}')
    
    path = 'qualifiers'
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


def display(policies, qualifiers):
    print('Policy Info:')
    for policy in policies:
        print('Policy: {}'.format(pprint.pformat(policy, indent=4)))

    print('Qualifier Info:')
    for qualifier in qualifiers:
        print('Qualifier: {}'.format(pprint.pformat(qualifier, indent=4)))
