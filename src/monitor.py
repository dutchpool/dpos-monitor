import sys
import json
import argparse

from printing import __print
from status import check_status
from ping import ping_servers
from telegram import set_telegram_conf, __send_telegram_message


__author__ = 'dutch_pool'
__version__ = '0.9.0'

if sys.version_info[0] < 3:
    print('python2 not supported, please use python3')
    sys.exit(0)

# Parse command line args
parser = argparse.ArgumentParser(description='DPOS delegate monitor script')
parser.add_argument('-c', metavar='config.json', dest='cfile', action='store',
                    default='config.json',
                    help='set a config file (default: config.json)')
args = parser.parse_args()


def check_all_nodes():
    results = [{"environment": "Lisk main", "messages": check_nodes("lisk_main", conf["lisk_main_hosts"])},
               {"environment": "Lisk test", "messages": check_nodes("lisk_test", conf["lisk_test_hosts"])},
               {"environment": "Lwf main", "messages": check_nodes("lwf_main", conf["lwf_main_hosts"])},
               {"environment": "Lwf test", "messages": check_nodes("lwf_test", conf["lwf_test_hosts"])},
               {"environment": "Onz test", "messages": check_nodes("oxy_test", conf["oxy_test_hosts"])},
               {"environment": "Oxy main", "messages": check_nodes("oxy_main", conf["oxy_main_hosts"])},
               {"environment": "Oxy test", "messages": check_nodes("oxy_test", conf["oxy_test_hosts"])},
               {"environment": "Shift main", "messages": check_nodes("shift_main", conf["shift_main_hosts"])},
               {"environment": "Shift test", "messages": check_nodes("shift_test", conf["shift_test_hosts"])}]

    complete_message = ""
    for result in results:
        if len(result["messages"]) > 0:
            complete_message += result["environment"] + "\n"
            for message in result["messages"]:
                complete_message += message + "\n"
    if complete_message is not "":
        __send_telegram_message(complete_message)


def check_nodes(environment, nodes_to_monitor):
    if len(nodes_to_monitor) == 0:
        return []
    try:
        environment_conf = json.load(open("default_configs/env_" + environment + ".json", 'r'))
        processed_ping_results = []
        processed_status_results = []
        if conf["check_ping"]:
            ping_result = ping_servers(nodes_to_monitor)
            processed_ping_results = process_ping_data(ping_result)
        if conf["check_block_height"] or conf["check_version"]:
            status_result = check_status(environment_conf, nodes_to_monitor, conf)
            processed_status_results = check_status_nodes(status_result)
        messages = []
        messages.extend(processed_ping_results)
        messages.extend(processed_status_results)
        return messages
    except Exception as e:
        __print('Unable to check nodes.')
        print(e)


def process_ping_data(ping_result):
    processed_ping_results = []
    try:
        for host in ping_result:
            if not host["up"]:
                processed_ping_results.append(host["name"] + ", server seems to be down!")
    except Exception as e:
        __print('Could nog process ping results.')
        print(e)
    return processed_ping_results


def check_status_nodes(status_result):
    max_block_height_and_version = get_max_block_height_and_version(status_result)
    # processed_status_results = []
    max_block_height = max_block_height_and_version["max_block_height"]
    version = max_block_height_and_version["version"]
    monitored_nodes_messages = []
    for host in status_result["nodes_to_monitor"]:
        try:
            if conf["check_block_height"]:
                # Block height
                block_height_message = check_block_height(host, max_block_height)
                if block_height_message is not None:
                    monitored_nodes_messages.append(block_height_message)

            if conf["check_version"]:
                # Version
                version_message = check_version(host, version)
                if version_message is not None:
                    monitored_nodes_messages.append(version_message)
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    if len(monitored_nodes_messages) > 0:
        monitored_nodes_messages.extend(get_messages_per_node(status_result))
    return monitored_nodes_messages


def get_max_block_height_and_version(status_result):
    try:
        max_block_height = 0
        version = ""
        for host in status_result["base_hosts"]:
            if host.block_height > max_block_height:
                max_block_height = host.block_height
            if host.version > version:
                version = host.version
        for host in status_result["peer_nodes"]:
            if host.block_height > max_block_height:
                max_block_height = host.block_height
            if host.version > version:
                version = host.version
        for host in status_result["nodes_to_monitor"]:
            if host.block_height > max_block_height:
                max_block_height = host.block_height
            if host.version > version:
                version = host.version
        return {"max_block_height": max_block_height, "version": version}
    except Exception as e:
        __print('Unable to get max block height and version')
        print(e)
        return {"max_block_height": 0, "version": ""}


def check_block_height(host, max_block_height):
    if host.block_height == 0:
        return host.name + '_' + host.host + ", could not get the block height, make sure the node can be reached."
    elif host.block_height == 403:
        return host.name + '_' + host.host + ", no access to get the block height. Add the ip of the monitoring server to the config"
    elif host.block_height == 500:
        return host.name + '_' + host.host + ", no (valid) response getting the block height. Server could be down."
    elif host.block_height < max_block_height - conf["max_blocks_behind"]:
        return host.name + '_' + host.host + ", incorrect block height, is " + str(
            host.block_height) + "should be " + str(max_block_height)
    return None


def check_version(host, version):
    if host.version == "":
        return host.name + '_' + host.host + ", could not get the version, make sure the node can be reached."
    elif host.version == "403":
        return host.name + '_' + host.host + ", no access to get the version. Add the ip of the monitoring server to the config."
    elif host.version == "500":
        return host.name + '_' + host.host + ", no (valid) response getting the version. Server could be down."
    elif host.version < version:
        return host.name + '_' + host.host + ", incorrect version, is " + host.version + "should be " + version
    return None


def get_messages_per_node(status_result):
    messages = []
    for host in status_result["base_hosts"]:
        messages.append(
            host.name + '_' + host.host + ", block height = " + str(host.block_height) + ", version = " + host.version)
    for host in status_result["peer_nodes"]:
        messages.append(
            host.name + '_' + host.host + ", block height = " + str(host.block_height) + ", version = " + host.version)
    for host in status_result["nodes_to_monitor"]:
        messages.append(
            host.name + '_' + host.host + ", block height = " + str(host.block_height) + ", version = " + host.version)
    return messages


try:
    conf = json.load(open(args.cfile, 'r'))
    set_telegram_conf(conf["telegram_settings"])
    check_all_nodes()
except Exception as ex:
    __print('Unable to load config file.')
    print(ex)
    sys.exit()