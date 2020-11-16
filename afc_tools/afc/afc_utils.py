import requests
import urllib3
import uuid

import afc_tools.shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def generate_unique_name(prefix=None):
    unique_name = uuid.uuid4().hex
    if prefix:
        unique_name = prefix + '-' + unique_name
    return unique_name


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
    # print('Token = {}'.format(token))
    return token


def get_version(host, token):
    path = 'versions'
    url = defines.vURL.format(host=host, path=path, version='v1')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': token,
        'accept': 'application/json',
    }

    r = requests.get(url, headers=headers, verify=False)
    r.raise_for_status()
    software_version = r.json()['result']['software']
    return software_version
