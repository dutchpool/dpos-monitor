from src.console.printing import __print
from src.telegram.telegram import __send_telegram_message
import requests

__author__ = 'dutch_pool'


class Host(object):
    def __init__(self, name, host, block_height, version):
        self.name = name
        self.host = host
        self.block_height = block_height
        self.version = version


def check_block_height(config):
    block_height = get_block_height()
    block_height_monitor_data = [{"name": "core", "height": block_height}]
    for host in config["hosts"]:
        try:
            uri = "http://" + host["host"] + ":" + str(config["port"]) + "/api/blocks/getHeight"
            response = requests.get(uri)
            if response.status_code == 200:
                json_response = response.json()
                if json_response["success"]:
                    if json_response["height"] < block_height - config["max_blocks_behind"] \
                            or json_response["height"] > block_height + config["max_blocks_ahead"]:
                        __print("Block height incorrect, " + host["name"])
                        __send_telegram_message(
                            host["name"] + '_' + host["host"] + ", incorrect blockheight, is " + str(
                                json_response["height"]) + " should be " + str(block_height)
                        )
                    elif json_response["height"] > block_height:
                        block_height = json_response["height"]
                    block_height_monitor_data.append(
                        {"name": host["name"], "height": json_response["height"], "status_code": 200})
            elif response.status_code == 403:
                __print("403 code block height, " + host["name"])
                block_height_monitor_data.append({"name": host["name"], "height": 0, "status_code": 403})
                # do something
            else:
                __print("Could not load block height, " + host["name"])
                __send_telegram_message(
                    host["name"] + '_' + host["host"] + ", could not get block height, node could be down"
                )
                block_height_monitor_data.append({"name": host["name"], "height": 0, "status_code": 500})
        except Exception as e:
            __print('Unable to check block height ' + host["host"])
            print(e)

    return block_height_monitor_data


def get_base_hosts_status(hosts, conf):
    base_hosts = []
    for host in hosts:
        try:
            block_height = 0
            version = ""
            if conf["check_block_height"]:
                block_height = get_block_height(host)
            if conf["check_version"]:
                version = get_version(host)
            base_hosts.append(Host(host["name"], host["host"], block_height, version))
        except Exception as e:
            __print('Unable to check base host status ' + host["host"])
            print(e)
    return base_hosts


def get_peer_nodes_status(peers, conf):
    peer_nodes = []
    index = 0
    for peer in peers:
        try:
            block_height = 0
            version = ""
            if index >= 3:
                return peer_nodes
            host = {"name": peer["name"], "host": "http://" + str(peer["ip"]) + ":" + str(peer["port"])}
            if conf["check_block_height"]:
                block_height = get_block_height(host)
            if conf["check_version"]:
                version = get_version(host)
            peer_nodes.append(Host(host["name"], host["host"], block_height, version))
            index += 1
        except Exception as e:
            __print('Unable to check peer nodes status ' + peer["name"])
            print(e)
    return peer_nodes


def get_nodes_to_monitor_status(nodes, conf):
    nodes_to_monitor = []
    for node in nodes:
        try:
            block_height = 0
            version = ""
            host = {"name": node["name"], "host": "http://" + str(node["host"]) + ":" + str(node["port"])}
            if conf["check_block_height"]:
                block_height = get_block_height(host)
            if conf["check_version"]:
                version = get_version(host)
            nodes_to_monitor.append(Host(host["name"], host["host"], block_height, version))
        except Exception as e:
            __print('Unable to check nodes to monitor status ' + node["name"])
            print(e)
    return nodes_to_monitor


def get_block_height(host):
    try:
        uri = host["host"] + "/api/blocks/getHeight"
        response = requests.get(uri)
        if response.status_code == 200:
            json_response = response.json()
            if json_response["success"]:
                return json_response["height"]
        elif response.status_code == 403:
            __print("403 block height, " + host["name"])
            return 403
        else:
            __print("500 block height, " + host["name"])
            return 500
    except Exception as e:
        __print('Unable to get block height ' + host["host"])
        print(e)
        return 0


def get_version(host):
    try:
        uri = host["host"] + "/api/peers/version"
        response = requests.get(uri)
        if response.status_code == 200:
            json_response = response.json()
            if json_response["success"]:
                return json_response["version"]
        elif response.status_code == 403:
            __print("403 version, " + host["name"])
            return "403"
        else:
            __print("500 version, " + host["name"])
            return "500"
    except Exception as e:
        __print('Unable to get version ' + host["host"])
        print(e)
        return ""


def check_status(environment_conf, nodes_to_monitor, conf):
    try:
        status_list = {}
        base_hosts = environment_conf["base_hosts"]
        peer_nodes = environment_conf["peer_nodes"]
        status_list["base_hosts"] = get_base_hosts_status(base_hosts, conf)
        status_list["peer_nodes"] = get_peer_nodes_status(peer_nodes, conf)
        status_list["nodes_to_monitor"] = get_nodes_to_monitor_status(nodes_to_monitor, conf)
        return status_list
    except Exception as e:
        __print('Unable to check_status')
        print(e)
        return []

