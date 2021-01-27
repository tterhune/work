import pprint
import requests
import urllib3

import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_mac_attachments(switch, cookie_jar):
    url = 'https://{}/rest/v10.04/system/vlans/*/macs'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    macs = r.json()
    return macs if macs else {}


def display(switch, macs):
    if not macs:
        print('No MAC addresses found for switch {}'.format(switch['name']))
        return

    # This is a nested dict, gross.
    header = ['MAC Address', 'VLAN', 'Interface', 'Type', 'Switch']
    table = []
    for vlan, vlan_macs in macs.items():
        for type_mac_tuple, mac_dict in vlan_macs.items():
            intf_dict = mac_dict['port']
            if intf_dict:
                intf_name = list(intf_dict.keys())[0]
            else:
                intf_name = 'unknown'
            row = [mac_dict['mac_addr'], vlan, intf_name, mac_dict['from'], switch['name']]
            table.append(row)

    print(tabulate.tabulate(table, header, tablefmt='grid'))
