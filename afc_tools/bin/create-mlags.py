#!/usr/bin/env python

import pprint
import sys
import time
import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.lags as lags_module
import afc_tools.afc.policy as policies_module
import afc_tools.afc.ports as ports_module
import afc_tools.afc.switches as switch_module
import afc_tools.aruba.policies as aruba_policies
import afc_tools.aruba.aruba_utils as aruba_module
import afc_tools.shared.defines as defines

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _get_port(afc_host, token, switch):
    ports = ports_module.get_ports(afc_host, token, switches=[switch['uuid']])
    port = None
    for port in ports:
        if (port['type'] == 'access' and port['admin_state'] == 'disabled'
                and not port['qos_ingress_policies']):
            print('Port = {}'.format(pprint.pformat(port, indent=4)))
            break

    return port


def _create_mlag(afc_host, token, switches, port_uuids=None):
    """Create an MLAG across two switches.

    Args:
        afc_host (str): AFC hostname
        token (str): AFC token
        switches (list): list of AFC switch objects

    Returns:
        tuple (dict, list[tuple]): AFC LAG dict, and tuple of port, switch
    """
    leaf_switches = list()
    for switch in switches:
        if switch['role'] == defines.SWITCH_ROLE_LEAF and switch['status'] == 'SYNCED':
            leaf_switches.append(switch)

    if len(leaf_switches) < 2:
        print('Need two leaf switches that are in sync, only found: {}'.format(leaf_switches))
        return

    # Pick two ports on two different switches
    lag_ports = []
    for switch in leaf_switches:
        port = _get_port(afc_host, token, switch)
        if port_uuids:
            if port['uuid'] not in port_uuids:
                lag_ports.append((port, switch))
        else:
            lag_ports.append((port, switch))

    for lag_port in lag_ports:
        print('Using port: {} on switch: {}'.format(lag_port[0]['name'], lag_port[1]['name']))

    # Create MLAG
    port_uuids = [lp[0]['uuid'] for lp in lag_ports]
    mlag_uuid = lags_module.create_lag(afc_host, token, port_uuids)

    mlag = lags_module.get_lag(afc_host, token, mlag_uuid)
    return mlag, lag_ports


def main(afc_host):
    token = afc_module.get_token(afc_host)

    # Display some info
    switches = switch_module.get_switches(afc_host, token)
    fabrics = switch_module.get_fabrics(afc_host, token)
    switch_module.display(afc_host, fabrics, switches)

    time.sleep(1)

    # Create an MLAG
    mlag, lag_ports = lags_module.create_mlag(afc_host, token, switches)
    print('MLAG: {}'.format(mlag['name']))

    port_uuids = []
    for p, s in lag_ports:
        print('\tPorts:')
        print('\tPort: {} Switch: {}', p, s)
        port_uuids.append(p['uuid'])

    # mlag2, lag_ports2 = lags_module.create_mlag(afc_host, token, switches, port_uuids)
    # print('MLAG2: {}'.format(mlag2['name']))

    # mlag = lags_module.get_lag(afc_host, token, mlag1['uuid'])
    print('\nMLAG {}\n'.format(pprint.pformat(mlag, indent=4)))

    # Display switch info
    #for switch in switches:
    #    cookie_jar = aruba_module.switch_login(switch)
    #    aruba_module.switch_logout(switch, cookie_jar)

    #for switch in switches:
    #    cookie_jar = aruba_module.switch_login(switch)
    #    aruba_module.switch_logout(switch, cookie_jar)

    time.sleep(2)
    print('Deleting MLAG: {}'.format(mlag['uuid']))
    lags_module.delete_lags(afc_host, token, [mlag['uuid']])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
