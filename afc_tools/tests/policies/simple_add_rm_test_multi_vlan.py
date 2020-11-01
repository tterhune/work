#!/usr/bin/env python

import pprint
import sys
import time
import urllib3

import afc_magic.afc.afc_utils as afc_module
import afc_magic.aruba.aruba_utils as aruba_module
import afc_magic.aruba.policies as aruba_policies
import afc_magic.shared.defines as defines
import afc_magic.afc.policy as policies_module
import afc_magic.afc.ports as ports_module
import afc_magic.afc.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def display_all(leaf_switch, cookie_jar):
    aruba_policies.display_all(leaf_switch, cookie_jar)
    print('\n')


def main(afc_host):
    token = afc_module.get_token(afc_host)

    # Display some info
    switches = switch_module.get_switches(afc_host, token)
    fabrics = switch_module.get_fabrics(afc_host, token)
    switch_module.display(fabrics, switches)
    policies_module.display_all(afc_host, token)

    time.sleep(1)

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

    print('Using port: {} on switch: {}'.format(port['name'], leaf_switch['name']))

    # Create qualifier and policy
    qualifier_uuid = policies_module.create_qualifier(afc_host, token, '100-110')
    policy_uuid = policies_module.create_qos_policy(afc_host, token, 4, 5, [qualifier_uuid])

    policy = policies_module.get_qos_policy(afc_host, token, policy_uuid)

    time.sleep(1)

    print('\n\t{} ADDING POLICY: {} to PORT: {} {}\n'.format('-' * 10, policy['name'],
                                                             port['name'], '-' * 10))

    # Apply policy to port
    ports_module.patch_port_policies(afc_host, token, port, [policy], defines.PATCH_OP_ADD)
    print('Successfully Added Policy: {} Port: {} Switch: {}'.format(policy['name'], port['name'],
          leaf_switch['name']))

    # Display AFC info
    policies_module.display_all(afc_host, token)

    port = ports_module.get_port(afc_host, token, port['uuid'])
    print('\nPort after applying Policy: {}\n'.format(pprint.pformat(port, indent=4)))

    # Display switch info
    cookie_jar = aruba_module.switch_login(leaf_switch)

    # classifiers = aruba_module.get_switch_classes(leaf_switch, cookie_jar)
    # policies = aruba_module.get_switch_policies(leaf_switch, cookie_jar)
    # aruba_module.display(leaf_switch, classifiers, policies)

    display_all(leaf_switch, cookie_jar)

    # aruba_module.switch_logout(leaf_switch, cookie_jar)

    print('\n\t{} DELETING POLICY: {} from PORT: {} {}\n'.format('-' * 10, policy['name'],
                                                                 port['name'], '-' * 10))

    time.sleep(2)

    ports_module.patch_port_policies(afc_host, token, port, [policy], defines.PATCH_OP_REMOVE)
    port = ports_module.get_port(afc_host, token, port['uuid'])
    print('\nPort after deleting Policy: {}'.format(pprint.pformat(port, indent=4)))

    time.sleep(1)

    display_all(leaf_switch, cookie_jar)

    print('\nCleaning up all qualifiers and policies')
    policies_module.cleanup_qualifiers(afc_host, token)
    policies_module.cleanup_policies(afc_host, token)

    # Display switch info
    # cookie_jar = aruba_module.switch_login(leaf_switch)

    # classifiers = aruba_module.get_switch_classes(leaf_switch, cookie_jar)
    # classifier_entries = []
    # for classifier in classifier_entries:
    #    classifier_entry = aruba_module.get_classifier_entries(leaf_switch, cookie_jar, classifier)
    #    classifier_entries.append(classifier_entry)

    # policies = aruba_module.get_switch_policies(leaf_switch, cookie_jar)
    # policy_entries = []
    # for policy in policies:
    #     policy_entry = aruba_module.get_policy_entries(leaf_switch, cookie_jar, policy)
    #     policy_entries.append(policy_entry)
    #     policy_action_set = aruba_module.get_policy_action_set(leaf_switch, cookie_jar,
    #                                                            policy_entry)
    #     policy_entries.append((policy_entry, policy_action_set))
    # aruba_module.display_all(leaf_switch, classifiers, policies, policy_entries)

    aruba_module.switch_logout(leaf_switch, cookie_jar)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
