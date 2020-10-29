#!/usr/bin/env python

import sys
import urllib3

import policies.afc as afc_module
import policies.aruba as aruba_module
import policies.policy as policy_module
import policies.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    switches = switch_module.get_switches(afc_host, token)
    fabrics = switch_module.get_fabrics(afc_host, token)
    switch_module.display(fabrics, switches)

    qualifiers = policy_module.get_qualifiers(afc_host, token)
    policies = policy_module.get_qos_policies(afc_host, token)
    policy_module.display(afc_host, token, policies, qualifiers)

    for switch in sorted(switches, key=lambda s: s['name']):
        cookie_jar = aruba_module.switch_login(switch)
        # classifiers = aruba_module.get_switch_classes(switch, cookie_jar)
        # policies = aruba_module.get_switch_policies(switch, cookie_jar)
        # aruba_module.display(switch, classifiers, policies)
        aruba_module.display_all(switch, cookie_jar)
        aruba_module.switch_logout(switch, cookie_jar)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
