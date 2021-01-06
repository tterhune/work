import pprint
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_writable_intf(switch, cookie_jar, intf_name):
    intf_name = intf_name.replace('/', '%2F')
    url = 'https://{}/rest/v10.04/system/interfaces/{}'.format(switch['ip_address'], intf_name)

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'selector': 'writable',
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    intf = r.json()

    # print('Got interfaces: {} from switch: {}'.format(pprint.pformat(intfs, indent=4),
    #                                                   switch['name']))
    return intf


def get_interfaces(switch, cookie_jar):
    url = 'https://{}/rest/v10.04/system/interfaces'.format(switch['ip_address'])

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    params = {
        'depth': 2,
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    intfs = r.json()
    
    # print('Got interfaces: {} from switch: {}'.format(pprint.pformat(intfs, indent=4),
    #                                                   switch['name']))
    return intfs if intfs else {}


def get_queue_stats(cookie_jar, switch, intf_name):
    # curl -X GET "https://10.101.36.192/rest/v10.04/system/interfaces/1%2F1%2F1?attributes=queue_tx_bytes,queue_tx_errors,queue_tx_maxdepth,queue_tx_packets" -H  "accept: application/json"
    url = 'https://{}/rest/v10.04/system/interfaces/{}'.format(switch['ip_address'], intf_name)

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    queues = ['queue_tx_bytes',
              'queue_tx_errors',
              'queue_tx_maxdepth',
              'queue_tx_packets']

    queue_names = ', '.join(queues)

    params = {
        'attributes': queue_names,
        'depth': 2
    }

    r = requests.get(url, headers=headers, params=params, cookies=cookie_jar, verify=False)
    r.raise_for_status()

    intf_queue_stats = r.json()

    print('Got queue stats: {} from switch: {}'.format(pprint.pformat(
        intf_queue_stats,
        indent=4),
        switch['name']))


def display(switches, cookie_jar):
    for switch in switches:
        print('\nInterfaces for switch {} ({}):'.format(switch['name'], switch['ip_address']))

        print('{0: <12} {1}'.format('uu:', '=> no policies configured'))

