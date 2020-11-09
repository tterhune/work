import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.macs as macs_module
import afc_tools.afc.switches as switches_module
import afc_tools.aruba.macs as aruba_macs
import afc_tools.aruba.aruba_utils as aruba_module


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    switches = switches_module.get_switches(afc_host, token)
    fabrics = switches_module.get_fabrics(afc_host, token)
    switches_module.display(afc_host, fabrics, switches)

    for switch in sorted(switches, key=lambda s: s['name']):
        cookie_jar = aruba_module.switch_login(switch)
        print('\nSwitch: {} ({})'.format(switch['name'], switch['ip_address']))
        macs = aruba_macs.get_mac_attachments(switch, cookie_jar)
        aruba_macs.display(macs)
        macs = macs_module.get_macs(afc_host, token, switch_uuids=[switch['uuid']], interfaces=True)
        macs_module.display(macs)

        aruba_module.switch_logout(switch, cookie_jar)
