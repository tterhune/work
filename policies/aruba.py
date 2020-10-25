import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def switch_login(switch):
    """Log into Aruba switch."""
    print('Attempting to log into switch {} {}'.format(switch['name'], switch['ip_address']))
    url = 'https://{}/rest/v10.04/login'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'multipart/form-data'
    } 

    params = {
        'username': 'admin',
        'password': 'plexxi'
    }

    r = requests.post(url, headers=headers, params=params, verify=False)
    r.raise_for_status()
    
    print('Successfully ({}) logged into switch {}/{}: cookies = {}'.format(r.status_code,
                                                                            switch['name'],
                                                                            switch['ip_address'],
                                                                            r.cookies))
    return r.cookies


def switch_logout(switch, cookie_jar):
    print('Attempting to logout of switch {} {}'.format(switch['name'], switch['ip_address']))
    url = 'https://{}/rest/v10.04/logout'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    r = requests.post(url, headers=headers, cookies=cookie_jar, verify=False)
    r.raise_for_status()
    print('Successfully ({}) logged out of {}/{}'.format(r.status_code,
                                                         switch['name'],
                                                         switch['ip_address']))
    

def get_switch_classes(switch, cookie_jar):
    url = 'https://{}/rest/v10.04/classes'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    classes = r.json()['result']
    
    print('Got classes: {} from switch: {}'.format(classes, switch['name']))


def get_switch_policies(switch, cookie_jar):
    url = 'https://{}/rest/v10.04/policies'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    policies = r.json()['result']
    print('Got policies: {} from switch {}'.format(switch['name'], policies))

