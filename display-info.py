#!/usr/bin/env python

import sys
import urllib3

import policies.afc as afc_module
import policies.aruba as aruba_module
import policies.policy as policy_module
import policies.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(argv):
    if len(argv) < 2:
        print('Usage: {} <AFC host>'.format(argv[0]))
        sys.exit(1)
    
    afc_host = argv[1]
    token = afc_module.get_token(afc_host)
    switches = switch_module.get_switches(afc_host, token)
    fabrics = switch_module.get_fabrics(afc_host, token)
    switch_module.display(fabrics, switches)

    qualifiers = policy_module.get_qualifiers(afc_host, token)
    policies = policy_module.get_qos_policies(afc_host, token)
    policy_module.display(policies, qualifiers)

    for switch in sorted(switches, key=lambda s: s['name']):
        cookie_jar = aruba_module.switch_login(switch)
        classifiers = aruba_module.get_switch_classes(switch, cookie_jar)
        policies = aruba_module.get_switch_policies(switch, cookie_jar)
        aruba_module.display(switch, classifiers, policies)
        aruba_module.switch_logout(switch, cookie_jar)


if __name__ == '__main__':
    main(sys.argv)
