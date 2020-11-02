import sys
import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.switches as switches_module
import afc_tools.aruba.policies as aruba_policies
import afc_tools.aruba.aruba_utils as aruba_module


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    switches = switches_module.get_switches(afc_host, token)
    fabrics = switches_module.get_fabrics(afc_host, token)
    switches_module.display(fabrics, switches)

    for switch in sorted(switches, key=lambda s: s['name']):
        cookie_jar = aruba_module.switch_login(switch)
        aruba_policies.display_all(switch, cookie_jar)
        aruba_module.switch_logout(switch, cookie_jar)
