import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.policy as policies_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)
    policies_module.cleanup_policies(afc_host, token)
    policies_module.cleanup_qualifiers(afc_host, token)
