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
    

def get_switch_classes(switch, cookie_jar):
    url = 'https://{}/rest/v10.04/system/classes'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    classifiers = r.json()
    
    # print('Got classes: {} from switch: {}'.format(pprint.pformat(classifiers, indent=4),
    #                                               switch['name']))
    return classifiers if classifiers else {}


def get_switch_policies(switch, cookie_jar):
    url = 'https://{}/rest/v10.04/system/policies'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    policies = r.json()
    # print('Got policies: {} from switch {}'.format(pprint.pformat(policies, indent=4),
    #                                               switch['name']))
    return policies if policies else {}


def delete_policy(switch, cookie_jar, policy):
    print('Deleting policy: {} on switch: {}'.format(policy['name'], switch['name']))

    url = 'https://{}/rest/v10.04/system/policies/{}'.format(switch['ip_address'], policy['name'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    r = requests.delete(url, headers=headers, cookies=cookie_jar, verify=False)
    r.raise_for_status()


def delete_classifier(switch, cookie_jar, classifier):
    print('Deleting classifier: {} on switch: {}'.format(classifier['name'], switch['name']))

    url = 'https://{}/rest/v10.04/system/classes/{},{}'.format(switch['ip_address'],
                                                               classifier['name'],
                                                               classifier['type'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        r = requests.delete(url, headers=headers, cookies=cookie_jar, verify=False)
        print('Status = {}'.format(r.status_code))
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print('Failed to delete classifier: {},{}'.format(classifier['name'], classifier['type']))


def display(switch, classifiers, policies):
    print('\nPolicies and Classifiers on switch {} ({}):'.format(switch['name'],
                                                                 switch['ip_address']))

    print('Classifiers:')
    for classifier in classifiers:
        print('\t{}'.format(pprint.pformat(classifier, indent=4)))

    if not classifiers:
        print('\t... no classifiers configured')

    print('\nPolicies:')
    for policy in policies:
        print('\t{}'.format(pprint.pformat(policy, indent=4)))

    if not policies:
        print('\t... no policies configured')

    print('\n')
