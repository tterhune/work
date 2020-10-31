#!/usr/bin/env python

import pprint
import sys
import urllib3

import afc_magic.afc.afc_utils as afc_module
import afc_magic.shared.defines as defines
import afc_magic.afc.policy as policies_module
import afc_magic.afc.ports as ports_module
import afc_magic.afc.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(argv):
    if len(argv) < 2:
        print('Usage: {} <AFC host>'.format(argv[0]))
        sys.exit(1)
    
    afc_host = argv[1]
    token = afc_module.get_token(afc_host)
    
    switches = switch_module.get_switches(afc_host, token)
    switch_module.display(switches)

    leaf_switch = None
    leaf_switches = list()
    for switch in switches:
        if switch['role'] == defines.SWITCH_ROLE_LEAF:
            leaf_switches.append(switch)
            if switch['status'] == 'SYNCED':
                leaf_switch = switch
                break

    port = None
    if leaf_switch:
        ports = ports_module.get_ports(afc_host, token, switches=[leaf_switch['uuid']])
        for port in ports:
            if port['type'] == 'access' and port['admin_state'] == 'disabled':
                print('Port = {}'.format(pprint.pformat(port, indent=4)))
                break
    # plag = None
    # provisioned_lags = lags_module.get_lags(afc_host, token, lag_type=defines.LAG_TYPE_PROVISIONED)
    # if provisioned_lags:
    #    plag = provisioned_lags[0]

    policy = None
    policies = policies_module.get_qos_policies(afc_host, token)
    for policy in policies:
        print('Policy: {}'.format(pprint.pformat(policy, indent=4)))

    if policies:
        policy = policies[0]

    if port:
        ports_module.apply_policies_to_port(afc_host, token, port, [policy])
        print('Successfully applied Policy: {} Port: {} Switch: {}'.format(
            policy['name'],
            port['name'],
            leaf_switch['name']))

    # ports_module.patch_port_policies(afc_host, token, port, policies, defines.PATCH_OP_ADD)

    ports_module.delete_policies_from_port(afc_host, token, port)

    # if plag and policy:
    #     lags_module.apply_policies_to_lag(afc_host, token, plag, [policy])
    # lags_module.apply_policies_to_lag(afc_host, token, plag, [policy])

    # for lag in provisioned_lags:
    #     print('Provisioned LAG = {}'.format(pprint.pformat(lag, indent=4)))

    # internal_lags = lags_module.get_lags(afc_host, token, lag_type=defines.LAG_TYPE_INTERNAL)
    # for lag in internal_lags:
    #     print('Internal LAG = {}'.format(pprint.pformat(lag, indent=4)))
        
    # cookie_jar = switch_login(switch)
    # time.sleep(2)
    # get_switch_classes(switch, cookie_jar)
    # get_switch_policies(switch, cookie_jar)
    # switch_logout(switch, cookie_jar)

    # q = policies_module.create_qualifier(afc_host, token, 'my-qualifier11', vlans='100')
    # p = policies_module.create_qos_policy(afc_host, token, 'my-policy11', 5, 5, [q])


if __name__ == '__main__':
    main(sys.argv)
