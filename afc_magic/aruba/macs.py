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
    
    print('Got macs: {} from switch: {}'.format(pprint.pformat(macs, indent=4), switch['name']))
    return macs if macs else {}


def display(switches, cookie_jar):
    for switch in switches:
        print('\nMAC Attachments for switch {} ({}):'.format(switch['name'], switch['ip_address']))

        macs = get_mac_attachments(switch, cookie_jar=cookie_jar)

        print('{0: <12} {1}'.format('Policies:', '=> no policies configured'))

