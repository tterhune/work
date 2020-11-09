import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.switches as switches_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    switches = switches_module.get_switches(afc_host, token)
    fabrics = switches_module.get_fabrics(afc_host, token)
    switches_module.display(afc_host, fabrics, switches)
