import copy
import requests
import urllib3

import shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_lag_str(afc_host, token, lags):
    lag_str = str()
    for lg in lags:
        lag_str += '\t\t{} {} {}'.format(lg['name'], lg['type'], lg['uuid'])

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
