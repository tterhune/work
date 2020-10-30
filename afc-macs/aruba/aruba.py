import pprint
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def switch_login(switch):
    """Log into Aruba switch."""
    # print('Attempting to LOG INTO switch {} ({})'.format(switch['name'], switch['ip_address']))

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
    
    # print('Successfully ({}) logged into switch {} ({})'.format(r.status_code,
    #                                                            switch['name'],
    #                                                            switch['ip_address']))

    return r.cookies


def switch_logout(switch, cookie_jar):
    # print('Attempting to LOGOUT of switch {} ({})'.format(switch['name'], switch['ip_address']))

    url = 'https://{}/rest/v10.04/logout'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    r = requests.post(url, headers=headers, cookies=cookie_jar, verify=False)
    r.raise_for_status()
    # print('Successfully ({}) logged out of {} ({})'.format(r.status_code,
    #                                                      switch['name'],
    #                                                      switch['ip_address']))
    

def get_mac_attachments(switch, cookie_jar):
    url = 'https://{}/rest/v10.04/system/vlans/*/macs'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    macs = r.json()
    
    print('Got classes: {} from switch: {}'.format(pprint.pformat(macs, indent=4), switch['name']))
    return macs if macs else {}


def display(switches, cookie_jar):
    for switch in switches:
        print('\nMAC Attachments for switch {} ({}):'.format(switch['name'], switch['ip_address']))

        macs = get_mac_attachments(switch, cookie_jar=cookie_jar)

        print('{0: <12} {1}'.format('Policies:', '=> no policies configured'))

