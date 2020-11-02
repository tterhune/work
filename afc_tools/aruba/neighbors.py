import pprint
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LLDP_URI = 'system/interfaces/{}/lldp_neighbors'
CDP_URI = 'system/interfaces/{}/cdp_neighbors'


def get_neighbors(switch, cookie_jar, interface='*'):
    url = 'https://{}/rest/v10.04/{}'.format(switch['ip_address'], LLDP_URI.format(interface))

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()
    lldp = r.json()

    url = 'https://{}/rest/v10.04/{}'.format(switch['ip_address'], CDP_URI.format(interface))
    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()
    cdp = r.json()

    return lldp, cdp


def display(lldp_neighbors, cdp_neighbors):
    # This is a nested dict, gross.
    total = 0
    print('Aruba Neighbors')
    print('---------------\n')
    for intf, lldp in lldp_neighbors.items():
        intf = intf.replace('%2F', '/')
        # print('{} => {}'.format(intf, pprint.pformat(lldp, indent=4)))
        for mac_and_chassis, lldp_info in lldp.items():
            print('Type               : {}'.format(
                lldp_info['neighbor_info'].get('chassis_protocol', 'NONE')))
            print('Learned on Intf    : {}'.format(intf))
            print('Port ID            : {}'.format(lldp_info['port_id']))
            print('Chassis ID         : {}'.format(lldp_info['chassis_id']))
            print('MAC Address        : {}'.format(lldp_info['mac_addr']))
            print('Chassis Description: {}'.format(
                lldp_info['neighbor_info'].get('chassis_description', 'NONE')))
            print('Chassis Name       : {}'.format(
                lldp_info['neighbor_info'].get('chassis_name', 'NONE')))
            print('Mgmt IP            : {}'.format(
                lldp_info['neighbor_info'].get('mgmt_ip_list', 'NONE')))
            print('Port Description   : {}\n'.format(
                lldp_info['neighbor_info'].get('port_description', 'NONE')))
            total += 1
    print('Total LLDP: {}'.format(total))

    total = 0
    for key, cdp in cdp_neighbors.items():
        print('{} => {}'.format(key, pprint.pformat(cdp, indent=4)))
        total += 1
    print('Total CDP : {}\n'.format(total))
