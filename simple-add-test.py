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


def main(argv):
    if len(argv) < 2:
        print('Usage: {} <AFC host>'.format(argv[0]))
        sys.exit(1)
    
    afc_host = argv[1]
    token = afc_module.get_token(afc_host)

    # Display some info
    switches = switch_module.get_switches(afc_host, token)
    switch_module.display(switches)
    policies_module.display_all(afc_host, token)

    # Find a leaf switch
    leaf_switch = None
    leaf_switches = list()
    for switch in switches:
        if switch['role'] == defines.SWITCH_ROLE_LEAF:
            leaf_switches.append(switch)
            if switch['status'] == 'SYNCED':
                leaf_switch = switch
                break

    # Pick a port
    port = None
    if leaf_switch:
        ports = ports_module.get_ports(afc_host, token, switches=[leaf_switch['uuid']])
        for port in ports:
            if (port['type'] == 'access' and port['admin_state'] == 'disabled' and
                    not port['qos_ingress_policies']):
                print('Port = {}'.format(pprint.pformat(port, indent=4)))
                break

    # Create qualifier and policy
    qualifier = policies_module.create_qualifier(afc_host, token, 'simple-add-test-qual', [100])
    policy = policies_module.create_qos_policy(afc_host, token, 'simple-add-test-policy', 4, 5,
                                               [qualifier['uuid']])

    # Apply policy to port
    ports_module.patch_port_policies(afc_host, token, port, policy, defines.PATCH_OP_ADD)
    print('Successfully Added Policy: {} Port: {} Switch: {}'.format(policy['name'], port['name'],
          leaf_switch['name']))

    # Display AFC info
    policies_module.display_all(afc_host, token)

    port = ports_module.get_port(afc_host, token, port['uuid'])
    print('Port after applying Policy: {}'.format(pprint.pformat(port, indent=4)))

    # Display switch info
    cookie_jar = aruba_module.switch_login(leaf_switch)

    classifiers = aruba_module.get_switch_classes(leaf_switch, cookie_jar)
    policies = aruba_module.get_switch_policies(leaf_switch, cookie_jar)
    aruba_module.display(leaf_switch, classifiers, policies)

    aruba_module.switch_logout(leaf_switch, cookie_jar)

    ports_module.patch_port_policies(afc_host, token, port, policy, defines.PATCH_OP_REMOVE)
    port = ports_module.get_port(afc_host, token, port['uuid'])
    print('Port after deleting Policy: {}'.format(pprint.pformat(port, indent=4)))

    print('Cleaning up all qualifiers and policies')
    policies_module.cleanup_qualifiers(afc_host, token)
    policies_module.cleanup_policies(afc_host, token)

    # Display switch info
    cookie_jar = aruba_module.switch_login(leaf_switch)

    classifiers = aruba_module.get_switch_classes(leaf_switch, cookie_jar)
    policies = aruba_module.get_switch_policies(leaf_switch, cookie_jar)
    aruba_module.display(leaf_switch, classifiers, policies)

    aruba_module.switch_logout(leaf_switch, cookie_jar)


if __name__ == '__main__':
    main(sys.argv)
