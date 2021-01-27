#!/usr/bin/env python

import pprint
import sys
import time
import urllib3

import afc_tools.shared.defines as defines
import afc_tools.afc.afc_utils as afc_module
import afc_tools.afc.lags as lags_module
import afc_tools.afc.switches as switch_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main(afc_host):
    token = afc_module.get_token(afc_host)

    # Display some info
    switches = switch_module.get_switches(afc_host, token)
    fabrics = switch_module.get_fabrics(afc_host, token)
    switch_module.display(afc_host, fabrics, switches)

    lags = lags_module.get_lags(afc_host, token, lag_type=defines.LAG_TYPE_PROVISIONED)
    lags_module.display_lags(afc_host, token, lags)

    time.sleep(1)

    lag_uuids = [l['uuid'] for l in lags]
    print('Deleting LAG UUIDs: {}'.format(lag_uuids))

    lags_module.delete_lags(afc_host, token, lag_uuids)

    lags = lags_module.get_lags(afc_host, token, lag_type=defines.LAG_TYPE_PROVISIONED)
    lags_module.display_lags(afc_host, token, lags)

    time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
