#!/usr/bin/env python

import pprint
import sys
import urllib3

import policies.afc as afc_module
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
    
    # fabric_uuid = create_fabric(afc_host, token, 'tim-fabric')
    # do_discover()

    switches = switch_module.get_switches(afc_host, token)
    leaf_switches = list()
    for switch in switches:
        print('Switch: {} {} {} {} {}'.format(
            switch['name'],
            switch['status'],
            switch['ip_address'],
            switch['role'],
            switch['switch_class']))
        
        if switch['role'] == defines.SWITCH_ROLE_LEAF:
            leaf_switches.append(switch)

    for leaf in leaf_switches:
        print('Leaf switch: {}'.format(leaf['name']))

    # ports = ports_module.get_ports(afc_host, token, switches=[switch['uuid']])
    # print('Ports for switch {}'.format(switch['name']))
    # for port in ports:
    #     print('Port = {}'.format(pprint.pformat(port, indent=4)))

    # provisioned_lags = lags_module.get_lags(afc_host, token, lag_type=defines.LAG_TYPE_PROVISIONED)
    # for lag in provisioned_lags:
    #     print('Provisioned LAG = {}'.format(pprint.pformat(lag, indent=4)))

    internal_lags = lags_module.get_lags(afc_host, token, lag_type=defines.LAG_TYPE_INTERNAL)
    # for lag in internal_lags:
    #     print('Internal LAG = {}'.format(pprint.pformat(lag, indent=4)))
        
    # cookie_jar = switch_login(switch)
    # time.sleep(2)
    # get_switch_classes(switch, cookie_jar)
    # get_switch_policies(switch, cookie_jar)
    # switch_logout(switch, cookie_jar)

    # q = policies_module.create_qualifier(afc_host, token, 'my-qualifier11', vlans='100')
#     p = policies_module.create_qos_policy(afc_host, token, 'my-policy11', 5, 5, [q])


if __name__ == '__main__':
    main(sys.argv)
