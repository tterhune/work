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


def cleanup_policies(afc_host, token, policies):
    for policy in policies:
        print('Delete Policy: {}'.format(pprint.pformat(policy, indent=4)))

        for intf in policy['interfaces']:
            print('Disassociate Intf: {}/{} from policy: {}'.format(intf['object_type'],
                                                                    intf['object_uuid'],
                                                                    policy['name']))

            if intf['object_type'] == 'port':
                port = ports_module.get_port(afc_host, token, intf['object_uuid'])
                ports_module.patch_port_policies(afc_host, token, port, policy['uuid'],
                                                 defines.PATCH_OP_REMOVE)
            if intf['object_type'] == 'lag':
                lag = lags_module.get_lag(afc_host, token, intf['object_uuid'])
                lags_module.patch_lag_policies(afc_host, token, lag, policy['uuid'],
                                               defines.PATCH_OP_REMOVE)


def cleanup_qualifiers(afc_host, token, qualifiers):
    for qualifier in qualifiers:
        print('Qualifier: {}'.format(pprint.pformat(qualifier, indent=4)))
        policies_module.delete_qualifier(afc_host, token, qualifier)


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


def main(argv):
    if len(argv) < 2:
        print('Usage: {} <AFC host>'.format(argv[0]))
        sys.exit(1)
    
    afc_host = argv[1]
    token = afc_module.get_token(afc_host)
    
    policies = policies_module.get_qos_policies(afc_host, token)
    cleanup_policies(afc_host, token, policies)

    qualifiers = policies_module.get_qualifiers(afc_host, token)
    cleanup_qualifiers(afc_host, token, qualifiers)

    switches = switch_module.get_switches(afc_host, token)
    for switch in switches:
        cleanup_switch(switch)


if __name__ == '__main__':
    main(sys.argv)
