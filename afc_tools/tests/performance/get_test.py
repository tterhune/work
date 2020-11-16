#!/usr/bin/env python

import eventlet
eventlet.monkey_patch(os=True,
                      select=True,
                      socket=True,
                      thread=True,
                      psycopg=True,
                      time=True)

requests = eventlet.import_patched('requests.__init__')
import sys
import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.shared.defines as defines
import afc_tools.afc.switches as switch_module
import afc_tools.afc.ports as ports_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_ports(afc_host, token):
    green_pool = eventlet.GreenPool()
    port_pile = eventlet.GreenPile(green_pool)
    for i in range(0, 20):
        port_pile.spawn(ports_module.get_ports, afc_host, token)

    for r in port_pile:
        pass


def get_vsx_count(afc_host, token, fabric_uuid):
    path = 'fabrics/{}/vsx'.format(fabric_uuid)
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    params = dict(count_only=True)
    url = defines.vURL.format(host=afc_host, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()


def get_leaf_spine_count(afc_host, token, fabric_uuid):
    path = 'fabrics/{}/leaf_spine'.format(fabric_uuid)
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    params = dict(count_only=True)
    url = defines.vURL.format(host=afc_host, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()


def get_evpn_count(afc_host, token, fabric_uuid):
    path = 'evpn'
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    params = dict(fabric_uuid=fabric_uuid, count_only=True)
    url = defines.vURL.format(host=afc_host, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()


def get_switch(afc_host, token):
    path = 'switches'
    headers = {
        'accept': 'application/json',
        'Authorization': token,
        'Content-Type': 'application/json'
    }

    params = dict(tags=True, unassigned=True)
    url = defines.vURL.format(host=afc_host, path=path, version='v1')
    r = requests.get(url, headers=headers, params=params, verify=False)
    r.raise_for_status()


def get_all(afc_host, token, fabric_uuid):
    green_pool = eventlet.GreenPool()
    pile = eventlet.GreenPile(green_pool)
    pile.spawn(get_switch, afc_host, token)
    pile.spawn(get_evpn_count, afc_host, token, fabric_uuid)
    pile.spawn(get_vsx_count, afc_host, token, fabric_uuid)
    pile.spawn(get_leaf_spine_count, afc_host, token, fabric_uuid)

    for r in pile:
        pass


def main(afc_host):
    token = afc_module.get_token(afc_host)

    fabrics = switch_module.get_fabrics(afc_host, token)
    print('fabrics = {}'.format(fabrics))
    fabric_uuid = fabrics[0]['uuid']

    for i in range(0, 100):
        print('Round {}'.format(i))
        gt1 = eventlet.spawn(get_all, afc_host, token, fabric_uuid)
        gt1.wait()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>], default is \'localhost\''.format(sys.argv[0]))
        my_afc_host = 'localhost'
    else:
        my_afc_host = sys.argv[1]

    main(my_afc_host)
