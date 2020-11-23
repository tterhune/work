import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _switch_login(switch, password):
    # print('Attempting to LOG INTO switch {} ({})'.format(switch['name'], switch['ip_address']))

    url = 'https://{}/rest/v10.04/login'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'multipart/form-data'
    }

    params = {
        'username': 'admin',
        'password': password
    }

    r = requests.post(url, headers=headers, params=params, verify=False)
    r.raise_for_status()
    return r


def switch_login(switch):
    """Log into Aruba switch.

    Arguments:
        switch (dict): AFC switch object

    Returns:
        dict: cookie jar
    """
    try:
        r = _switch_login(switch, 'plexxi')
    except requests.exceptions.HTTPError as e:
        print('Switch {} login failed, trying different credentials'.format(switch['name']))
        r = _switch_login(switch, 'aruba')
    
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
