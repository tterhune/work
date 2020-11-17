import collections
import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.switches as switches_module
import afc_tools.afc.lags as lags_module
import afc_tools.afc.ports as ports_module
import afc_tools.shared.defines as defines

import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    switches = switches_module.get_switches(afc_host, token)
    fabrics = switches_module.get_fabrics(afc_host, token)
    switches_module.display(afc_host, fabrics, switches)

    switch_map = {s['uuid']: s for s in switches}

    headers = ['Switch Name', 'LAG name', 'Type', 'MLAG', 'UUID', 'Ports']
    lags = lags_module.get_lags(afc_host, token, defines.LAG_TYPE_PROVISIONED)
    lag_table = []

    # lag_display = collections.defaultdict(list)
    for lag in lags:
        for port_info in lag['port_properties']:
            switch_uuid = port_info['switch_uuid']
            port_uuids = port_info['port_uuids']
            ports = []
            for port_uuid in port_uuids:
                port = ports_module.get_port(afc_host, token, port_uuid)
                ports.append(port)

            port_names = [p['name'] for p in ports]
            port_names = '\n'.join(port_names)

            switch_name = switch_map[switch_uuid]['name']

            lag_info = [switch_name,
                        lag['name'],
                        lag['type'],
                        lag['mlag'],
                        lag['uuid'],
                        port_names]
            lag_table.append(lag_info)

    print(tabulate.tabulate(lag_table, headers=headers))
