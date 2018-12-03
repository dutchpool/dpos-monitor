import os
from src.printing import __print


__author__ = 'dutch_pool'


def ping_servers(hosts):
    ping_monitor_data = []
    for host in hosts:
        if host["can_ping"]:
            ping_monitor_data.append(ping(host))
    return ping_monitor_data


def ping(host):
    try:
        response = os.system("ping -c 5 " + host["host"])

        if response == 0:
            return {"name": host["name"], "up": True}
        else:
            __print(host["host"] + ' is down!')
            return {"name": host["name"], "up": False}
    except Exception as e:
        __print('Unable to ping server ' + host["host"])
        print(e)