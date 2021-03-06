import pprint
import requests
import urllib3

import afc_tools.aruba.interfaces as interfaces_module
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_queue_stats(cookie_jar, switch, interface_name):
    """Get queues for a switch.

    Arguments:
        cookie_jar (requests.CookieJar): requests cookie jar
        switch (dict): AFC switch object
        interface_name (str): name of intf

    Returns:
        dict: classifiers switch object, which is a dictionary
    """
    intf_name = interface_name.replace('/', '%2F')
    url = 'https://{}/rest/v10.04/system/interfaces/{}'.format(switch['ip_address'], intf_name)
    # GET "https://10.101.36.192/rest/v10.04/system/interfaces/1%2F1%2F1?attributes=queue_tx_bytes,queue_tx_errors,queue_tx_maxdepth,queue_tx_packets"
    # "accept: application/json"
    # GET https://diablo-sw-02.lab.plexxi.com/rest/v10.04/system/qos?attributes=queues&depth=2"
    # "accept: application/json"

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    queues = ['queue_tx_bytes',
              'queue_tx_errors',
              'queue_tx_maxdepth',
              'queue_tx_packets']

    queue_names = ','.join(queues)

    params = {
        'depth': 2,
        'attributes':  queue_names
        # 'selector': 'statistics'
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    queue_stats = r.json()
    return queue_stats

    # print('Got qos: {} from switch: {}'.format(pprint.pformat(qos, indent=4), switch['name']))

    # url = 'https://{}/rest/v10.04/system/queues'.format(switch['ip_address'])

    # url = 'https://{}/rest/v10.04/system/q_profiles/factory-default/q_profile_entries'.format(switch['ip_address'])

    # headers = {
    #     'accept': 'application/json',
    #     'Content-Type': 'application/json'
    # }

    # params = {
    #     'depth': 2
   #  }

    # r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    # r.raise_for_status()

    # queues = r.json()
    # print('Got queues: {} from switch: {}'.format(pprint.pformat(queues, indent=4), switch['name']))

    # return queues if queues else {}


def get_switch_classes(cookie_jar, switch):
    """Get classifiers for a switch.

    Arguments:
        cookie_jar (requests.CookieJar): requests cookie jar
        switch (dict): AFC switch object

    Returns:
        dict: classifiers switch object, which is a dictionary
    """
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
    # print('GET: classifier = {}'.format(pprint.pformat(classifier, indent=4)))
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


def get_switch_policies(cookie_jar, switch):
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
    print('GET policy entries for policy: {}'.format(policy['name']))
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

    policy_action_set = None
    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    try:
        r.raise_for_status()
        policy_action_set = r.json()
    except requests.exceptions.HTTPError:
        if r.status_code == requests.codes.not_found:
            print('*** Policy action set: {} GET not found: {}'.format(
                policy_entry['policy_action_set'],
                r.status_code))
        else:
            print('*** Policy action set: {} GET failure: {}'.format(
                policy_entry['policy_action_set'],
                r.status_code))

    # print('Got policies: {} from switch {}'.format(pprint.pformat(policies, indent=4),
    #                                               switch['name']))
    return policy_action_set if policy_action_set else {}


def delete_policy(cookie_jar, switch, policy):
    print('Deleting policy: {} on switch: {}'.format(policy['name'], switch['name']))

    url = 'https://{}/rest/v10.04/system/policies/{}'.format(switch['ip_address'], policy['name'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    r = requests.delete(url, headers=headers, cookies=cookie_jar, verify=False)
    r.raise_for_status()


def delete_classifier(cookie_jar, switch, classifier):
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


def delete_all(cookie_jar, switch):
    policies = get_switch_policies(cookie_jar, switch)
    classifiers = get_switch_classes(cookie_jar, switch)

    for name, policy in policies.items():
        print('Deleting Policy: {}'.format(pprint.pformat(policy, indent=4)))
        delete_policy(cookie_jar, switch, policy)

    for name, classifier in classifiers.items():
        print('Deleting Classifier: {}'.format(pprint.pformat(classifier, indent=4)))
        delete_classifier(cookie_jar, switch, classifier)


def display(switch, classifiers, policies):
    print('\nPolicies and Classifiers on switch {} ({}):'.format(switch['name'],
                                                                 switch['ip_address']))

    if classifiers:
        print('Classifiers:')
        print('------------')

        max_name_len = 0
        for name, classifier in classifiers.items():
            max_name_len = max(max_name_len, len(name))

        print('{0: ^{4}} {1: <6} {2: <10} {3: <6}'.format(
            'Classifier Name',
            'Type',
            'State',
            'Code',
            max_name_len))
        print('{0} {1} {2} {3}'.format(
            '-' * max_name_len,
            '-' * 6,
            '-' * 10,
            '-' * 6))
        for name, classifier in classifiers.items():
            print('{0: <{4}} {1: <6} {2: <10} {3: <6}'.format(
                classifier['name'],
                classifier['type'],
                classifier['status']['state'],
                classifier['status']['code'],
                max_name_len))
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
        # print('Classifier Entry: {}'.format(classifier_entry[0]))
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
    classifiers = get_switch_classes(cookie_jar, leaf_switch)
    classifier_entries = []
    for name, classifier in classifiers.items():
        classifier_entry = get_classifier_entries(leaf_switch, cookie_jar, classifier)
        classifier_entries.append((name, classifier_entry))

    policies = get_switch_policies(cookie_jar, leaf_switch)
    policy_entries = []
    for name, policy in policies.items():
        policy_entry_dict = get_policy_entries(leaf_switch, cookie_jar, policy)
        for priority, policy_entry in policy_entry_dict.items():
            policy_action_set = get_policy_action_set(leaf_switch, cookie_jar, policy_entry)
            policy_entries.append(((priority, policy_entry), policy_action_set))

    display_tree(leaf_switch, classifiers, policies, classifier_entries, policy_entries)

    interfaces = interfaces_module.get_interfaces(leaf_switch, cookie_jar)

    for interface_name, interface in interfaces.items():
        if 'policy_in_cfg' in interface and interface['policy_in_cfg']:
            print('{}: {}'.format(interface_name, interface['policy_in_cfg']))
            # intf = interfaces_module.get_writable_intf(leaf_switch, cookie_jar, interface_name)
            # print('writable {}: {}'.format(interface_name, pprint.pformat(intf, indent=4)))
            queue_stats = get_queue_stats(cookie_jar, leaf_switch, interface_name)
            print('{} queue_stats = {}'.format(interface_name, pprint.pformat(queue_stats, indent=4)))

