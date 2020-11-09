import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.neighbors as neighbors_module
import afc_tools.afc.switches as switches_module
import afc_tools.aruba.neighbors as aruba_neighbors
import afc_tools.aruba.aruba_utils as aruba_module


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    switches = switches_module.get_switches(afc_host, token)
    fabrics = switches_module.get_fabrics(afc_host, token)
    switches_module.display(afc_host, fabrics, switches)

    for switch in sorted(switches, key=lambda s: s['name']):
        cookie_jar = aruba_module.switch_login(switch)

        print('\nSwitch {} ({}):\n'.format(switch['name'], switch['ip_address']))
        lldp, cdp = aruba_neighbors.get_neighbors(switch, cookie_jar)
        aruba_neighbors.display(lldp, cdp)
        neighbors = neighbors_module.get_neighbors(afc_host, token, switch_uuids=[switch['uuid']])
        neighbors_module.display(afc_host, token, neighbors)

        aruba_module.switch_logout(switch, cookie_jar)
