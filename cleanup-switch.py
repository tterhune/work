#!/usr/bin/env python

import pprint
import sys
import urllib3

import policies.afc as afc_module
import policies.aruba as aruba_module
import shared.defines as defines
import policies.lags as lags_module
import policies.policy as policies_module
import policies.ports as ports_module
import policies.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def cleanup_switch(switch):
    cookie_jar = aruba_module.switch_login(switch)

    classifiers = aruba_module.get_switch_classes(switch, cookie_jar)
    for name, classifier in classifiers.items():
        print('Found classifier: {} on switch: {}'.format(name, switch['name']))

        aruba_module.delete_classifier(switch, cookie_jar, classifier)

    policies = aruba_module.get_switch_policies(switch, cookie_jar)
    for name, policy in policies.items():
        print('Found policy: {} on switch: {}'.format(name, switch['name']))

        aruba_module.delete_policy(switch, cookie_jar, policy)

    aruba_module.switch_logout(switch, cookie_jar)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    
    switches = switch_module.get_switches(afc_host, token)
    for switch in switches:
        cleanup_switch(switch)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
