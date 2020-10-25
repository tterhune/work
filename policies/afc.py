import requests
import urllib3

import shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def ping_afc(host):
    path = 'ping'
    url = defines.URL.format(host=host, path=path)
    headers = {
        'Content-Type': 'application/json',
        'accept': 'application/json',
        'X-Auth-Username': 'admin',
        'X-Auth-Password': 'plexxi'
    } 
    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()


def get_token(host):
    path = defines.TOKEN
    url = defines.vURL.format(host=host, path=path, version='v1')

    headers = {
        'accept': 'application/json',
        'X-Auth-Username': 'admin',
        'X-Auth-Password': 'plexxi'
    } 

    r = requests.post(url, headers=headers, verify=False)
    r.raise_for_status()
    token = r.json()['result']
    print(f'Token = {token}')
    return token