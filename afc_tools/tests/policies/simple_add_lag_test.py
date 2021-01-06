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


def _get_port(afc_host, token, switch, existing_port_uuids):
    ports = ports_module.get_ports(afc_host, token, switches=[switch['uuid']])
    port = None
    print('existing = {}'.format(existing_port_uuids))

    for port in ports:
        if (port['type'] == 'access' and (not port['qos_ingress_policies']) and
                (port['uuid'] not in existing_port_uuids)):
            print('Port = {}/{}'.format(port, port['uuid']))
            break

    print('FOUND PORT {}'.format(port))
    return port


def _create_lag(afc_host, token, switches):
    lag = {}
    lag_ports = []
    leaf_switch = None

    for switch in switches:
        if switch['role'] == defines.SWITCH_ROLE_LEAF and switch['status'] == 'SYNCED':
            leaf_switch = switch
            break

    if not leaf_switch:
        print('Need leaf switch that is in SYNC, but none found')
        return lag, lag_ports

    # Pick two ports on two different switches
    port_uuids = []
    for _ in range(0,2):
        port = _get_port(afc_host, token, leaf_switch, port_uuids)
        lag_ports.append(port)
        port_uuids.append(port['uuid'])

    for lag_port in lag_ports:
        print('Using port: {} on switch: {}'.format(lag_port['name'], leaf_switch['name']))

    port_uuids = [lp['uuid'] for lp in lag_ports]

    print('Creating LAG on switch {}'.format(leaf_switch['name']))

    lag_uuid = lags_module.create_lag(afc_host, token, port_uuids, mlag=False)

    print('Done creating LAG on switch {}'.format(leaf_switch['name']))

    lag = lags_module.get_lag(afc_host, token, lag_uuid)
    return lag, lag_ports


def main(afc_host):
    token = afc_module.get_token(afc_host)

    # Get LAGs
    lags = lags_module.get_lags(afc_host, token, lag_type=defines.LAG_TYPE_PROVISIONED)

    lags_module.display_lags(afc_host, token, lags)

    for lag in lags:
        print('Deleting LAG: {}'.format(lag['name']))
        lags_module.delete_lags(afc_host, token, [lag['uuid']])

    # Display some info
    switches = switch_module.get_switches(afc_host, token)
    fabrics = switch_module.get_fabrics(afc_host, token)
    switch_module.display(afc_host, fabrics, switches)

    time.sleep(1)

    # Create an LAG
    print('Creating LAG')
    lag, lag_ports = _create_lag(afc_host, token, switches)

    print('Created LAG: {}'.format(lag['name']))

    lag = lags_module.get_lag(afc_host, token, lag['uuid'])

    lags_module.display_lags(afc_host, token, [lag])

    print('Deleting LAG: {}'.format(lag['name']))
    lags_module.delete_lags(afc_host, token, [lag['uuid']])


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
