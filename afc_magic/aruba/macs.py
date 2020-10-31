import pprint
import requests
import urllib3

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


def display(macs):
    # This is a nested dict, gross.
    total = 0
    if macs:
        print('{0: ^20}  {1}  {2: ^10}  {3: ^7}'.format('MAC Address',
                                                        'VLAN',
                                                        'Interface',
                                                        'Type'))
        print('{}  {}  {}  {}'.format('-' * 20, '-' * 4, '-' * 10, '-' * 7))
        for vlan, vlan_macs in macs.items():
            for type_mac_tuple, mac_dict in vlan_macs.items():
                total += 1
                intf_dict = mac_dict['port']
                if intf_dict:
                    intf_name = list(intf_dict.keys())[0]
                else:
                    intf_name = 'unknown'

                print('{0: ^20}  {1: ^4}  {2: ^10}  {3: ^7}'.format(mac_dict['mac_addr'],
                                                                    vlan,
                                                                    intf_name,
                                                                    mac_dict['from']))
    print('\nTotal MAC addresses: {}'.format(total))
