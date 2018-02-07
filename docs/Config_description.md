# Config.json information

```
{
  "check_ping": true,
  "check_block_height": true,
  "check_version": false,
  "max_blocks_behind": 10,
  ...
}

```

* port
    * The port on which the node software communicates. Normally 8000 for Lisk and 10000 for Oxy (non ssl).
* check_ping
    * If the hosts should be pinged to check if they are reachable.
* check_block_height
    * If the block height of the hosts should be checked against the block height of the core nodes.
* check_version
    * If the version of your node should be checked against the version of the core nodes.
* max_blocks_behind
    * The max number of blocks you accept your node to be behind the current block height

```
 "lisk_main_hosts": [],
  "lisk_test_hosts": [],
  "lwf_main_hosts": [],
  "lwf_test_hosts": [],
  "onz_test_hosts": [],
  "oxy_main_hosts": [
    {
      "name": "oxy_node_1",
      "host": "1.2.3.4",
      "port": 10000,
      "can_ping": true
    },
    {
      "name": "oxy_node_2",
      "host": "2.3.4.5",
      "port": 10000,
      "can_ping": false
    }
  ],
  "oxy_test_hosts": [],
  "shift_main_hosts": [],
  "shift_test_hosts": []
```
* Each platform can contain a list of hosts to monitor
* hosts
    * The hosts to ping / check their block height / check their version.
        * name
            * The name of the host, used in telegram messages and the monitoring dashboard.
        * host
            * The ip or hostname (without http) where the host can be reached. There is no https support yet.
        * port
            * The port necessary to reaching the api
        * ping
            * If the node can be pinged, for example azure has disabled ICMP (ICMP is necessary for pinging).
    
## Telegram configuration
This part of the configuration is to configure telegram to send messages in case something is not right with the node.

```
  "telegram_settings": {
    "use_telegram": false,
    "bot_key": "",
    "chat_id": ""
  }
```

* use_telegram
    * If Telegram should be used to send messages in case something is wrong.
* bot_key
    * The token received from the BotFather when registering a telegram bot.
* chat_id
    * The chat id of the Telegram chat where the messages from the Telegram bot should be delivered.