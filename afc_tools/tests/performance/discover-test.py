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
import time
import urllib3

import afc_tools.afc.afc_utils as afc_module
import afc_tools.shared.defines as defines
import afc_tools.afc.switches as switch_module
import afc_tools.afc.ports as ports_module

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_ports(afc_host, token, ports):
    count = 0
    for port in ports:
        ports_module.get_port(afc_host, token, port['uuid'])
        count += 1
    print('\tPorts: got {} of them'.format(count))


def get_switches(afc_host, token, switches):
    count = 0
    for switch in switches:
        switch_module.get_switch(afc_host, token, switch['uuid'])
        count += 1
    print('\tSwitches : got {} of them'.format(count))


def get_all(afc_host, token):
    green_pool = eventlet.GreenPool()

    switches = switch_module.get_switches(afc_host, token)
    ports = ports_module.get_ports(afc_host, token)

    for i in range(0, 1000):
        print('\tGetting switches and ports Round {}'.format(i))
        pile = eventlet.GreenPile(green_pool)
        pile.spawn(get_switches, afc_host, token, switches)
        pile.spawn(get_ports, afc_host, token, ports)
        for r in pile:
            pass
        print('\tGetting switches and ports done Round {}'.format(i))
        time.sleep(1)


def setup_teardown(afc_host, token, fabric_name, switch_prefix):
    print('Creating fabric: {}'.format(fabric_name))
    fabric = switch_module.create_fabric(afc_host, token, fabric_name)

    print('Discovering switches: {}'.format(switch_prefix))
    switch_module.do_discovery(afc_host, token, fabric['uuid'], switch_prefix)

    sleep_time = 2
    print('{} Sleeping for {} minutes {}'.format('-' * 20, sleep_time, '-' * 20 ))
    time.sleep(sleep_time)

    switches = switch_module.get_switches(afc_host, token)
    for switch in switches:
        if switch['status'] != 'SYNCED':
            print('Deleting switch {} not in SYNC, but is instead: {} status'.format(
                switch['name'],
                switch['status']))

        print('Deleting switch: {}'.format(switch['name']))
        switch_module.delete_switch(afc_host, token, switch['uuid'])

    print('Deleting fabric: {}'.format(fabric['name']))
    switch_module.delete_fabric(afc_host, token, fabric['uuid'])


def main(afc_host, fabric_name, switch_prefix):
    token = afc_module.get_token(afc_host)

    fabrics = switch_module.get_fabrics(afc_host, token)
    switches = switch_module.get_switches(afc_host, token)
    if switches:
        print('Found some switches, cleaning up')
        for switch in switches:
            print('Deleting switch: {}'.format(switch['name']))
            switch_module.delete_switch(afc_host, token, switch['uuid'])

    if fabrics:
        print('Found some fabrics, cleaning up')
        for fabric in fabrics:
            print('Deleting switch: {}'.format(fabric['name']))
            switch_module.delete_switch(afc_host, token, fabric['uuid'])

    eventlet.spawn(get_all, afc_host, token)

    for i in range(0, 100):
        print('Round {}'.format(i))
        setup_teardown(afc_host, token, fabric_name, switch_prefix)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('WARNING: Usage: {} [<AFC host>] <fabric-name> <switch>'.format(sys.argv[0]))
        sys.exit(1)
    elif len(sys.argv) == 3:
        print('WARNING: Usage: {} [<AFC host>] <fabric-name> <switch>'.format(sys.argv[0]))
        my_afc_host = 'localhost'
        my_fabric_name = sys.argv[1]
        my_switch_prefix = sys.argv[2]
    else:
        my_afc_host = sys.argv[1]
        my_fabric_name = sys.argv[2]
        my_switch_prefix = sys.argv[3]

    main(my_afc_host, my_fabric_name, my_switch_prefix)
