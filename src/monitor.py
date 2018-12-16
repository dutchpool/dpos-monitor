import sys
import json
import argparse
from distutils.version import StrictVersion
from ping import ping_servers
from printing import __print
from status import check_status, check_lisk_status
from telegram import __send_telegram_message, set_telegram_conf

__author__ = 'dutch_pool'
__version__ = '1.1.0'

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
    results = []
    if "adamant_main_hosts" in conf:
        results.append(
            {"environment": "Adamant main", "messages": check_nodes("adamant_main", conf["adamant_main_hosts"])})
    if "blockpool_main_hosts" in conf:
        results.append({"environment": "Blockpool main", "messages": check_nodes("blockpool_main", conf["blockpool_main_hosts"])})
    if "kapu_main_hosts" in conf:
        results.append({"environment": "Kapu main", "messages": check_nodes("kapu_main", conf["kapu_main_hosts"])})
    if "lisk_main_hosts" in conf:
        results.append({"environment": "Lisk main", "messages": check_nodes("lisk_main", conf["lisk_main_hosts"])})
    if "lisk_test_hosts" in conf:
        results.append({"environment": "Lisk test", "messages": check_nodes("lisk_test", conf["lisk_test_hosts"])})
    if "lwf_main_hosts" in conf:
        results.append({"environment": "Lwf main", "messages": check_nodes("lwf_main", conf["lwf_main_hosts"])})
    if "lwf_test_hosts" in conf:
        results.append({"environment": "Lwf test", "messages": check_nodes("lwf_test", conf["lwf_test_hosts"])})
    if "onz_main_hosts" in conf:
        results.append({"environment": "Onz main", "messages": check_nodes("onz_main", conf["onz_main_hosts"])})
    if "onz_test_hosts" in conf:
        results.append({"environment": "Onz test", "messages": check_nodes("onz_test", conf["onz_test_hosts"])})
    if "oxy_main_hosts" in conf:
        results.append({"environment": "Oxy main", "messages": check_nodes("oxy_main", conf["oxy_main_hosts"])})
    if "oxy_test_hosts" in conf:
        results.append({"environment": "Oxy test", "messages": check_nodes("oxy_test", conf["oxy_test_hosts"])})
    if "qredit_main_hosts" in conf:
        results.append({"environment": "Qredit main", "messages": check_nodes("qredit_main", conf["qredit_main_hosts"])})
    if "ripa_main_hosts" in conf:
        results.append({"environment": "Ripa main", "messages": check_nodes("ripa_main", conf["ripa_main_hosts"])})
    if "rise_main_hosts" in conf:
        results.append({"environment": "Rise main", "messages": check_nodes("rise_main", conf["rise_main_hosts"])})
    if "rise_test_hosts" in conf:
        results.append({"environment": "Rise test", "messages": check_nodes("rise_test", conf["rise_test_hosts"])})
    if "sauco_main_hosts" in conf:
        results.append({"environment": "Sauco main", "messages": check_nodes("sauco_main", conf["sauco_main_hosts"])})
    if "shift_main_hosts" in conf:
        results.append({"environment": "Shift main", "messages": check_nodes("shift_main", conf["shift_main_hosts"])})
    if "shift_test_hosts" in conf:
        results.append({"environment": "Shift test", "messages": check_nodes("shift_test", conf["shift_test_hosts"])})
    if "swapblocks_test_hosts" in conf:
        results.append({"environment": "Swapblocks test",
                        "messages": check_nodes("swapblocks_test", conf["swapblocks_test_hosts"])})
    if "swapblocks_main_hosts" in conf:
        results.append({"environment": "Swapblocks main",
                        "messages": check_nodes("swapblocks_main", conf["swapblocks_main_hosts"])})

    complete_message = ""
    for result in results:
        if len(result["messages"]) > 0:
            complete_message += "***" + result["environment"] + "***\n"
            for message in result["messages"]:
                complete_message += message + "\n"
    if complete_message is not "":
        __send_telegram_message(complete_message)
    print(complete_message)


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
        if environment.startswith("lisk"):
            status_result = check_lisk_status(environment_conf, nodes_to_monitor, conf)
            processed_status_results = check_lisk_status_nodes(status_result)
        elif conf["check_block_height"] or conf["check_version"]:
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
                processed_ping_results.append(host["name"] + ":\nCould not reach the server, it might be down!\n")
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

    consensus = get_consensus_messages(status_result, max_block_height, version)

    # total_nodes = len(status_result["base_hosts"]) + len(status_result["peer_nodes"]) + len(
    # status_result["nodes_to_monitor"])
    for host in status_result["nodes_to_monitor"]:
        try:
            if conf["check_block_height"]:
                # Block height
                block_height_message = check_block_height(host, max_block_height, consensus["block_height_consensus"],
                                                          consensus["total_nodes"])
                if block_height_message is not None:
                    monitored_nodes_messages.append(block_height_message)

            if conf["check_version"]:
                # Version
                version_message = check_version(host, version, consensus["version_consensus"], consensus["total_nodes"])
                if version_message is not None:
                    monitored_nodes_messages.append(version_message)
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    return monitored_nodes_messages


def get_max_block_height_and_version(status_result):
    try:
        max_block_height = 0
        version = "0.0.0"
        for host in status_result["base_hosts"]:
            if conf["check_block_height"] and host.block_height > max_block_height:
                max_block_height = host.block_height
            if conf["check_version"] and StrictVersion(host.version) > StrictVersion(version):
                version = host.version
            for peer in host.peers:
                if "height" in peer:
                    if conf["check_block_height"] and peer["height"] > max_block_height:
                        max_block_height = peer["height"]
                if "version" in peer:
                    try:
                        if conf["check_version"] and StrictVersion(peer["version"]) > StrictVersion(version):
                            version = peer["version"]
                    except Exception as exception:
                        print(exception)
        for host in status_result["peer_nodes"]:
            if conf["check_block_height"] and host.block_height > max_block_height:
                max_block_height = host.block_height
            if conf["check_version"] and StrictVersion(host.version) > StrictVersion(version):
                version = host.version
            for peer in host.peers:
                if "height" in peer:
                    if conf["check_block_height"] and peer["height"] > max_block_height:
                        max_block_height = peer["height"]
                if "version" in peer:
                    try:
                        if conf["check_version"] and StrictVersion(peer["version"]) > StrictVersion(version):
                            version = peer["version"]
                    except Exception as exception:
                        print(exception)
        for host in status_result["nodes_to_monitor"]:
            if conf["check_block_height"] and host.block_height > max_block_height:
                max_block_height = host.block_height
            if conf["check_version"] and StrictVersion(host.version) > StrictVersion(version):
                version = host.version
            for peer in host.peers:
                if "height" in peer:
                    if conf["check_block_height"] and peer["height"] > max_block_height:
                        max_block_height = peer["height"]
                if "version" in peer:
                    try:
                        if conf["check_version"] and StrictVersion(peer["version"]) > StrictVersion(version):
                            version = peer["version"]
                    except Exception as exception:
                        print(exception)
        return {"max_block_height": max_block_height, "version": version}
    except Exception as e:
        __print('Unable to get max block height and version')
        print(e)
        return {"max_block_height": 0, "version": "0.0.0"}


def get_consensus_messages(status_result, max_block_height, version):
    block_height_consensus = 0
    version_consensus = 0
    total_nodes = 0
    for host in status_result["base_hosts"]:
        total_nodes += 1
        try:
            if host.block_height == max_block_height:
                block_height_consensus += 1

            if host.version == version:
                version_consensus += 1
            for peer in host.peers:
                total_nodes += 1
                if "height" in peer:
                    if max_block_height >= peer["height"] >= max_block_height - 2:
                        block_height_consensus += 1
                if "version" in peer:
                    if peer["version"] == version:
                        version_consensus += 1
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    for host in status_result["peer_nodes"]:
        total_nodes += 1
        try:
            if host.block_height == max_block_height:
                block_height_consensus += 1

            if host.version == version:
                version_consensus += 1
            for peer in host.peers:
                total_nodes += 1
                if "height" in peer:
                    if max_block_height >= peer["height"] >= max_block_height - 2:
                        block_height_consensus += 1
                if "version" in peer:
                    if peer["version"] == version:
                        version_consensus += 1
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    for host in status_result["nodes_to_monitor"]:
        total_nodes += 1
        try:
            if host.block_height == max_block_height:
                block_height_consensus += 1

            if host.version == version:
                version_consensus += 1
            for peer in host.peers:
                total_nodes += 1
                if "height" in peer:
                    if max_block_height >= peer["height"] >= max_block_height - 2:
                        block_height_consensus += 1
                if "version" in peer:
                    if peer["version"] == version:
                        version_consensus += 1
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    return {"block_height_consensus": block_height_consensus,
            "version_consensus": version_consensus, "total_nodes": total_nodes}


def check_block_height(host, max_block_height, block_height_consensus, total_nodes):
    if host.block_height == 0:
        return host.name + ":\nCould not reach the server, it might be down!\n"
    elif host.block_height == 403:
        return host.name + ":\nNode api access denied. Is the monitoring server ip whitelisted in the node's config?\n"
    elif host.block_height == 500:
        return host.name + ":\nNo (valid) response from the server, it might be down!\n"
    elif host.block_height < max_block_height - conf["max_blocks_behind"]:
        consensus_percentage = int((block_height_consensus / total_nodes * 100) * 100) / 100
        block_height_difference = max_block_height - host.block_height
        line1 = host.name
        line2 = ":\nincorrect block height " + str(host.block_height) + " (-" + str(block_height_difference) + ")"
        line3 = "\nshould be " + str(max_block_height)
        line4 = "\nconsensus " + str(consensus_percentage) + "% " + str(block_height_consensus) + "/" + str(
            total_nodes) + "\n"

        return line1 + line2 + line3 + line4
    return None


def check_version(host, version, version_consensus, total_nodes):
    if host.version == "0.0.0":
        return host.name + ":\nCould not reach the server, it might be down!\n"
    elif host.version == "403":
        return host.name + ":\nNode api access denied. Is the monitoring server ip whitelisted in the node's config?\n"
    elif host.version == "500":
        return host.name + ":\nNo (valid) response from the server, it might be down!\n"
    elif StrictVersion(host.version) < StrictVersion(version) and version is not "403" and version is not "500":
        consensus_percentage = int((version_consensus / total_nodes * 100) * 100) / 100
        line1 = host.name
        line2 = ":\nincorrect version " + host.version
        line3 = "\nshould be " + version
        line4 = "\nconsensus " + str(consensus_percentage) + "% " + str(version_consensus) + "/" + str(
            total_nodes) + "\n"

        return line1 + line2 + line3 + line4
    return None


def check_lisk_status_nodes(status_result):
    max_block_height_and_version = get_lisk_max_block_height(status_result)
    # processed_status_results = []
    max_block_height = max_block_height_and_version["max_block_height"]
    version = max_block_height_and_version["version"]
    monitored_nodes_messages = []

    consensus = get_consensus_messages(status_result, max_block_height, version)

    # total_nodes = len(status_result["base_hosts"]) + len(status_result["peer_nodes"]) + len(
    # status_result["nodes_to_monitor"])
    for host in status_result["nodes_to_monitor"]:
        try:
            if conf["check_block_height"]:
                # Block height
                block_height_message = check_block_height(host, max_block_height, consensus["block_height_consensus"],
                                                          consensus["total_nodes"])
                if block_height_message is not None:
                    monitored_nodes_messages.append(block_height_message)
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    return monitored_nodes_messages


def get_lisk_max_block_height(status_result):
    try:
        max_block_height = 0
        version = "0.0.0"
        for host in status_result["base_hosts"]:
            if conf["check_block_height"] and host.block_height > max_block_height:
                max_block_height = host.block_height
            for peer in host.peers:
                if "height" in peer:
                    if conf["check_block_height"] and peer["height"] > max_block_height:
                        max_block_height = peer["height"]
        for host in status_result["peer_nodes"]:
            if conf["check_block_height"] and host.block_height > max_block_height:
                max_block_height = host.block_height
            for peer in host.peers:
                if "height" in peer:
                    if conf["check_block_height"] and peer["height"] > max_block_height:
                        max_block_height = peer["height"]
        for host in status_result["nodes_to_monitor"]:
            if conf["check_block_height"] and host.block_height > max_block_height:
                max_block_height = host.block_height
            for peer in host.peers:
                if "height" in peer:
                    if conf["check_block_height"] and peer["height"] > max_block_height:
                        max_block_height = peer["height"]
        return {"max_block_height": max_block_height, "version": version}
    except Exception as e:
        __print('Unable to get max block height and version')
        print(e)
        return {"max_block_height": 0, "version": "0.0.0"}


def get_lisk_consensus_messages(status_result, max_block_height):
    block_height_consensus = 0
    total_nodes = 0
    for host in status_result["base_hosts"]:
        total_nodes += 1
        try:
            if host.block_height == max_block_height:
                block_height_consensus += 1
            for peer in host.peers:
                total_nodes += 1
                if "height" in peer:
                    if max_block_height >= peer["height"] >= max_block_height - 2:
                        block_height_consensus += 1
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    for host in status_result["peer_nodes"]:
        total_nodes += 1
        try:
            if host.block_height == max_block_height:
                block_height_consensus += 1
            for peer in host.peers:
                total_nodes += 1
                if "height" in peer:
                    if max_block_height >= peer["height"] >= max_block_height - 2:
                        block_height_consensus += 1
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    for host in status_result["nodes_to_monitor"]:
        total_nodes += 1
        try:
            if host.block_height == max_block_height:
                block_height_consensus += 1
            for peer in host.peers:
                total_nodes += 1
                if "height" in peer:
                    if max_block_height >= peer["height"] >= max_block_height - 2:
                        block_height_consensus += 1
        except Exception as e:
            __print('Unable to get block height and version messages')
            print(e)
    return {"block_height_consensus": block_height_consensus,
            "version_consensus": total_nodes, "total_nodes": total_nodes}


def check_lisk_block_height(host, max_block_height, block_height_consensus, total_nodes):
    if host.block_height == 0:
        return host.name + ":\nCould not reach the server, it might be down!\n"
    elif host.block_height == 403:
        return host.name + ":\nNode api access denied. Is the monitoring server ip whitelisted in the node's config?\n"
    elif host.block_height == 500:
        return host.name + ":\nNo (valid) response from the server, it might be down!\n"
    elif host.block_height < max_block_height - conf["max_blocks_behind"]:
        consensus_percentage = int((block_height_consensus / total_nodes * 100) * 100) / 100
        block_height_difference = max_block_height - host.block_height
        line1 = host.name
        line2 = ":\nincorrect block height " + str(host.block_height) + " (-" + str(block_height_difference) + ")"
        line3 = "\nshould be " + str(max_block_height)
        line4 = "\nconsensus " + str(consensus_percentage) + "% " + str(block_height_consensus) + "/" + str(
            total_nodes) + "\n"

        return line1 + line2 + line3 + line4
    return None


try:
    conf = json.load(open(args.cfile, 'r'))
    set_telegram_conf(conf["telegram_settings"])
    check_all_nodes()
except Exception as ex:
    __print('Unable to load config file.')
    print(ex)
    sys.exit()