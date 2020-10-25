import requests
import urllib3
import pprint

import defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
