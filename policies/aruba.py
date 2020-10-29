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


def get_classifier_entries(switch, cookie_jar, classifier):
    print('GET: classifier = {}'.format(pprint.pformat(classifier, indent=4)))
    url = 'https://{}/rest/v10.04/system/classes/{},{}/cfg_entries'.format(
        switch['ip_address'], classifier['name'], classifier['type'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    classifier_entries = r.json()

    return classifier_entries if classifier_entries else {}


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


def get_policy_entries(switch, cookie_jar, policy):
    url = 'https://{}/rest/v10.04/system/policies/{}/cfg_entries'.format(switch['ip_address'],
                                                                         policy['name'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    policy_entries = r.json()
    # print('Got policies: {} from switch {}'.format(pprint.pformat(policies, indent=4),
    #                                               switch['name']))
    return policy_entries if policy_entries else {}


def get_policy_action_set(switch, cookie_jar, policy_entry):
    print('Policy entry: {}'.format(pprint.pformat(policy_entry, indent=4)))
    uri = policy_entry['policy_action_set']
    url = 'https://{}{}'.format(switch['ip_address'], uri)

    print('GET Policy Action Set: {}'.format(url))

    # url = 'https://{}/rest/v10.04/system/policies/{}/cfg_entries/{}/policy_action_set'.format(
    #    switch['ip_address'], policy['name'], policy_entry['sequence_number'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    policy_action_set = r.json()
    # print('Got policies: {} from switch {}'.format(pprint.pformat(policies, indent=4),
    #                                               switch['name']))
    return policy_action_set if policy_action_set else {}


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

    if classifiers:
        print('Classifiers:')
        print('------------')
        for name, classifier in classifiers.items():
            print('\t{} state: {} code: {}'.format(name, classifier['status']['state'],
                                                   classifier['status']['code']))
    else:
        print('{0: <12} {1}'.format('Classifiers:', '=> no classifiers configured'))

    if policies:
        print('Policies:')
        print('---------')
        for policy in policies:
            print('\t{}'.format(pprint.pformat(policy, indent=4)))
    else:
        print('{0: <12} {1}'.format('Policies:', '=> no policies configured'))


def display_tree(switch, classifiers, policies, classifier_entries, policy_entries):
    display(switch, classifiers, policies)

    if not classifier_entries:
        print('{0: <20} {1}'.format('Classifier Entries:', '=> no classifier entries configured'))

    for classifier_entry in classifier_entries:
        print('Classifier Entry: {}'.format(classifier_entry[0]))
        classifier_entry_dict = classifier_entry[1]
        print('{0: <10} {1: <5}'.format('Priority', 'VLAN'))
        print('{} {}'.format('-' * 10, '-' * 5))
        for priority, ce in sorted(classifier_entry_dict.items(), key=lambda t: int(t[0])):
            print('{0: <10} {1: <5}'.format(priority, ce['vlan']))

    if not policy_entries:
        print('{0: <20} {1}'.format('Policy Entries:', '=> no policy entries configured'))

    print('\n')
    for policy_entry in policy_entries:
        print('Policy Entry: {}'.format(pprint.pformat(policy_entry[0], indent=4)))
        print('Policy Action Set: {}'.format(pprint.pformat(policy_entry[1], indent=4)))


def display_all(leaf_switch, cookie_jar):
    classifiers = get_switch_classes(leaf_switch, cookie_jar)
    classifier_entries = []
    for name, classifier in classifiers.items():
        classifier_entry = get_classifier_entries(leaf_switch, cookie_jar, classifier)
        classifier_entries.append((name, classifier_entry))

    policies = get_switch_policies(leaf_switch, cookie_jar)
    policy_entries = []
    for name, policy in policies.items():
        policy_entry_dict = get_policy_entries(leaf_switch, cookie_jar, policy)
        for priority, policy_entry in policy_entry_dict.items():
            policy_action_set = get_policy_action_set(leaf_switch, cookie_jar, policy_entry)
            policy_entries.append(((priority, policy_entry), policy_action_set))

    display_tree(leaf_switch, classifiers, policies, classifier_entries, policy_entries)
