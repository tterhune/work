import requests
import urllib3

import shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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


def apply_policies_to_lag(host, token, lag, policies):
    path = 'lags/{}'.format(lag['uuid'])

    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    } 

    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.put(url, headers=headers, data=policies, verify=False)
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

    policies = []
    url = defines.vURL.format(host=host, path=path, version='v1')
    r = requests.put(url, headers=headers, data=policies, verify=False)
    r.raise_for_status()
    print('Succeeded ({}) deleting ALL policies from LAG = {}'.format(r.status_code, lag['name']))
